from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config

def analyze_failures(test_output: str) -> str:
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.2)
    messages = [
        SystemMessage(content=(
            "Você é um revisor técnico de software especializado em debugging. "
            "Analise falhas de testes e forneça feedback claro e objetivo sobre os problemas encontrados."
        )),
        HumanMessage(content=(
            f"Analise o resultado do pytest abaixo e descreva:\n"
            f"1. Quais testes falharam e por quê\n"
            f"2. O que precisa ser corrigido no código\n"
            f"3. Sugestões específicas de correção\n\n"
            f"Resultado pytest:\n{test_output}"
        ))
    ]
    response = llm.invoke(messages)
    return response.content.strip()
