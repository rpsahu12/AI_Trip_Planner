from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import uuid

load_dotenv()

# DEBUG: Check if keys are actually loading
print(f"DEBUG: GROQ Key found? {os.getenv('GROQ_API_KEY') is not None}")
print(f"DEBUG: TAVILY Key found? {os.getenv('TAVILY_API_KEY') is not None}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Initialize Graph ONCE at startup ---
try:
    # Initialize the builder once
    graph_builder = GraphBuilder(model_provider="groq")
    react_app = graph_builder() # Compile the graph
    
    # Optional: Save the graph image only once on startup, not every request
    try:
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("travel_agent_graph.png", "wb") as f:
            f.write(png_graph)
        print("Graph visualization saved to travel_agent_graph.png")
    except Exception as img_e:
        print(f"Could not save graph image (requires graphviz): {img_e}")

except Exception as e:
    print(f"CRITICAL ERROR: Could not initialize AI Graph: {e}")
    react_app = None

class QueryRequest(BaseModel):
    question: str
    thread_id: str = None # Optional: Allow client to send a session ID

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    if react_app is None:
        return JSONResponse(status_code=500, content={"error": "AI Agent failed to initialize."})

    try:
        print(f"Received Query: {query.question}")
        
        # --- 2. Manage Thread ID for Memory ---
        # If the user provides a thread_id, use it. If not, generate a new one.
        # Note: To fully support memory, your GraphBuilder must have checkpointer enabled.
        thread_id = query.thread_id or str(uuid.uuid4())
        
        config = {"configurable": {"thread_id": thread_id}}

        # --- 3. Construct Proper Message ---
        # Using HumanMessage is safer than raw strings
        input_message = HumanMessage(content=query.question)
        
        # Invoke the graph
        # We pass the new message. The graph (if checkpointed) handles history.
        output = await react_app.ainvoke({"messages": [input_message]}, config=config)

        # Extract response
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)
        
        return {
            "answer": final_output,
            "thread_id": thread_id # Return the ID so the frontend can send it back next time
        }

    except Exception as e:
        # Print full trace for debugging in console
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "active", "agent_loaded": react_app is not None}