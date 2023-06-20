## The class used to configure the system.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
from dotenv import load_dotenv
import logging

load_dotenv(verbose=True)


class Config():
    """Initialize the Config class"""
    def __init__(self):
        self.debug_mode = os.getenv("DEBUG_MODE", "True") == "True"
        self.auto_mode = os.getenv("AUTO_MODE", "False") == "True"
        self.private_mode = os.getenv("PRIVATE_MODE", "False") == "True"

        self.temperature = float(os.getenv("TEMPERATURE", "0.5"))

        self.max_depth = int(os.getenv("MAX_DEPTH", "3"))
        self.max_breadth = int(os.getenv("MAX_BREADTH", "5"))

        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 0))

        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        )
        
        self.redis_url = os.getenv("REDIS_URL", "redis://username:password@localhost:6379")
        self.wipe_redis_on_start = os.getenv("WIPE_REDIS_ON_START", "False") == "True"
        self.memory_index = os.getenv("MEMORY_INDEX", "hybrid-agi")

        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")
        self.openai_base_path = os.environ.get('OPENAI_API_BASE', 'http://localhost:8080/v1')

        self.downloads_directory = os.getenv("DOWNLOADS_DIRECTORY", "archives")

        self.user_language = os.getenv("USER_LANGUAGE", "english")
        self.user_expertise = os.getenv("USER_EXPERTISE", "Nothing")
