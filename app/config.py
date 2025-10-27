import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MODEL = "gpt-4o-mini"
    MAX_ITERATIONS = 5
    WORKSPACE_PATH = "workspace"

    IMPLEMENTATION_MODULE = "implementation"
    TEST_FILE = "test_implementation.py"

