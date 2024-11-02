import streamlit as st
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2


# Initialize Firebase app
cred = credentials.Certificate("streamlitchat-a40f7-8c5fd38d36bf.json")
try:
    firebase_admin.get_app()
except ValueError as e:
    initialize_app(cred)

# Initialize Google OAuth2 client
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_url = "http://localhost:8501/"  # Your redirect URL

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)


st.session_state.email = ''



async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    return await client.get_access_token(code, redirect_url)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_logged_in_user_email():
    try:
        query_params = st.experimental_get_query_params()
        code = query_params.get('code')
        if code:
            token = asyncio.run(get_access_token(client, redirect_url, code))
            st.experimental_set_query_params()

            if token:
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_email)
                    st.session_state.email = user.email
                    return user.email
        return None
    except:
        pass


def show_login_button():
    authorization_url = asyncio.run(client.get_authorization_url(
        redirect_url,
        scope=["email", "profile"],
        extras_params={"access_type": "offline"},
    ))
    st.markdown(f'<a href="{authorization_url}" target="_self">Login</a>', unsafe_allow_html=True)
    get_logged_in_user_email()

def app():
    st.title('Welcome!')
    if not st.session_state.email:
        get_logged_in_user_email()
        if not st.session_state.email:

            show_login_button()

    if st.session_state.email:
        st.write(st.session_state.email)
        if st.button("Logout", type="primary", key="logout_non_required"):
            st.session_state.email = ''
            st.rerun()

app()