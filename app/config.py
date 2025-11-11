import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MODEL = "gpt-4o-mini"
    MAX_ITERATIONS = 10  # Aumentado para o ciclo incremental
    WORKSPACE_PATH = "workspace"

    IMPLEMENTATION_MODULE = "app_code"  # Nome do arquivo de implementação (app_code.py)
    TEST_FILE = "test_app.py"          # Nome do arquivo de teste
    # Chave para armazenar o estado do plano no Redis
    PLAN_KEY = "tdd_plan_queue"

