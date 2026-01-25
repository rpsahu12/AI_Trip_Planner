import os
from typing import Literal
from pydantic import BaseModel
from utils.config_loader import load_config  # Direct import
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class ModelLoader(BaseModel):
    model_provider: Literal["groq", "google"] = "groq"

    def load_llm(self):
        print(f"DEBUG: Loading config for {self.model_provider}...")
        
        # 1. Load Config
        config = load_config()
        
        # DEBUG PRINT: This will show you exactly what Python sees!
        print(f"DEBUG: Config loaded: {config}")

        if config is None:
            raise ValueError("❌ Config is None! check config.yaml location.")

        try:
            if self.model_provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                # This line is where it was crashing:
                model_name = config["llm"]["groq"]["model_name"]
                return ChatGroq(model=model_name, api_key=api_key)

            elif self.model_provider == "google":
                api_key = os.getenv("GOOGLE_API_KEY")
                model_name = config["llm"]["google"]["model_name"]
                return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)

        except TypeError:
            raise ValueError("❌ YAML FORMAT ERROR: Check indentation in config.yaml. 'llm' or 'groq' is likely empty.")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load LLM: {str(e)}")