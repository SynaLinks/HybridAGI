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

        self.embeddings_model = os.getenv("EMBEDDINGS_MODEL", "togethercomputer/m2-bert-80M-8k-retrieval")
        self.embeddings_dim = int(os.getenv("EMBEDDINGS_DIM", "768"))

        self.max_output_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", 256))
        self.top_p = float(os.getenv("TOP_P", 0.7))
        self.top_k = int(os.getenv("TOP_K", 10))
        self.repetition_penalty = float(os.getenv("REPETITION_PENALTY", 1))

        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")

        self.local_smart_llm_model_url = os.environ.get(
            "LOCAL_SMART_LLM_MODEL_URL",
            "http://localhost:8080")
        self.local_fast_llm_model_url = os.environ.get(
            "LOCAL_FAST_LLM_MODEL_URL",
            "http://localhost:8080")

        self.temperature = float(os.getenv("TEMPERATURE", "0.5"))

        self.max_decision_attemps = int(os.getenv("MAX_DECISION_ATTEMPS", "5"))
        self.max_evaluation_attemps = int(os.getenv("MAX_EVALUATION_ATTEMPS", "5"))
        self.max_iteration = int(os.getenv("MAX_ITERATION", "50"))

        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 0))

        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        
        self.redis_url = os.getenv("REDIS_URL", "redis://falkordb:6379")
        self.memory_index = os.getenv("MEMORY_INDEX", "hybrid-agi")

        self.fast_llm_max_token = os.getenv("FAST_LLM_MAX_TOKEN", "4000")
        self.smart_llm_max_token = os.getenv("SMART_LLM_MAX_TOKEN", "8000")

        self.downloads_directory = os.getenv("DOWNLOADS_DIRECTORY", "./archives")
        self.documentation_directory = os.getenv("DOCUMENTATION_DIRECTORY", "./documentation")
        self.library_directory = os.getenv("LIBRARY_DIRECTORY", "./programs")