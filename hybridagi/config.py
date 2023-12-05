"""The config store. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

class Config():
    """Initialize the Config class"""
    def __init__(self):
        self.verbose = os.getenv("VERBOSE", "True") == "True"
        self.debug_mode = os.getenv("DEBUG_MODE", "True") == "True"
        self.private_mode = os.getenv("PRIVATE_MODE", "False") == "True"

        self.local_model_url = os.environ.get(
            "LOCAL_MODEL_URL",
            "http://localhost:8010")

        self.temperature = float(os.getenv("TEMPERATURE", "0.5"))

        self.max_decision_attemp = int(os.getenv("MAX_DECISION_ATTEMP", "5"))
        self.max_evaluation_attemp = int(os.getenv("MAX_EVALUATION_ATTEMP", "5"))
        self.max_iteration = int(os.getenv("MAX_ITERATION", "50"))

        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 0))

        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.memory_index = os.getenv("MEMORY_INDEX", "hybrid-agi")

        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")

        self.fast_llm_max_token = os.getenv("FAST_LLM_MAX_TOKEN", "4000")
        self.smart_llm_max_token = os.getenv("SMART_LLM_MAX_TOKEN", "8000")

        self.downloads_directory = os.getenv("DOWNLOADS_DIRECTORY", "archives")
        self.library_directory = os.getenv("LIBRARY_DIRECTORY", "")

        self.user_language = os.getenv("USER_LANGUAGE", "English")
