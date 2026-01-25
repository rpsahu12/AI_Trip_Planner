from utils.place_info_search import TavilyPlaceSearchTool
from typing import List
from langchain.tools import tool

class PlaceSearchTool:
    def __init__(self):
        self.tavily_search = TavilyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the place search tool"""

        @tool
        def search_attractions(place: str) -> str:
            """Search attractions of a place"""
            return self.tavily_search.tavily_search_attractions(place)

        @tool
        def search_restaurants(place: str) -> str:
            """Search restaurants of a place"""
            return self.tavily_search.tavily_search_restaurants(place)

        @tool
        def search_activities(place: str) -> str:
            """Search activities of a place"""
            return self.tavily_search.tavily_search_activity(place)

        @tool
        def search_transportation(place: str) -> str:
            """Search transportation of a place"""
            return self.tavily_search.tavily_search_transportation(place)

        return [
            search_attractions,
            search_restaurants,
            search_activities,
            search_transportation,
        ]
