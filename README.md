<h1 align="center">🌍 AI Trip Planner & Group Diplomat</h1>
<p align="center">
  <i>Your intelligent travel companion — plan smarter, travel better, and stop fighting over the itinerary.</i><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/badge/FastAPI-Framework-green?style=flat-square&logo=fastapi">
  <img src="https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square&logo=streamlit">
  <img src="https://img.shields.io/badge/GenAI-LLM-yellow?style=flat-square&logo=openai">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square">
</p>

> ⚠️ **Note on Performance:** This app is hosted on a **Free Tier** instance on Render. If the app does not load immediately, please allow **30–60 seconds** for the server to "wake up" (Cold Start). Once active, the experience is fast and responsive.

---

## 🧭 Introduction

**AI Trip Planner** is a Gen AI-driven assistant designed to make travel planning effortless and personalized. Unlike traditional planners, this system uses an **AI Diplomat** to resolve group conflicts, finding the mathematical intersection of everyone's interests, budgets, and vibes.

Powered by **Python** and **FastAPI**, the system delivers a customized travel itinerary optimized for time, cost, and user satisfaction.

---

## 💡 Key Features

- 🤝 **NEW: Multi-User Collaboration:** Stop the group chat chaos. Create a room code, invite friends, and let everyone submit their own preferences privately.
- 🧠 **AI-Powered "Diplomacy":** If friends have conflicting interests (e.g., Beach vs. Mountains), the AI finds a fair compromise or proposes a multi-stop route.
- 💬 **Conversational Refinement:** After the plan is generated, chat with the AI to tweak details (e.g., *"Change Day 2 dinner to a cheaper spot"*).
- 💰 **INR Localization:** All costs and budget estimates are strictly provided in **Indian Rupees (₹)**.
- ⚡ **Real-Time Adaptability:** Updates itineraries based on intent and natural language feedback.

---

## 🧩 Tech Stack

| Category | Technology |
|-----------|-------------|
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **AI Agents** | LangGraph / LangChain |
| **LLM Provider** | Groq (Llama 3) |
| **Search Tool** | Tavily AI |
| **Deployment** | Render (Backend) & Streamlit Cloud (Frontend) |

---

## ⚙️ How It Works

1. **Lobby Creation:** The host starts a "Group Room" and shares a 6-digit code.
2. **Preference Collection:** Friends join the lobby and use a continuous slider to set their budget and choose their "vibe" (Party, Relax, Nature, etc.).
3. **The Unbiased Plan:** The AI aggregates all data and generates a consensus-based itinerary.
4. **Interactive Chat:** The group can continue chatting with the LLM to refine the final plan until everyone is satisfied.

---

## 📦 Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/rpsahu12/AI_Trip_Planner.git](https://github.com/rpsahu12/AI_Trip_Planner.git)
cd AI_Trip_Planner

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Backend
uvicorn main:app --reload

# Run Frontend (New Terminal)
streamlit run app.py
