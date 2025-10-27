from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config
import re

def extract_code(text: str) -> str:
    """Extract Python code from markdown code blocks or return the text if it's already code."""
    patterns = [
        r'```python\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return '\n\n'.join(matches)
    
    return text.strip()

def generate_code(test_code: str, feedback: str = "", previous_code: str = "") -> str:
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.4)
    module_name = Config.IMPLEMENTATION_MODULE
    
    context_parts = []
    
    if feedback:
        context_parts.append(f"📋 Feedback da execução anterior:\n{feedback}\n")
    
    if previous_code:
        context_parts.append(f"❌ Código anterior que falhou:\n```python\n{previous_code}\n```\n")
    
    context = "\n".join(context_parts) if context_parts else ""
    
    messages = [
        SystemMessage(content=(
            "Você é um desenvolvedor Python seguindo TDD (Test-Driven Development). "
            "Seu trabalho é implementar o código que faz os testes passarem. "
            "\n\nREGRAS IMPORTANTES:"
            "\n1. Escreva APENAS a implementação das funções/classes"
            "\n2. NÃO inclua os testes no código"
            "\n3. NÃO inclua imports de pytest"
            "\n4. Foque em fazer os testes passarem de forma simples e correta"
            "\n5. Se houver feedback, corrija os erros apontados"
            "\n6. Mantenha o código limpo e legível"
            "\n7. Trate exceções quando especificado"
            f"\n8. Este código será salvo no módulo '{module_name}.py'"
            "\n\nFormato esperado:"
            "\ndef função(parametros):"
            "\n    \"\"\"Docstring descritiva.\"\"\""
            "\n    # implementação"
            "\n    return resultado"
        )),
        HumanMessage(content=(
            f"{context}"
            f"📝 Testes que devem passar:\n```python\n{test_code}\n```\n\n"
            "Implemente o código que faz TODOS os testes passarem. "
            "Retorne SOMENTE a implementação, sem os testes, sem imports de pytest."
        ))
    ]
    
    response = llm.invoke(messages)
    code = extract_code(response.content)
    
    # Validação: garantir que não há imports de pytest
    code = remove_test_imports(code)
    
    return code

def remove_test_imports(code: str) -> str:
    """Remove imports relacionados a testes."""
    lines = code.split('\n')
    filtered_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Remove imports de pytest e test_
        if not (stripped.startswith('import pytest') or 
                stripped.startswith('from pytest') or
                ('test_' in stripped and 'import' in stripped)):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)
