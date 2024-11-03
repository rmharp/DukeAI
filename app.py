import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import datetime
import os
import logging

logging.basicConfig(level=logging.DEBUG)

# Initialize Firebase only if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = credentials.Certificate('dukeai-103f8-369df2b50aa4.json')
    firebase_admin.initialize_app(cred)

    # Add custom CSS styling
st.markdown("""
    <style>
    /* Style the title */
    .title {
        font-size: 30px;
        color: #4A90E2;
        font-weight: bold;
        margin-top: 20px;
    }

    /* Style for buttons */
    .stButton > button {
        background-color: #56c1ca;
        color: white;
        font-size: 16px;
        margin: 10px 0;
        padding: 8px 16px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #132c5e;
    }

    /* Style text inputs */
    input[type="text"], input[type="password"] {
        padding: 8px;
        width: 100%;
        font-size: 16px;
        margin: 10px 0;
        border-radius: 5px;
    }

    /* Placeholder container styling */
    .stContainer {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

def app():
    # Initialize session state variables
    if 'db' not in st.session_state:
        st.session_state.db = ''
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'signout' not in st.session_state:
        st.session_state.signout = False

    # Create a placeholder for the main content
    main_placeholder = st.empty()

    # Main app logic within the placeholder
    with main_placeholder.container():
        if st.session_state.current_page == 'login':
            login_page()
        elif st.session_state.current_page == 'role_selection':
            role_selection_page()
        elif st.session_state.current_page == 'participant_profile':
            participant_profile_setup_page()
        elif st.session_state.current_page == 'researcher_profile':
            researcher_profile_setup_page()
        elif st.session_state.current_page == 'collect_study_information':
            collect_study_information()
        elif st.session_state.current_page == 'clinicaltrialdata':
            clinicaltrialdata()
        else:
            st.error('Unknown page')

def login_page():
    
    image_path = os.path.join('media', 'clinical_consent_pfp.png')
    st.image(image_path, use_column_width=True)

    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'], key='login_choice')

    if choice == 'Login':
        st.text_input('Email Address', key='login_email')
        st.text_input('Password', type='password', key='login_password')

        # Define the login function to be called on button click
        def login():
            try:
                email = st.session_state.login_email
                password = st.session_state.login_password

                # Authenticate user (Note: Replace this with proper password verification)
                user = auth.get_user_by_email(email)
                if user:
                    # Assuming authentication is successful
                    st.session_state.useremail = user.email
                    st.session_state.username = user.uid
                    st.session_state.signout = True
                    st.session_state.db = firestore.client()
                    st.session_state.logged_in = True
                    
                    # Initialize registered and researcher flags
                    st.session_state.registered = False
                    st.session_state.researcher = False

                    # Check if the user is registered
                    db = st.session_state.db
                    if not db:
                        st.error('Database connection not established.')
                        return

                    # Check in participants collection
                    participants_ref = db.collection('participants')
                    participants_query = participants_ref.where('uid', '==', st.session_state.username).get()
                    if participants_query:
                        # User is a participant
                        st.session_state.registered = True
                        st.session_state.researcher = False
                    else:
                        # Check in researchers collection
                        researchers_ref = db.collection('researchers')
                        researchers_query = researchers_ref.where('uid', '==', st.session_state.username).get()
                        if researchers_query:
                            # User is a researcher
                            st.session_state.registered = True
                            st.session_state.researcher = True
                        else:
                            # User not registered in either collection
                            st.session_state.registered = False
                            st.session_state.researcher = False

                    # Now, based on the flags, set the current page
                    if st.session_state.logged_in and not st.session_state.registered:
                        st.session_state.current_page = 'role_selection'
                    elif st.session_state.logged_in and st.session_state.registered and st.session_state.researcher:
                        st.session_state.current_page = 'collect_study_information'
                    elif st.session_state.logged_in and st.session_state.registered and not st.session_state.researcher:
                        st.session_state.current_page = 'clinicaltrialdata'
                    else:
                        st.error('Unknown state. Please contact support.')

                    # Force a rerun by updating a dummy session state variable
                    st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.warning(f'Login failed, please try again. Error: {e}')

        # Attach the login function to the button's on_click event
        st.button('Login', key='login_button', on_click=login)
    else:
        st.text_input('Email Address', key='signup_email')
        st.text_input('Password', type='password', key='signup_password')
        st.text_input('Enter your unique username', key='signup_username')

        # Define the account creation function
        def create_account():
            try:
                email = st.session_state.signup_email
                password = st.session_state.signup_password
                username = st.session_state.signup_username
                user = auth.create_user(email=email, password=password, uid=username)
                st.success('Account created successfully!')
                st.markdown('Please login using your email and password')
                st.balloons()
            except Exception as e:
                st.error(f'Error creating account: {e}')

        # Attach the account creation function to the button
        st.button('Create my account', key='signup_button', on_click=create_account)

def role_selection_page():
    st.markdown(
        '<h1><span style="color: #56c1ca;">C</span>linical <span style="color: #56c1ca;">C</span>onsent</h1>',
        unsafe_allow_html=True
    )

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)
    
    st.title("Select your position:")
    
    if st.button('Participant'):
        st.write("You selected Participant.")
        st.session_state.current_page = 'participant_profile'
        # Force a rerun
        st.session_state['dummy'] = not st.session_state.get('dummy', False)
    elif st.button('Researcher'):
        st.write("You selected Researcher.")
        st.session_state.current_page = 'researcher_profile'
        # Force a rerun
        st.session_state['dummy'] = not st.session_state.get('dummy', False)

def participant_profile_setup_page():
    global registered
    st.markdown(
        '<h1><span style="color: #56c1ca;">C</span>linical <span style="color: #56c1ca;">C</span>onsent</h1>',
        unsafe_allow_html=True
    )

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)
    
    st.title("Set up your Profile")

    first_name_participant = st.text_input("First Name", key="first_name_participant")
    last_name_participant = st.text_input("Last Name", key="last_name_participant")
    sexuality_participant = st.selectbox("Sexuality", ["Heterosexual", "Homosexual", "Bisexual", "Other"], key="sexuality_participant")
    age_participant = st.number_input("Age", min_value=0, max_value=120, step=5, key="age_participant")
    sex_participant = st.selectbox("Sex", ["Male", "Female", "Other"], key="sex_participant")
    state_participant = st.text_input("State", key='state_participant')
    city_participant = st.text_input("City", key='city_participant')
    address_participant = st.text_input("Address", key='address_participant')
    height_participant = st.number_input("Height (in)", min_value=0.0, max_value=300.0, step=10.0, key="height_participant")
    weight_participant = st.number_input("Weight (lb)", min_value=0.0, max_value=500.0, step=20.0, key="weight_participant")
    previous_surgery_participant = st.text_input("Previous Surgery (if any)", key="previous_surgery_participant")
    mental_disability_participant = st.text_input("Mental Disability (if any)", key="mental_disability_participant")
    physical_disability_participant = st.text_input("Current Physical Disability or Disease (if any)", key="physical_disability_participant")
    previous_records_participant = st.text_area("Previous Records of Disease or Surgery (if any)", key="previous_records_participant")
    pregnancy_participant = st.selectbox("Are you currently pregnant?", ["No", "Yes", "Not applicable"], key="pregnancy_participant")
    breastfeeding_participant = st.selectbox("Are you currently breastfeeding?", ["No", "Yes", "Not applicable"], key="breastfeeding_participant")
    allergy_participant = st.text_input("Allergies (if any)", key="allergy_participant")
    smoking_participant = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"], key="smoking_participant")
    blood_type_participant = st.selectbox("Blood Type", ["A", "B", "AB", "O", "Unknown"], key="blood_type_participant")

    # Define the participant info form submission function
    def submit_form_participant():
        global registered
        # Access all input values from st.session_state
        first_name_participant = st.session_state.first_name_participant
        last_name_participant = st.session_state.last_name_participant
        sexuality_participant = st.session_state.sexuality_participant
        age_participant = st.session_state.age_participant
        sex_participant = st.session_state.sex_participant
        state_participant = st.session_state.state_participant
        city_participant = st.session_state.city_participant
        address_participant = st.session_state.address_participant
        height_participant = st.session_state.height_participant
        weight_participant = st.session_state.weight_participant
        previous_surgery_participant = st.session_state.previous_surgery_participant
        mental_disability_participant = st.session_state.mental_disability_participant
        physical_disability_participant = st.session_state.physical_disability_participant
        previous_records_participant = st.session_state.previous_records_participant
        pregnancy_participant = st.session_state.pregnancy_participant
        breastfeeding_participant = st.session_state.breastfeeding_participant
        allergy_participant = st.session_state.allergy_participant
        smoking_participant = st.session_state.smoking_participant
        blood_type_participant = st.session_state.blood_type_participant
        uid = st.session_state.username

        # Validate inputs to form
        if not first_name_participant or not last_name_participant or not age_participant or not sex_participant or not state_participant or not city_participant or not address_participant or not pregnancy_participant:
            st.error("Please fill out all the required participant details.")
        else:
            try:
                db = st.session_state.db
                # Use 'studies' as the document reference
                participants = db.collection('participants').document()

                # Prepare the data to save
                data = {
                    'first_name_participant': first_name_participant,
                    'last_name_participant': last_name_participant,
                    'sexuality_participant': sexuality_participant,
                    'age_participant': age_participant,
                    'sex_participant': sex_participant,
                    'state_participant': state_participant,
                    'city_participant': city_participant,
                    'address_participant': address_participant,
                    'height_participant': height_participant,
                    'weight_participant': weight_participant,
                    'previous_surgery_participant': previous_surgery_participant,
                    'mental_disability_participant': mental_disability_participant,
                    'physical_disability_participant': physical_disability_participant,
                    'previous_records_participant': previous_records_participant,
                    'pregnancy_participant': pregnancy_participant,
                    'breastfeeding_participant': breastfeeding_participant,
                    'allergy_participant': allergy_participant,
                    'smoking_participant': smoking_participant,
                    'blood_type_participant': blood_type_participant,
                    'timestamp': datetime.datetime.utcnow(),
                    'uid': uid
                }

                # Save the data to Firestore
                participants.set(data)

                st.success("Form submitted successfully!")
                st.session_state.current_page = 'clinicaltrialdata'
                registered = True
                # Force a rerun
                st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")

    # Attach the submit_form function to the button
    st.button("Submit Profile", key="submit_button_participant", on_click=submit_form_participant) 

def researcher_profile_setup_page():
    st.markdown(
        '<h1><span style="color: #56c1ca;">C</span>linical <span style="color: #56c1ca;">C</span>onsent</h1>',
        unsafe_allow_html=True
    )

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)
    
    st.title("Set up your Profile")

    name_researcher = st.text_input("Name", key="name_researcher")
    organization_email_researcher = st.text_input("Organization Email", key="organization_email_researcher")
    position_researcher = st.text_input("Position", key="position_researcher")
    research_keywords_researcher = st.text_area("Research Keywords (comma-separated)", key="research_keywords_researcher")
    phone_number_researcher = st.text_input("Phone Number", key="phone_number_researcher")
    actively_recruiting_researcher = st.text_input("Actively Recruiting?", key="actively_recruiting_researcher")
    
    # Define the researcher info form submission function
    def submit_form_researcher():
        global registered
        # Access all input values from st.session_state
        name_researcher = st.session_state.name_researcher
        organization_email_researcher = st.session_state.organization_email_researcher
        position_researcher = st.session_state.position_researcher
        research_keywords_researcher = st.session_state.research_keywords_researcher
        phone_number_researcher = st.session_state.phone_number_researcher
        actively_recruiting_researcher = st.session_state.actively_recruiting_researcher
        uid = st.session_state.username

        # Validate inputs to form
        if not name_researcher or not organization_email_researcher or not phone_number_researcher or not actively_recruiting_researcher:
            st.error("Please fill out all the required researcher details.")
        else:
            try:
                db = st.session_state.db
                # Use 'studies' as the document reference
                researchers = db.collection('researchers').document()

                # Prepare the data to save
                data = {
                    'name_researcher': name_researcher,
                    'organization_email_researcher': organization_email_researcher,
                    'position_researcher': position_researcher,
                    'research_keywords_researcher': research_keywords_researcher,
                    'phone_number_researcher': phone_number_researcher,
                    'actively_recruiting_researcher': actively_recruiting_researcher,
                    'timestamp': datetime.datetime.utcnow(),
                    'uid': uid
                }

                # Save the data to Firestore
                researchers.set(data)

                st.success("Form submitted successfully!")
                st.session_state.current_page = 'clinicaltrialdata'
                registered = True
                # Force a rerun
                st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")

    # Attach the submit_form function to the button
    st.button("Submit Profile", key="submit_button_researcher", on_click=submit_form_researcher) 

def collect_study_information():
    st.markdown(
        '<h1><span style="color: #56c1ca;">C</span>linical <span style="color: #56c1ca;">C</span>onsent</h1>',
        unsafe_allow_html=True
    )

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)

    st.title("Study Information Collection")

    # Study Details
    st.header("Study Details")
    st.text_input("Study Name", key='study_name')
    st.text_area("Description", key='description')

    # Participant Information
    st.header("Participant Information")
    st.selectbox("Sexuality", ["Heterosexual", "Homosexual", "Bisexual", "Other"], key='sexuality')
    st.number_input("Age", min_value=0, max_value=120, step=5, key='age')
    st.selectbox("Sex", ["Male", "Female", "Other"], key='sex')
    st.text_input("State", key='state')
    st.text_input("City", key='city')
    st.text_input("Address", key='address')
    st.number_input("Height (in)", min_value=0.0, max_value=300.0, step=10.0, key='height')
    st.number_input("Weight (lb)", min_value=0.0, max_value=500.0, step=20.0, key='weight')
    st.text_area("Previous Surgery", key='previous_surgery')
    st.text_area("Mental Disability (list if any)", key='mental_disability')
    st.text_area("Physical Disability (list if any)", key='physical_disability')
    st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key='blood_type')

    # Consent Form Upload
    st.file_uploader("Upload Consent Form (PDF)", type=["pdf"], key='consent_form')

    # Define the form submission function
    def submit_form():
        # Access all input values from st.session_state
        #keys matching
        study_name = st.session_state.study_name
        description = st.session_state.description
        sexuality = st.session_state.sexuality
        age = st.session_state.age
        sex = st.session_state.sex
        state = st.session_state.state
        city = st.session_state.city
        address = st.session_state.address
        height = st.session_state.height
        weight = st.session_state.weight
        previous_surgery = st.session_state.previous_surgery
        mental_disability = st.session_state.mental_disability
        physical_disability = st.session_state.physical_disability
        blood_type = st.session_state.blood_type
        consent_form = st.session_state.consent_form
        uid = st.session_state.username

        # Validate inputs
        if not study_name or not description:
            st.error("Please fill out all the required study details.")
        elif age <= 0:
            st.error("Please fill out all the required participant information.")
        else:
            try:
                db = st.session_state.db
                # Use 'studies' as the document reference
                studies = db.collection('studies').document()

                # Prepare the data to save
                data = {
                    'study_name': study_name,
                    'description': description,
                    'participant': {
                        'sexuality': sexuality,
                        'age': age,
                        'sex': sex,
                        'state': state,
                        'city': city,
                        'address': address,
                        'height_in': height,
                        'weight_lb': weight,
                        'previous_surgery': previous_surgery,
                        'mental_disability': mental_disability,
                        'physical_disability': physical_disability,
                        'blood_type': blood_type,
                    },
                    'timestamp': datetime.datetime.utcnow(),
                    'uid': uid
                }

                # Save the data to Firestore
                studies.set(data)

                st.success("Form submitted successfully!")
                st.session_state.current_page = 'clinicaltrialdata'
                # Force a rerun
                st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")

    # Attach the submit_form function to the button
    st.button("Submit", key="submit_button", on_click=submit_form)

def clinicaltrialdata():
    st.markdown(
        '<h1><span style="color: #56c1ca;">C</span>linical <span style="color: #56c1ca;">C</span>onsent</h1>',
        unsafe_allow_html=True
    )

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)

    st.title("Clinical Trial Data")

    db = st.session_state.db
    if not db:
        st.error('Database connection not established.')
        return

    # Get participant data
    participants_ref = db.collection('participants')
    participant_query = participants_ref.where('uid', '==', st.session_state.username).get()
    if participant_query:
        # Since uid should be unique, we can take the first document
        participant_doc = participant_query[0]
        participant_data = participant_doc.to_dict()

        # Extract necessary fields
        age_participant = participant_data.get('age_participant', '')
        sex_participant = participant_data.get('sex_participant', '').strip().lower()
        city_participant = participant_data.get('city_participant', '')
        state_participant = participant_data.get('state_participant', '')
        mental_disability_participant = participant_data.get('mental_disability_participant', '')
        physical_disability_participant = participant_data.get('physical_disability_participant', '')
    else:
        # Handle the case where no participant is found
        st.error("No participant found with the given UID.")
        return

    # Ensure age is an integer
    try:
        age_participant = int(age_participant)
    except (ValueError, TypeError):
        st.error("Participant's age is not a valid number.")
        return

    # Reference to the 'clinical_trials' collection
    trials_ref = db.collection('clinical_trials')

    # Get all clinical trials
    clinical_trials_query = trials_ref.get()

    matched_trials = []

    for clinical_trial in clinical_trials_query:
        d = clinical_trial.to_dict()

        # Initialize match to True
        is_match = True
        
        testing = False
        if testing:

            # Location matching
            trial_city = d.get('locationCity', '')
            trial_state = d.get('locationState', '')

            if trial_city != '' and trial_state != '':
                # For simplicity, we'll assume if city and state match, it's within 20 miles
                if trial_city.strip().lower() != city_participant.strip().lower() or trial_state.strip().lower() != state_participant.strip().lower():
                    is_match = False
            elif trial_state != '':
                if trial_state.strip().lower() != state_participant.strip().lower():
                    is_match = False
            # If both locationCity and locationState are unspecified, treat as unrestrictive
        
        # Sex matching
        trial_sex = d.get('sex', 'All')
        if trial_sex not in [None, '', 'All', 'ALL', all]:
            if trial_sex.strip().lower() != sex_participant.strip().lower():
                is_match = False
        
        # Age matching
        min_age = d.get('minAge')
        max_age = d.get('maxAge')

        #print(age_participant)
        #print(min_age)
        #print(max_age)
        
        # If minAge is specified, check that participant is older or equal
        if min_age not in [None, '']:
            try:
                min_age = int(min_age)
                if age_participant < min_age:
                    is_match = False
            except (ValueError, TypeError):
                pass  # Ignore invalid minAge

        # If maxAge is specified, check that participant is younger or equal
        if max_age not in [None, '']:
            try:
                max_age = int(max_age)
                if age_participant > max_age:
                    is_match = False
            except (ValueError, TypeError):
                pass  # Ignore invalid maxAge
        
        # Healthy Volunteers matching
        healthy_volunteers = d.get('healthyVolunteers')
        if healthy_volunteers not in [None, '']:
            # Convert to boolean
            if isinstance(healthy_volunteers, str):
                healthy_volunteers = healthy_volunteers.lower() == 'true'
            has_disabilities = (
                (mental_disability_participant.strip().lower() != 'none' and mental_disability_participant.strip() != '') or
                (physical_disability_participant.strip().lower() != 'none' and physical_disability_participant.strip() != '')
            )
            if healthy_volunteers:
                if has_disabilities:
                    is_match = False
        
        
        
        # After all checks, if is_match is True, add trial to matched_trials
        if is_match:
            matched_trials.append(d)

    # Now display the matched trials
    if matched_trials:
        for d in matched_trials:
            try:
                # Retrieve data without default values
                nct_id = d.get('nctId', '')
                status_verified_date = d.get('statusVerifiedDate', '')
                brief_title = d.get('title', 'No Title')
                description = d.get('openai_summary', '')

                # Prepare left and right content only if data exists
                left_content = f"<strong>NCT ID:</strong> {nct_id}" if nct_id else ''
                right_content = f"<strong>Status Verified Date:</strong> {status_verified_date}" if status_verified_date else ''

                # Display the top line with alignment
                if left_content or right_content:
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; width: 100%;">
                            <div style="text-align: left;">{left_content}</div>
                            <div style="text-align: right;">{right_content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(f"<h2>{brief_title}</h2>", unsafe_allow_html=True)
                if description:
                    st.write(description)
                else:
                    st.write("Description not available.")
                user_query = st.text_input("Do you have any questions?", key=f"ask_{nct_id}")

                # You can later process the user_query as needed
                if user_query:
                    print(f"User query for {nct_id}: {user_query}")

                # Add a horizontal line to separate entries
                st.markdown("<hr>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.write("No matched clinical trials found.")

# Do you have any questions?

def sign_out():
    st.session_state.signout = False
    st.session_state.username = ''
    st.session_state.useremail = ''
    st.session_state.current_page = 'login'
    # Force a rerun
    st.session_state['dummy'] = not st.session_state.get('dummy', False)

app()