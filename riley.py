import requests
import firebase_admin
import openai
import os
from firebase_admin import credentials, firestore
from tqdm import tqdm
from dotenv import load_dotenv
import time

# Load environment variables from a .env file
load_dotenv()

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('dukeai-103f8-369df2b50aa4.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def fetch_clinical_trials(max_studies=None, batch_size=1000):
    url = "https://clinicaltrials.gov/api/v2/studies"
    page_token = None
    studies = []

    headers = {
        "Accept": "application/json"
    }

    # Set total_batches to 1 for testing
    total_batches = 1

    # Fetch the studies with a progress bar
    with tqdm(total=max_studies, desc="Fetching Clinical Trials") as pbar:
        while len(studies) < max_studies:
            params = {
                "filter.overallStatus": "RECRUITING",
                "countTotal": "true",
                "pageToken": page_token,
                "format": "json",
                "markupFormat": "markdown",
                "pageSize": batch_size  # Limit studies per API call
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print("Response content:", response.text)
                break

            try:
                data = response.json()
            except ValueError:
                print("Failed to decode JSON. Response was:", response.text)
                break

            fetched_studies = data.get("studies", [])
            if not fetched_studies:
                break

            for study in fetched_studies:
                if len(studies) >= max_studies:
                    break

                document_section = study.get("documentSection", {}).get("largeDocumentModule", {})
                design_info = study["protocolSection"]["designModule"].get("designInfo", {})
                responsible_party = study["protocolSection"]["sponsorCollaboratorsModule"].get("responsibleParty", {})
                enrollment_info = study["protocolSection"]["designModule"].get("enrollmentInfo", {})
                contacts_locations = study["protocolSection"].get("contactsLocationsModule", {})
                central_contacts = contacts_locations.get("centralContacts", [{}])[0]
                locations = contacts_locations.get("locations", [{}])[0]

                study_info = {
                    "nctId": study["protocolSection"]["identificationModule"].get("nctId"),
                    "title": study["protocolSection"]["identificationModule"].get("officialTitle"),
                    "studyType": study["protocolSection"]["designModule"].get("studyType"),
                    "investigator": responsible_party.get("investigatorFullName", "N/A"),
                    "sponsorName": study["protocolSection"]["sponsorCollaboratorsModule"]["leadSponsor"].get("name"),
                    "organization": study["protocolSection"]["identificationModule"]["organization"].get("fullName"),
                    "overallStatus": study["protocolSection"]["statusModule"]["overallStatus"],
                    "briefSummary": study["protocolSection"]["descriptionModule"].get("briefSummary"),
                    "description": study["protocolSection"]["descriptionModule"].get("detailedDescription"),
                    "conditions": study["protocolSection"]["conditionsModule"].get("conditions"),
                    "keywords": study["protocolSection"]["conditionsModule"].get("keywords"),
                    "purpose": design_info.get("primaryPurpose"),
                    "phase": study["protocolSection"]["designModule"].get("phases"),
                    "interventionalModel": design_info.get("interventionModel"),
                    "observationalModel": design_info.get("observationalModel"),
                    "timePerspective": design_info.get("timePerspective"),
                    "enrollmentCount": enrollment_info.get("count", "N/A"),
                    "enrollmentType": enrollment_info.get("type", "N/A"),
                    "targetDuration": study["protocolSection"]["designModule"].get("targetDuration"),
                    "eligibilityCriteria": study["protocolSection"]["eligibilityModule"].get("eligibilityCriteria"),
                    "sex": study["protocolSection"]["eligibilityModule"].get("sex"),
                    "minAge": study["protocolSection"]["eligibilityModule"].get("minimumAge"),
                    "maxAge": study["protocolSection"]["eligibilityModule"].get("maximumAge"),
                    "healthyVolunteers": study["protocolSection"]["eligibilityModule"].get("healthyVolunteers"),
                    "centralContactName": central_contacts.get("name", "N/A"),
                    "centralContactPhone": central_contacts.get("phone", "N/A"),
                    "centralContactEmail": central_contacts.get("email", "N/A"),
                    "locationFacility": locations.get("facility", "N/A"),
                    "locationCity": locations.get("city", "N/A"),
                    "locationState": locations.get("state", "N/A"),
                    "locationZip": locations.get("zip", "N/A"),
                    "locationCountry": locations.get("country", "N/A"),
                    "hasProtocol": any(doc.get("hasProtocol") for doc in document_section.get("largeDocs", [])),
                    "hasSAP": any(doc.get("hasSap") for doc in document_section.get("largeDocs", [])),
                    "hasICF": any(doc.get("hasIcf") for doc in document_section.get("largeDocs", [])),
                    "fileName": [doc.get("filename") for doc in document_section.get("largeDocs", [])]
                }
                studies.append(study_info)
                pbar.update(1)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    return studies

def openai_prompting(firestore_data, model_choice="gpt-4o", limit=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Limit the number of documents processed if a limit is provided
    if limit:
        firestore_data = firestore_data[:limit]

    results = []
    for doc in tqdm(firestore_data, desc="Generating summaries"):
        # Ensure keywords is a list
        keywords = doc.get('keywords', [])
        if not isinstance(keywords, list):
            keywords = [keywords]

        # Replace None values with 'N/A'
        keywords = [kw if kw is not None else 'N/A' for kw in keywords]

        study_info = {
            "keywords": keywords,
            "briefSummary": doc.get('briefSummary', 'N/A'),
            "description": doc.get('description', 'N/A')
        }

        # Prepare the system content with the specified prompt
        system_content = (
            "You are a 9th-grade teacher tasked with explaining the background, purpose, methodologies, "
            "and potential risks of specific clinical trials to a 9th grader. "
            "Your job is to create a summary and generate hashtags based on provided clinical trial information.\n\n"
            "Ensure the response follows this strict format:\n"
            "1. A single line of hashtags derived from 'keywords', using no more than six keywords.\n"
            "The line must start with 'Hashtag:' and separate each keyword by a comma without a # prefix.\n"
            "2. A one- to two-paragraph summary that:\n"
            "   - Must start with 'Summary:' and continue with a one to two-paragraph explanation.\n"
            "   - Must be more than 7 sentences.\n"
            "   - Provides relevant background using the keywords in one sentence.\n"
            "   - Clearly describes what participants will experience and the purpose of the trial.\n"
            "   - Uses simple language suitable for a 9th grader.\n"
            "   - State specific potential risks that participants may take during the trial.\n"
            "   - Starts with the label called 'Summary'.\n\n"
            "Do not add any titles or extra explanations outside of the requested format.\n"
            "Ensure there are no double newline characters in the response. Each section should be separated by a single newline character.\n\n"
            "Ensure uniformity by maintaining the structure exactly as requested for each response:\n"
            "   'Hashtag: keyword1, keyword2, keyword3, ...'\n"
            "   'Summary: [Summary text]'\n"
            "Maintain clarity in your response."
        )

        # Prepare the assistant content using extracted trial information
        assistant_content = (
            "Here is the clinical trial information:\n"
            "- **Keywords**: " + ", ".join(study_info['keywords']) + "\n"
            "- **Brief Summary**: " + (study_info['briefSummary'] or 'N/A') + "\n"
            "- **Description**: " + (study_info['description'] or 'N/A') + "\n"
            "\nPlease provide a summary and hashtags based on the above information."
        )

        data = {
            "model": model_choice,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "assistant",
                    "content": assistant_content
                },
                {
                    "role": "user",
                    "content": "Please provide the requested explanation and hashtags."
                }
            ],
            "max_tokens": 500
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            output = response.json()['choices'][0]['message']['content']
            results.append(output.strip())
        else:
            print(f"Error: {response.status_code} - {response.text}")
            results.append(None)

    return results

def get_existing_document_ids(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    document_ids = [doc.id for doc in docs]
    return document_ids

def store_to_existing_firestore_batch(fetched_data, results, batch_size=10):
    total_batches = (len(fetched_data) + batch_size - 1) // batch_size

    for i in range(total_batches):
        batch = db.batch()
        batch_start = i * batch_size
        batch_end = batch_start + batch_size
        batch_fetched_data = fetched_data[batch_start:batch_end]
        batch_results = results[batch_start:batch_end]

        for doc, response in tqdm(zip(batch_fetched_data, batch_results), desc=f"Processing batch {i + 1}/{total_batches}", total=len(batch_fetched_data)):
            doc_id = doc.get('nctId')  # Use 'nctId' as the document ID
            if response:
                hashtags_list = []
                summary_line = ""
                
                lines = response.split('\n')
                for line in lines:
                    if line.startswith('Hashtag:'):
                        hashtags_list = line.replace('Hashtag:', '').strip().split(', ')
                    elif line.startswith('Summary:'):
                        summary_line = line.replace('Summary:', '').strip()

                doc_ref = db.collection("clinical_trials_final").document(doc_id)
                # Update the study data with the OpenAI outputs
                doc.update({
                    "openai_hashtags": hashtags_list,
                    "openai_summary": summary_line
                })
                # Add the update to the batch
                batch.set(doc_ref, doc)
            else:
                print(f"Failed to parse response for document ID: {doc_id}")

        # Commit the batch
        batch.commit()
        print(f"Batch {i + 1}/{total_batches} update completed.")

def main():
    # Fetch clinical trials data
    results = fetch_clinical_trials(batch_size=1000)
    
    # Generate summaries and hashtags using OpenAI API
    openai_results = openai_prompting(results)

    # Store the updated data to Firestore in batches
    store_to_existing_firestore_batch(results, openai_results, batch_size=10)

    print("Data stored in Firestore successfully.")

if __name__ == "__main__":
    main()