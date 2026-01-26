<h1 align="center">🌍 AI Trip Planner & Group Diplomat</h1>
<p align="center">
  <i>Plan smarter, travel better, and stop fighting over the itinerary.</i><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-green?style=flat-square&logo=fastapi">
  <img src="https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square&logo=streamlit">
  <img src="https://img.shields.io/badge/GenAI-LLM-yellow?style=flat-square&logo=openai">
</p>

---

## 🧭 Introduction

**AI Trip Planner** is a next-generation travel assistant designed to solve the two biggest headaches in travel: **planning hours** and **group conflicts**.

Traditional planning is fragmented. Group trips are worse—endless group chats, conflicting budgets, and "I don't care, you decide" attitudes. This application solves both using **Generative AI** and a **Real-Time Lobby System**.

Whether you are a solo backpacker or a group of six with completely different budgets, our **AI Diplomat** analyzes everyone's preferences to mathematically find the perfect compromise itinerary.

---

## 🌟 Key Features

### 🤝 **NEW: Multi-User Collaboration ("The Lobby")**
Stop the group chat chaos.
- **Invite Friends:** Create a room code and invite friends to join your live lobby.
- **Real-Time Voting:** Each user privately submits their budget, preferred vibe (Party vs. Relax), and interests.
- **The AI Diplomat:** Our algorithm aggregates conflicting data (e.g., "Low Budget" vs. "Luxury") and generates a **single, unbiased itinerary** that acts as a fair compromise.
- **Group Chat:** Discuss and refine the plan live with the AI after it's generated.

### 🧠 **Intelligent Personalization**
- Understands natural language (e.g., *"Plan a romantic getaway to Paris, but keep it under ₹1.5 Lakh"*).
- tailor-made day-wise itineraries including hotels, restaurants, and hidden gems.

### ⚡ **Real-Time Adaptability**
- **Dynamic Replanning:** Ask the AI to change plans on the fly (e.g., *"It's raining, give us indoor options for today"*).
- **Currency Localization:** automatically handles costs in your local currency (₹ INR).

### 🔒 **Secure & Scalable**
- Built on **FastAPI** for high-performance async processing.
- Scalable architecture ready for **AWS Cloud** deployment.

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|-------------|
| **Frontend** | Streamlit (Python-based UI) |
| **Backend** | FastAPI (High-performance API) |
| **AI Agents** | LangGraph / LangChain |
| **LLM Provider** | Groq / OpenAI |
| **Real-Time State** | Python Async / Session State |
| **Deployment** | Docker / AWS |

---

## ⚙️ How It Works

### 1. **The Lobby (Group Mode)**
1.  **Host** creates a room and shares the unique **Room Code**.
2.  **Friends** join via their own devices using the code.
3.  Everyone submits their individual preferences (Budget, Vibe, Destination).
4.  The **AI Diplomat** processes all inputs to find the intersection of interests.

### 2. **The Generation (AI Core)**
1.  The backend aggregates the data (e.g., *3 users want "Party", 1 wants "History"*).
2.  The LLM generates a mathematically weighted plan.
3.  The final itinerary is broadcasted to all screens simultaneously.

### 3. **The Refinement**
1.  Users can chat with the plan: *"Change dinner on Day 2 to something cheaper."*
2.  The plan updates in real-time for the whole group.

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone [https://github.com/rpsahu12/AI_Trip_Planner.git](https://github.com/rpsahu12/AI_Trip_Planner.git)
cd AI_Trip_Planner

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up Environment Variables (.env)
# Create a .env file and add your API keys:
# GROQ_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here

# 5. Run the Backend (FastAPI)
uvicorn main:app --reload

# 6. Run the Frontend (Streamlit) (New Terminal)
streamlit run app.py
