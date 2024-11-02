import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import json
import requests

cred = credentials.Certificate('dukeai-103f8-369df2b50aa4.json')
# firebase_admin.initialize_app(cred)

def participant_profile_setup_page():
    st.title("Set up your Profile")

    with st.form("profile_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        sexuality = st.selectbox("Sexuality", ["Heterosexual", "Homosexual", "Bisexual", "Other"])
        age = st.number_input("Age", min_value=0)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        location = st.text_input("Location")
        height = st.number_input("Height (in cm)", min_value=0.0)
        weight = st.number_input("Weight (in kg)", min_value=0.0)
        previous_surgery = st.text_input("Previous Surgery (if any)")
        mental_disability = st.text_input("Mental Disability (if any)")
        physical_disability = st.text_input("Current Physical Disability or Disease (if any)")
        previous_records = st.text_area("Previous Records of Disease or Surgery")
        pregnancy = st.selectbox("Are you currently pregnant?", ["No", "Yes", "Not applicable"])
        breastfeeding = st.selectbox("Are you currently breastfeeding?", ["No", "Yes", "Not applicable"])
        allergy = st.text_input("Allergies (if any)")
        smoking = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"])
        blood_type = st.selectbox("Blood Type", ["A", "B", "AB", "O", "Unknown"])

        # Submit button
        submitted = st.form_submit_button("Submit Profile")
        if submitted:
            st.success("Profile information saved successfully!")    

def role_selection_page():
    st.title("Select your position:")
    
    if st.button('Participant'):
        st.write("You selected Participant.")
        st.session_state.show_role_selection = False
        st.session_state.show_participant_profile = True  # Show participant profile setup
    elif st.button('Researcher'):
        st.write("You selected Researcher.")
        st.session_state.show_role_selection = False

def app():
    st.title(':blue[T]rial :blue[T]alk')
    
    # Initialize session state variables
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'show_role_selection' not in st.session_state:
        st.session_state.show_role_selection = False 
    if 'show_participant_profile' not in st.session_state:
        st.session_state.show_participant_profile = False
    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False

    def state_setup():
        try:
            user = auth.get_user_by_email(email)
            st.session_state.useremail = user.email
            st.session_state.username = user.uid
            st.session_state.show_role_selection = True
            st.write('Login Successful')
        except:
            st.warning('Login failed, please try again.')
            
    def reset_states():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.show_role_selection = False
        st.session_state.show_participant_profile = False
        st.session_state.username = ''

    if st.session_state.username:
        if st.session_state.show_participant_profile:
            participant_profile_setup_page()
        elif st.session_state.show_role_selection:
            role_selection_page()
        else:
            # Default content after login
            st.write(f"Welcome, {st.session_state.username}!")
            if st.button('Sign Out'):
                reset_states()
    else:
        # Login/Signup form
        choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
    
        if choice == 'Login':
            global email  # Make email accessible to the state_setup function
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')
            if st.button('Login'):
                state_setup()
        else: 
            # Sign up form
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')
            username = st.text_input('Enter your unique username')

            if st.button('Create my account'):
                user = auth.create_user(email=email, password=password, uid=username)
                st.success('Account created successfully!')
                st.markdown('Please login using your email and password')
                st.balloons()

app()