import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import datetime

# Initialize Firebase only if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = credentials.Certificate('dukeai-103f8-369df2b50aa4.json')
    firebase_admin.initialize_app(cred)

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
    st.title(':blue[T]rial :blue[T]alk')

    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'], key='login_choice')

    if choice == 'Login':
        st.text_input('Email Address', key='login_email')
        st.text_input('Password', type='password', key='login_password')

        # Define the login function to be called on button click
        def login():
            try:
                email = st.session_state.login_email
                password = st.session_state.login_password

                # Authenticate user (Note: This should be replaced with proper authentication)
                user = auth.get_user_by_email(email)
                if user:
                    # Assuming authentication is successful
                    st.session_state.useremail = user.email
                    st.session_state.username = user.uid
                    st.session_state.signout = True
                    st.session_state.current_page = 'researcher_profile'
                    st.session_state.db = firestore.client()

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
    st.title(':blue[T]rial :blue[T]alk')

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)
    
    st.title("Select your position:")
    
    if st.button('Participant'):
        st.write("You selected Participant.")
        st.session_state.show_role_selection = False
        st.session_state.show_participant_profile = True  # Show participant profile setup
    elif st.button('Researcher'):
        st.write("You selected Researcher.")
        st.session_state.show_role_selection = False
        st.session_state.show_researcher_profile = True # Show researcher profile setup
        

def participant_profile_setup_page():
    st.title(':blue[T]rial :blue[T]alk')

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)
    
    st.title("Set up your Profile")

    first_name_participant = st.text_input("First Name", key="first_name_participant")
    last_name_participant = st.text_input("Last Name", key="last_name_participant")
    sexuality_participant = st.selectbox("Sexuality", ["Heterosexual", "Homosexual", "Bisexual", "Other"], key="sexuality_participant")
    age_participant = st.number_input("Age", min_value=0.0, key="age_participant")
    sex_participant = st.selectbox("Sex", ["Male", "Female", "Other"], key="sex_participant")
    state_participant = st.text_input("State", key='state_participant')
    city_participant = st.text_input("City", key='city_participant')
    address_participant = st.text_input("Address", key='address_participant')
    
    height_participant = st.number_input("Height (in cm)", min_value=0.0, key="height_participant")
    weight_participant = st.number_input("Weight (in kg)", min_value=0.0, key="weight_participant")
    previous_surgery_participant = st.text_input("Previous Surgery (if any)", key="previous_surgery_participant")
    mental_disability_participant = st.text_input("Mental Disability (if any)", key="mental_disability_participant")
    physical_disability_participant = st.text_input("Current Physical Disability or Disease (if any)", key="physical_disability_participant")
    previous_records_participant = st.text_area("Previous Records of Disease or Surgery", key="previous_records_participant")
    pregnancy_participant = st.selectbox("Are you currently pregnant?", ["No", "Yes", "Not applicable"], key="pregnancy_participant")
    breastfeeding_participant = st.selectbox("Are you currently breastfeeding?", ["No", "Yes", "Not applicable"], key="breastfeeding_participant")
    allergy_participant = st.text_input("Allergies (if any)", key="allergy_participant")
    smoking_participant = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"], key="smoking_participant")
    blood_type_participant = st.selectbox("Blood Type", ["A", "B", "AB", "O", "Unknown"], key="blood_type_participant")

    # Define the participant info form submission function
    def submit_form_participant():
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
        if not first_name_participant or not last_name_participant or not age_participant or not sex_participant or not state_participant or not city_participant or not address_participant or not mental_disability_participant or not physical_disability_participant or not pregnancy_participant or not allergy_participant:
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
                # Force a rerun
                st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")

    # Attach the submit_form function to the button
    st.button("Submit", key="submit_button_participant", on_click=submit_form_participant) 

def researcher_profile_setup_page():
    st.title(':blue[T]rial :blue[T]alk')

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
    
    # Define the researcher info form submission function
    def submit_form_researcher():
        # Access all input values from st.session_state
        name_researcher = st.session_state.name_researcher
        organization_email_researcher = st.session_state.organization_email_researcher
        position_researcher = st.session_state.position_researcher
        research_keywords_researcher = st.session_state.research_keywords_researcher
        phone_number_researcher = st.session_state.phone_number_researcher
        uid = st.session_state.username

        # Validate inputs to form
        if not name_researcher or not organization_email_researcher or not phone_number_researcher:
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
                    'timestamp': datetime.datetime.utcnow(),
                    'uid': uid
                }

                # Save the data to Firestore
                researchers.set(data)

                st.success("Form submitted successfully!")
                st.session_state.current_page = 'clinicaltrialdata'
                # Force a rerun
                st.session_state['dummy'] = not st.session_state.get('dummy', False)
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")

    # Attach the submit_form function to the button
    st.button("Submit", key="submit_button_researcher", on_click=submit_form_researcher) 





    

def collect_study_information():
    st.title(':blue[T]rial :blue[T]alk')

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
                    'timestamp': datetime.datetime.utcnow()
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
    st.title(':blue[T]rial :blue[T]alk')

    # Display user info and sign out button
    st.text('Username: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.button('Sign Out', key='signout_button', on_click=sign_out)

    st.title("Clinical Trial Data")

    db = st.session_state.db
    if not db:
        st.error('Database connection not established.')
        return

    clinical_trials = db.collection('clinical_trials').get()

    for clinical_trial in clinical_trials:
        d = clinical_trial.to_dict()
        try:
            # Retrieve data without default values
            nct_id = d.get('nctId', '')
            status_verified_date = d.get('statusVerifiedDate', '')
            brief_title = d.get('briefTitle', 'No Title')
            description = d.get('description', '')

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
            user_query = st.text_input("Ask me Anything:", key=f"ask_{nct_id}")

            # You can later process the user_query as needed
            if user_query:
                print(f"User query for {nct_id}: {user_query}")

            # Add a horizontal line to separate entries
            st.markdown("<hr>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")

def sign_out():
    st.session_state.signout = False
    st.session_state.username = ''
    st.session_state.useremail = ''
    st.session_state.current_page = 'login'
    # Force a rerun
    st.session_state['dummy'] = not st.session_state.get('dummy', False)

app()