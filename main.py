from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import asyncio

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 1. Initialize Graph ---
try:
    graph_builder = GraphBuilder(model_provider="groq")
    react_app = graph_builder() 
except Exception as e:
    print(f"CRITICAL ERROR: Could not initialize AI Graph: {e}")
    react_app = None

# --- 2. In-Memory Storage ---
# Added 'latest_plan' to store the most recent itinerary text
rooms = {}

# --- 3. Pydantic Models ---
class QueryRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None

class CreateRoomRequest(BaseModel):
    host_name: str

class JoinRoomRequest(BaseModel):
    room_code: str
    user_name: str

class PreferenceSubmission(BaseModel):
    room_code: str
    user_name: str
    preferences: Dict 

class GeneratePlanRequest(BaseModel):
    room_code: str

class GroupChatRequest(BaseModel):
    room_code: str
    user_name: str
    message: str

# --- 4. Endpoints ---

@app.post("/create-room")
def create_room(req: CreateRoomRequest):
    room_code = str(uuid.uuid4())[:6].upper()
    rooms[room_code] = {
        "users": [req.host_name],
        "preferences": [],
        "status": "waiting",
        "chat_history_thread": str(uuid.uuid4()), # Shared memory ID for this group
        "latest_plan": None # Stores the current text of the plan
    }
    return {"room_code": room_code, "message": "Room created"}

@app.post("/join-room")
def join_room(req: JoinRoomRequest):
    if req.room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if req.user_name not in rooms[req.room_code]["users"]:
        rooms[req.room_code]["users"].append(req.user_name)
    return {"message": "Joined successfully"}

@app.get("/room-status/{room_code}")
def get_room_status(room_code: str):
    if room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_code]

@app.post("/submit-preferences")
def submit_preferences(sub: PreferenceSubmission):
    if sub.room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Update logic
    rooms[sub.room_code]["preferences"] = [
        p for p in rooms[sub.room_code]["preferences"] if p["user"] != sub.user_name
    ]
    rooms[sub.room_code]["preferences"].append({
        "user": sub.user_name,
        "data": sub.preferences
    })
    return {"message": "Preferences received"}

# --- HELPER: Common function to talk to AI ---
async def ask_agent(prompt: str, thread_id: str):
    if react_app is None:
        raise Exception("AI Agent not initialized")
    
    config = {"configurable": {"thread_id": thread_id}}
    input_message = HumanMessage(content=prompt)
    output = await react_app.ainvoke({"messages": [input_message]}, config=config)
    
    if isinstance(output, dict) and "messages" in output:
        return output["messages"][-1].content
    return str(output)

