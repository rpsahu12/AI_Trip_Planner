import streamlit as st
import requests
import uuid

# --- Configuration ---
BASE_URL = "http://localhost:8000"  # Ensure this matches your FastAPI port

st.set_page_config(
    page_title="🌍 Travel Agent AI",
    page_icon="✈️",
    layout="centered"
)

st.title("🌍 Travel Planner Agent")

# --- 1. Session State Management ---
# Generate a random ID for this user session if it doesn't exist
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Initialize chat history if empty
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. Display Chat History ---
# This keeps the old messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. Chat Input & Logic ---
# st.chat_input is better than st.text_input for chatbots
if prompt := st.chat_input("Where do you want to go?"):
    
    # A. Display User Message Immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. Call Backend
    with st.chat_message("assistant"):
        with st.spinner("Planning your trip..."):
            try:
                payload = {
                    "question": prompt,
                    "thread_id": st.session_state.thread_id
                }
                
                response = requests.post(f"{BASE_URL}/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    
                    # Display Answer
                    st.markdown(answer)
                    
                    # Save AI message to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    st.error(error_msg)
            
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the backend. Is 'main.py' running?")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")