import streamlit as st
import requests
import uuid
import time
import os

BASE_URL = os.getenv(
    "BACKEND_URL",
    "https://ai-trip-planner-ytay.onrender.com"
)

st.set_page_config(page_title="🌍 AI Trip Planner", page_icon="✈️", layout="wide")

# --- Session State ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "room_code" not in st.session_state:
    st.session_state.room_code = None
if "username" not in st.session_state:
    st.session_state.username = None
# We use this to track if a plan exists in the lobby
if "shared_plan" not in st.session_state:
    st.session_state.shared_plan = None

# --- Helper: Lobby Polling ---
@st.fragment(run_every=3)
def show_lobby_status():
    st.subheader("Friends in Lobby")
    try:
        status_res = requests.get(f"{BASE_URL}/room-status/{st.session_state.room_code}")
        if status_res.status_code == 200:
            room_data = status_res.json()
            users = room_data["users"]
            prefs = room_data["preferences"]
            
            # Check if there is a generated plan shared with the room
            latest_plan_from_server = room_data.get("latest_plan")
            
            submitted_users = [p['user'] for p in prefs]

            for u in users:
                status_icon = "✅" if u in submitted_users else "⏳"
                st.write(f"{status_icon} **{u}**")
            
            # Return data to main flow
            return submitted_users, latest_plan_from_server
            
    except Exception:
        st.warning("Connecting...")
        return [], None

# --- Sidebar ---
st.sidebar.title("✈️ Navigator")
mode = st.sidebar.radio("Choose Mode:", ["🤖 Solo Chat", "👥 Group Planner"])

# ==========================================
# MODE 1: SOLO CHAT (Side-by-Side Layout)
# ==========================================
if mode == "🤖 Solo Chat":
    st.title("🤖 Personal Travel Agent")
    st.caption("Plan your trip, then chat to modify it.")

    if "solo_plan" not in st.session_state:
        st.session_state.solo_plan = None

    # --- LAYOUT: 2 Columns instead of Tabs ---
    col1, col2 = st.columns([1.5, 1]) # Plan is wider (60%), Chat is narrower (40%)

    # LEFT COLUMN: The Plan
    with col1:
        st.subheader("📄 Itinerary")
        if st.session_state.solo_plan:
            st.markdown(st.session_state.solo_plan)
        else:
            st.info("👈 Use the chat on the right to generate a plan!")

    # RIGHT COLUMN: The Chat
    with col2:
        st.subheader("💬 Chat")
        
        # Container for chat history (scrollable)
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input is now ALWAYS visible on the right
        if prompt := st.chat_input("Where to? (e.g. 'Goa for 3 days')"):
            
            # 1. Show User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # 2. Call Backend
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            payload = {
                                "question": prompt,
                                "thread_id": st.session_state.thread_id
                            }
                            response = requests.post(f"{BASE_URL}/query", json=payload)
                            
                            if response.status_code == 200:
                                data = response.json()
                                answer = data.get("answer", "No answer.")
                                latest_plan = data.get("latest_plan")
                                
                                if latest_plan:
                                    st.session_state.solo_plan = latest_plan
                                    # Force a rerun so the Left Column updates immediately
                                    st.rerun()
                                
                                st.markdown(answer)
                                st.session_state.messages.append({"role": "assistant", "content": answer})
                            else:
                                st.error(f"Error {response.status_code}")
                        except Exception as e:
                            st.error(f"Connection Error: {str(e)}")

# ==========================================
# MODE 2: GROUP PLANNER
# ==========================================
elif mode == "👥 Group Planner":
    st.title("👥 Group Trip Collaboration")

    # LOGIN SCREEN
    if not st.session_state.room_code:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🆕 Create Group")
            h_name = st.text_input("Host Name")
            if st.button("Create"):
                res = requests.post(f"{BASE_URL}/create-room", json={"host_name": h_name})
                if res.status_code == 200:
                    st.session_state.room_code = res.json()["room_code"]
                    st.session_state.username = h_name
                    st.rerun()
        with col2:
            st.subheader("🔗 Join Group")
            j_name = st.text_input("Your Name")
            code = st.text_input("Room Code")
            if st.button("Join"):
                res = requests.post(f"{BASE_URL}/join-room", json={"room_code": code, "user_name": j_name})
                if res.status_code == 200:
                    st.session_state.room_code = code
                    st.session_state.username = j_name
                    st.rerun()

    # INSIDE LOBBY
    else:
        st.info(f"**Room:** `{st.session_state.room_code}` | **User:** {st.session_state.username}")
        
        col_left, col_right = st.columns([1, 2])

        with col_left:
            # Polling for Users AND Plan updates
            users, server_plan = show_lobby_status()
            
            # Sync server plan to local session
            if server_plan:
                st.session_state.shared_plan = server_plan

        with col_right:
            # IF NO PLAN YET: Show Preferences Form
            if not st.session_state.shared_plan:
                st.subheader("📝 Submit Preferences")
                with st.form("prefs"):
                    dest = st.text_input("Destination", "Anywhere")
                    vibe = st.selectbox("Vibe", ["Relaxing", "Party", "Adventure", "Culture"])
                    budget = st.slider("Budget (INR)", 5000, 200000, 10000)
                    if st.form_submit_button("Submit"):
                        requests.post(f"{BASE_URL}/submit-preferences", json={
                            "room_code": st.session_state.room_code,
                            "user_name": st.session_state.username,
                            "preferences": {"destination": dest, "vibe": vibe, "budget": f"₹{budget}"}
                        })
                        st.toast("Submitted!")
                
                # Generate Button (Only if people are there)
                if users:
                    if st.button("🚀 Generate Plan"):
                        with st.spinner("Negotiating..."):
                            requests.post(f"{BASE_URL}/generate-group-plan", json={"room_code": st.session_state.room_code})
                            st.rerun()

            # IF PLAN EXISTS: Show Plan + Chat Interface
            else:
                st.success("🎉 Plan Generated!")
                
                # Tabbed view: Plan vs Chat
                tab1, tab2 = st.tabs(["📄 Current Itinerary", "💬 Discuss & Modify"])
                
                with tab1:
                    st.markdown(st.session_state.shared_plan)
                
                with tab2:
                    st.write("Does this work for everyone? Ask for changes below.")
                    
                    # Group Chat Input
                    if chat_input := st.chat_input("Suggest a change (e.g. 'Add a fancy dinner on day 2')"):
                        with st.spinner("Updating plan..."):
                            res = requests.post(f"{BASE_URL}/chat-group", json={
                                "room_code": st.session_state.room_code,
                                "user_name": st.session_state.username,
                                "message": chat_input
                            })
                            if res.status_code == 200:
                                st.toast("Plan Updated!")
                                st.rerun() # Force refresh to show new plan
