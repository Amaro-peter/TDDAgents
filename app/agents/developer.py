import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config
import logging

def remove_test_imports(code: str) -> str:
    """Remove imports relacionados a testes."""
    lines = code.split('\n')
    return '\n'.join([line for line in lines if not (line.strip().startswith('import pytest') or line.strip().startswith('from pytest'))])

def generate_code_incremental(
    test_code: str,
    function_name: str,
    feedback: str = "",
    previous_code: str = ""
) -> str:
    """Gera código MÍNIMO para fazer os testes passarem."""
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.3)
    
    context_parts = []
    if feedback:
        context_parts.append(f"FEEDBACK DO REVISOR:\n{feedback}")
    if previous_code:
        clean_prev = previous_code.strip()
        if clean_prev and clean_prev != "# Implementação incremental via TDD":
            context_parts.append(f"CÓDIGO ANTERIOR:\n```python\n{clean_prev}\n```")
    
    context = "\n\n".join(context_parts) if context_parts else ""
    
    system_msg = SystemMessage(content=(
        f"Você é o DESENVOLVEDOR (Developer) em um fluxo de Test-Driven Development (TDD).\n\n"
        f"⚠️⚠️⚠️ ATENÇÃO CRÍTICA ⚠️⚠️⚠️\n"
        f"A função que você DEVE implementar se chama: **{function_name}**\n"
        f"NÃO invente outro nome! Use EXATAMENTE: def {function_name}(...)\n\n"
        f"🧩 PRINCÍPIO DE TDD:\n"
        f"Implemente APENAS o código mínimo necessário para que os testes atuais passem.\n"
        f"Seu papel é evoluir o código passo a passo conforme novos testes são adicionados.\n\n"
        f"📜 REGRAS FUNDAMENTAIS:\n"
        f"1. Analise cuidadosamente os testes fornecidos.\n"
        f"2. Implemente a função {function_name} com a assinatura correta.\n"
        f"3. Escreva SOMENTE o código mínimo necessário para fazer os testes atuais passarem.\n"
        f"4. NÃO tente generalizar o comportamento ainda — apenas o suficiente para os testes disponíveis.\n"
        f"5. Preserve qualquer implementação anterior que já funciona corretamente.\n"
        f"6. Quando houver testes diversos e cobrindo casos distintos, você PODE começar a generalizar a lógica.\n"
        f"7. Sempre mantenha o código limpo, consistente e legível.\n\n"
        f"💡 DICA:\n"
        f"Imagine que você está escrevendo a menor solução possível para que os testes parem de falhar.\n"
        f"Evite adicionar comportamento não testado.\n\n"
        f"📦 FORMATO DE RESPOSTA OBRIGATÓRIO:\n"
        f"⚠️ CRÍTICO: Retorne APENAS o código Python puro, SEM blocos markdown.\n"
        f"⚠️ NÃO use ```python ou ``` na resposta.\n"
        f"⚠️ Retorne SOMENTE a função Python como string:\n\n"
        f"def {function_name}(...):\n"
        f"    # Código mínimo para passar nos testes\n"
        f"    return result\n\n"
        f"EXEMPLO CORRETO DE RESPOSTA:\n"
        f"def {function_name}(s):\n"
        f"    if not s:\n"
        f"        return 0\n"
        f"    total = 0\n"
        f"    for char in s:\n"
        f"        total += values[char]\n"
        f"    return total\n\n"
        f"EXEMPLO ERRADO (NÃO FAÇA ISSO):\n"
        f"```python\n"
        f"def {function_name}(s):\n"
        f"    ...\n"
        f"```\n\n"
        f"⚠️ LEMBRE-SE:\n"
        f"- Retorne APENAS código Python puro\n"
        f"- SEM markdown, SEM backticks, SEM explicações\n"
        f"- Use sempre 'def {function_name}(...):'\n"
        f"- NÃO mude o nome da função"
    ))

    human_msg = HumanMessage(content=(
        f"NOME DA FUNÇÃO (use EXATAMENTE este): {function_name}\n\n"
        f"TESTES QUE DEVEM PASSAR:\n```python\n{test_code}\n```\n\n"
        f"{context}\n\n"
        f"TAREFA:\n"
        f"1. Implemente a função {function_name}.\n"
        f"2. Faça com que TODOS os testes acima passem.\n"
        f"3. Escreva apenas o código MÍNIMO necessário.\n"
        f"4. Quando houver muitos testes variados, você pode começar a generalizar a lógica.\n\n"
        f"⚠️ IMPORTANTE: Retorne APENAS o código Python puro, SEM blocos markdown.\n\n"
        f"Código da função {function_name}:"
    ))
    
    response = llm.invoke([system_msg, human_msg])
    raw_code = response.content.strip()
    
    
    ##logging.info("=" * 70)
    ##logging.info("🔍 RAW RESPONSE FROM DEVELOPER LLM:")
    ##logging.info(f"Length: {len(raw_code)} chars")
    ##logging.info(f"Lines: {len(raw_code.split(chr(10)))}")
    ##logging.info(f"Content:\n{raw_code}")
    ##logging.info("=" * 70)
    
    # Remove imports de teste
    clean_code = remove_test_imports(raw_code)
    
   
    ##logging.info("=" * 70)
    ##logging.info("🔍 FINAL CODE AFTER CLEANUP:")
    ##logging.info(f"Length: {len(clean_code)} chars")
    ##logging.info(f"Lines: {len(clean_code.split(chr(10)))}")
    ##logging.info(f"Content:\n{clean_code}")
    ##logging.info("=" * 70)
    
    if not clean_code.strip():
        raise ValueError("Developer gerou código vazio")
    
    # Valida se a função tem o nome correto
    if f"def {function_name}" not in clean_code:
        raise ValueError(
            f"Código não contém a função {function_name}.\n\n"
            f"RAW RESPONSE:\n{raw_code}\n\n"
            f"FINAL CODE:\n{clean_code}"
        )
    
    try:
        compile(clean_code, '<string>', 'exec')
    except SyntaxError as e:
        raise ValueError(f"Erro de sintaxe: {e}\n\nCódigo:\n{clean_code}")
    
    return clean_code