@app.post("/generate-group-plan")
async def generate_group_plan(req: GeneratePlanRequest):
    """Initial generation of the plan."""
    if req.room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[req.room_code]
    prefs = room["preferences"]
    
    if not prefs:
        raise HTTPException(status_code=400, detail="No preferences submitted yet.")

    destinations = [p['data'].get('destination', 'Unknown') for p in prefs]
    main_destination = next((d for d in destinations if d and d != "Unknown"), "Dream Vacation")

        # --- Construct the Conflict Resolution Prompt ---
    diplomat_prompt = (
        "Act as a travel diplomat and expert planner for a group of friends. "
        "Here are the conflicting preferences from the group members:\n\n"
    )
    
    for p in prefs:
        user = p['user']
        data = p['data']
        diplomat_prompt += f"- User {user}: Wants {data.get('destination', 'Anywhere')}, Interest: {data.get('vibe', 'Any')}, Budget: {data.get('budget', 'Flexible')}\n"

    diplomat_prompt += (
    "\nTASK:\n"
    "You are an AI travel diplomat responsible for creating a fair, transparent, and detailed travel plan "
    "for multiple people with possibly conflicting preferences.\n\n"

    "1. Analyze all user requests and preferences. "
    "If there are contradictions (e.g., 'Snow' vs 'Beach', 'Luxury' vs 'Budget'), "
    "propose one or more fair solutions such as:\n"
    "   - A multi-destination or split itinerary\n"
    "   - Nearby locations that satisfy both preferences\n"
    "   - A best-compromise plan based on majority preference\n\n"

    "2. Create a DAY-WISE detailed itinerary including:\n"
    "   - Locations covered each day\n"
    "   - Activities with approximate timing\n"
    "   - Travel mode between places\n\n"

    "3. For EACH major component (Hotels, Travel, Activities), provide MULTIPLE OPTIONS:\n"
    "   - Budget Option\n"
    "   - Mid-Range Option\n"
    "   - Premium Option\n\n"

    "4. HOTEL OPTIONS:\n"
    "   - Suggest at least 2-3 hotels per destination\n"
    "   - Mention hotel name, star rating, location\n"
    "   - Price per night per person in ₹ (INR)\n"
    "   - Booking platforms (e.g., MakeMyTrip, Booking.com, Agoda)\n\n"

    "5. TRAVEL OPTIONS:\n"
    "   - Intercity travel (Flight / Train / Bus / Cab)\n"
    "   - Mention provider name (e.g., IRCTC, Indigo, Vistara, RedBus, Uber Intercity)\n"
    "   - Approximate cost per person\n\n"

    "6. ACTIVITIES & ATTRACTIONS:\n"
    "   - Mention specific attractions, parks, experiences\n"
    "   - Entry fees or activity cost per person\n"
    "   - Optional alternatives where applicable\n\n"

    "7. COST BREAKDOWN:\n"
    "   - Per-person cost breakdown (Hotels, Travel, Activities, Food, Misc.)\n"
    "   - Total group cost\n"
    "   - Separate totals for Budget / Mid-Range / Premium plans\n\n"

    "8. VOTING SUMMARY PER OPTION:\n"
    "   - For each major option (hotel tier, travel mode, itinerary style), "
    "     summarize how many participants are satisfied or prefer it\n"
    "   - Present this as a simple table or bullet summary\n"
    "   - Clearly identify the option with the highest overall acceptance\n\n"

    "9. RISK ALERTS & CONSIDERATIONS:\n"
    "   - Weather risks (rain, snowfall, heatwaves, humidity)\n"
    "   - Crowd risk (peak season, festivals, weekends)\n"
    "   - Seasonal limitations (closures, restricted access, surge pricing)\n"
    "   - Provide mitigation tips or safer alternatives where possible\n\n"

    "10. FAIRNESS JUSTIFICATION:\n"
    "   - Explain clearly why the final recommended plan is fair for all participants\n"
    "   - Mention how conflicting preferences are balanced\n\n"

    "11. ASSUMPTIONS & FLEXIBILITY:\n"
    "   - Mention assumptions made (season, availability, pricing variability)\n"
    "   - Clearly state that prices are approximate and subject to change\n"
    )

    # Call AI
    plan_text = await ask_agent(diplomat_prompt, room["chat_history_thread"])

    # 2. NEW: Generate Map Coordinates based on the Plan Text
    # We run this in a thread to keep the server responsive
    try:
        print("🗺️ Generating Map Coordinates...")
        map_data = await asyncio.to_thread(graph_builder.convert_to_coordinates, plan_text)
        map_json = map_data.dict() # Convert Pydantic model to Dict
    except Exception as e:
        print(f"⚠️ Map generation failed: {e}")
        map_json = None
        
    # SAVE the plan to the room so everyone sees it
    room["latest_plan"] = plan_text
    
    return {"answer": plan_text, "map_data": map_json}

@app.post("/chat-group")
async def chat_group(req: GroupChatRequest):
    """Follow-up chat to refine the plan."""
    if req.room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[req.room_code]
    
    # Construct a prompt that includes who is asking
    context_prompt = f"User '{req.user_name}' says: {req.message}. Update the plan accordingly."
    
    # Call AI with the SAME thread_id to maintain context
    updated_plan = await ask_agent(context_prompt, room["chat_history_thread"])
    
    # Update the shared plan
    room["latest_plan"] = updated_plan
    
    try:
        map_data = await asyncio.to_thread(graph_builder.convert_to_coordinates, updated_plan)
        map_json = map_data.dict()
    except Exception as e:
        print(f"⚠️ Map update failed: {e}")
        map_json = None
    
    return {
        "answer": updated_plan,
        "map_data": map_json
    }

# --- Solo Chat Endpoint ---
solo_sessions = {} 

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        thread_id = query.thread_id or str(uuid.uuid4())
        
        # Initialize session if new
        if thread_id not in solo_sessions:
            solo_sessions[thread_id] = {"latest_plan": None}
            
        # Contextual Prompt
        current_plan = solo_sessions[thread_id]["latest_plan"]
        final_prompt = query.question
        
        if current_plan and "plan" not in query.question.lower():
             final_prompt = f"Current Plan: {current_plan}\n\nUser Request: {query.question}\n\nTask: Update the plan based on the request."

        # Call AI Agent (Text)
        answer = await ask_agent(final_prompt, thread_id)
        
        # Update the stored plan if the answer looks like an itinerary
        if "Day 1" in answer or "Itinerary" in answer:
            solo_sessions[thread_id]["latest_plan"] = answer

        # 2. NEW: Generate Map Coordinates
        map_json = None
        # Only try to make a map if we actually have a plan in the answer
        if "Day 1" in answer or "Itinerary" in answer:
            try:
                map_data = await asyncio.to_thread(graph_builder.convert_to_coordinates, answer)
                map_json = map_data.dict()
            except Exception as e:
                print(f"⚠️ Map generation failed: {e}")

        return {
            "answer": answer, 
            "thread_id": thread_id,
            "latest_plan": solo_sessions[thread_id]["latest_plan"],
            "map_data": map_json 
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})