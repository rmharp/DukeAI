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
#firebase_admin.initialize_app(cred)


def app():

    st.header('Hello 🌎!')
    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
    if choice == 'Login':
        email = st.text_input('Email Address')
        password = st.text_input('Password', type = 'password')

        st.button('Login')
    else: 
        email = st.text_input('Email Address')
        password = st.text_input('Password', type = 'password')
        username = st.text_input('Enter your unique username')

        if st.button('Create my account'):
            user = auth.create_user(email = email, password = password, uid=username)
            #user = sign_up_with_email_and_password(email=email,password=password,username=username)
            
            st.success('Account created successfully!')
            st.markdown('Please Login using your email and password')
            st.balloons()
        
app()