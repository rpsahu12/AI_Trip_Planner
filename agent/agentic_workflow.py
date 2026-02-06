from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

# Import your tools
from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.expense_calculator_tool import CalculatorTool
from tools.currency_conversion_tool import CurrencyConvertorTool
from pydantic import BaseModel, Field
from typing import List, Optional

class GraphBuilder:
    def __init__(self, model_provider: str = "groq"):
        # 1. Load LLM
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        if not self.llm:
            raise ValueError(f"Failed to load LLM for provider: {model_provider}")

        # 2. Load Tools
        self.tools = []
        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConvertorTool()
        
        self.tools.extend([
            *self.weather_tools.weather_tool_list, 
            *self.place_search_tools.place_search_tool_list,
            *self.calculator_tools.calculator_tool_list,
            *self.currency_converter_tools.currency_converter_tool_list
        ])
        
        # 3. Bind Tools to LLM
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        # 4. FIX: Ensure System Prompt is a Message Object, not just a string
        if isinstance(SYSTEM_PROMPT, str):
            self.system_prompt = SystemMessage(content=SYSTEM_PROMPT)
        else:
            self.system_prompt = SYSTEM_PROMPT

        self.graph = None

    def agent_function(self, state: MessagesState):
        """Main Agent Function"""
        user_question = state["messages"]
        
        # Now this is safe: [SystemMessage] + [HumanMessage, AIMessage...]
        input_messages = [self.system_prompt] + user_question
        
        response = self.llm_with_tools.invoke(input_messages)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        
        # Add Nodes
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        
        # Add Edges
        graph_builder.add_edge(START, "agent")
        
        # FIX: Only use conditional edge. 
        # tools_condition automatically handles:
        # 1. If tool called -> Go to "tools"
        # 2. If no tool -> Go to END
        graph_builder.add_conditional_edges("agent", tools_condition)
        
        # When tools finish, go back to agent to read the results
        graph_builder.add_edge("tools", "agent")
        
        # DO NOT add_edge("agent", END) here. It conflicts with conditional_edges.

        # Compile
        # Use MemorySaver here if you want conversation history in the future
        from langgraph.checkpoint.memory import MemorySaver
        memory = MemorySaver()
        self.graph = graph_builder.compile(checkpointer=memory)
        
        return self.graph

    def __call__(self):
        return self.build_graph()
    def convert_to_coordinates(self, itinerary_text: str):
        """
        Takes the text plan from the agent and converts it to coordinates
        using a structured LLM call.
        """
        # Create a specialized LLM just for formatting
        structured_llm = self.llm.with_structured_output(TripItinerary)
        
        # Invoke it with the text
        return structured_llm.invoke(itinerary_text)

# --- Map Data Structures ---
class ItineraryLocation(BaseModel):
    name: str = Field(description="Name of the location, hotel, or landmark")
    description: str = Field(description="One sentence description of why to visit")
    latitude: float = Field(description="The latitude of the location")
    longitude: float = Field(description="The longitude of the location")
    type: str = Field(description="Type of location: 'hotel', 'restaurant', or 'activity'")

class TripItinerary(BaseModel):
    trip_title: str = Field(description="A catchy title for the trip")
    locations: List[ItineraryLocation]
# ---------------------------