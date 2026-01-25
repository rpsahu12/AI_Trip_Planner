class TravelAgentException(Exception):
    """Base exception class for the Travel Agent application."""
    def __init__(self, message="An error occurred in the Travel Agent application"):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(TravelAgentException):
    """Raised when the configuration file or environment variables are missing."""
    def __init__(self, message="Configuration error detected"):
        super().__init__(f"⚙️ CONFIG ERROR: {message}")

class ModelLoadError(TravelAgentException):
    """Raised when the AI Model (Groq/Gemini) fails to initialize."""
    def __init__(self, message="Failed to load AI Model"):
        super().__init__(f"🤖 MODEL ERROR: {message}")

class ToolExecutionError(TravelAgentException):
    """Raised when an external tool (Search, Weather) fails."""
    def __init__(self, tool_name, message):
        super().__init__(f"🛠️ TOOL ERROR ({tool_name}): {message}")