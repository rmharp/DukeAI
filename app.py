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

    st.title(':blue[T]rial :blue[T]alk')
    
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    
    def f():
        try:
            user = auth.get_user_by_email(email)
            st.session_state.useremail = user.email
            st.session_state.username = user.uid
            st.write('Login Succesful')
            #st.session_state.signout = True
            #st.session_state.signedout = True
        
        except:
            st.warning('Login failed please try again.')
            
    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''

    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False
        
    if not st.session_state['signedout']:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
    
        if choice == 'Login':
            email = st.text_input('Email Address')
            password = st.text_input('Password', type = 'password')

            st.button('Login', on_click=f)
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
    
    if st.session_state.signout:
        st.text('Username: ' + st.session_state.username)
        st.text('Email: ' + st.session_state.useremail)
        st.button('Sign Out', on_click=t)

app()