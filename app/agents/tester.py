from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config
import re
import logging

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

def generate_tests(specification: str) -> str:
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.2)
    module_name = Config.IMPLEMENTATION_MODULE
    
    messages = [
        SystemMessage(content=(
            "Você é um engenheiro de testes especializado em TDD (Test-Driven Development). "
            "Sua única responsabilidade é escrever testes ANTES da implementação. "
            "\n\nREGRAS IMPORTANTES:"
            "\n1. Escreva APENAS os testes usando pytest"
            f"\n2. Os testes devem importar funções/classes de '{module_name}' (ex: from {module_name} import fizzbuzz)"
            "\n3. NÃO inclua a implementação das funções"
            "\n4. NÃO escreva o código que será testado"
            "\n5. Os testes devem falhar inicialmente (Red do TDD)"
            "\n6. Use assertions claras e descritivas"
            "\n7. Cubra casos normais, edge cases e casos de erro"
            "\n8. Agrupe testes relacionados em funções separadas com nomes descritivos"
            "\n\nFormato esperado:"
            "\nimport pytest"
            f"\nfrom {module_name} import <função_ou_classe>"
            "\n\ndef test_caso1():"
            "\n    assert ..."
            "\n\ndef test_caso2():"
            "\n    assert ..."
        )),
        HumanMessage(content=(
            f"Especificação:\n{specification}\n\n"
            "Crie testes unitários completos em pytest que validem esta especificação. "
            "Lembre-se: escreva APENAS os testes, a implementação virá depois. "
            f"Os testes devem importar de '{module_name}' (ex: from {module_name} import fizzbuzz)."
        ))
    ]
    response = llm.invoke(messages)
    code = extract_code(response.content)
    
    # Validação adicional: garantir que não há implementação
    if has_implementation(code):
        logging.warning("⚠️ Testes contêm implementação, regenerando...")
        return generate_tests(specification)
    
    # Validação: garantir que importa do módulo correto
    if f"from {module_name} import" not in code and f"import {module_name}" not in code:
        logging.warning(f"⚠️ Testes não importam de '{module_name}', corrigindo...")
        # Tenta identificar o que está sendo importado
        import_match = re.search(r'from \w+ import (.+)', code)
        if import_match:
            imports = import_match.group(1)
            code = f"from {module_name} import {imports}\n\n" + re.sub(r'from \w+ import .+\n', '', code)
        else:
            code = f"from {module_name} import *\n\n" + code
    
    return code

def has_implementation(code: str) -> bool:
    """Verifica se o código de teste contém implementação de funções."""
    lines = code.split('\n')
    in_test_function = False
    in_fixture = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detecta fixtures do pytest
        if '@pytest.fixture' in stripped:
            in_fixture = True
            continue
        
        # Detecta início de função de teste
        if stripped.startswith('def test_'):
            in_test_function = True
            in_fixture = False
            continue
        
        # Se estamos fora de função de teste/fixture e encontramos uma definição de função
        if not in_test_function and not in_fixture and stripped.startswith('def ') and not stripped.startswith('def test_'):
            # Ignora se for apenas um helper de teste ou fixture
            if 'helper' not in stripped.lower() and 'fixture' not in stripped.lower() and '@' not in stripped:
                return True
        
        # Detecta fim de função (nova definição ou volta ao nível 0 de indentação)
        if (in_test_function or in_fixture) and stripped and not line.startswith((' ', '\t')):
            in_test_function = False
            in_fixture = False
    
    return False


