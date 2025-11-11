import re
import ast
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config

def extract_code(text: str) -> str:
    """Extrai código Python de blocos markdown ou retorna o texto como está."""
    match = re.search(r'```(?:python)?\s*(.*?)\s*```', text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def generate_test_for_sub_req(
    sub_requirement: str,
    function_name: str,
    all_tests_code: str = "",
    feedback: str = ""
) -> str:
    """Gera um novo teste pytest para o sub-requisito ou REVISA testes existentes."""
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.2)
    module_name = Config.IMPLEMENTATION_MODULE

    # ⚠️ DETECTA SE É MODO DE REVISÃO DE TESTES
    is_test_review = "REVISÃO DE TESTES NECESSÁRIA" in feedback
    
    context = ""
    if all_tests_code:
        num_tests = len([l for l in all_tests_code.split('\n') if 'def test_' in l])
        context += f"TESTES EXISTENTES ({num_tests} funções):\n```python\n{all_tests_code}\n```\n\n"
    if feedback:
        context += f"FEEDBACK DO REVISOR:\n{feedback}\n\n"

    # ==================== MODO REVISÃO DE TESTES ====================
    if is_test_review:
        system_msg = SystemMessage(content=(
            f"Você é especialista em Test-Driven Development (TDD) e está em MODO DE REVISÃO DE TESTES.\n\n"
            f"⚠️⚠️⚠️ MODO CRÍTICO: REVISÃO E CORREÇÃO DE TESTES ⚠️⚠️⚠️\n\n"
            f"A função testada se chama: **{function_name}**\n\n"
            f"📋 CONTEXTO:\n"
            f"Após 5+ tentativas de implementação, os testes ainda falham.\n"
            f"Isso indica problemas NOS PRÓPRIOS TESTES, não necessariamente na implementação.\n\n"
            f"🔍 PROBLEMAS COMUNS EM TESTES QUE VOCÊ DEVE CORRIGIR:\n"
            f"1. ❌ Testes contraditórios:\n"
            f"   - test_empty() espera 0\n"
            f"   - test_empty_string() espera '' (para a mesma entrada!)\n\n"
            f"2. ❌ Asserções incorretas:\n"
            f"   - assert {function_name}('abc') == 'ERRADO'  # Expectativa errada\n\n"
            f"3. ❌ Testes muito rígidos:\n"
            f"   - Validam implementação específica ao invés de comportamento\n\n"
            f"4. ❌ Testes que não refletem a especificação:\n"
            f"   - Validam requisitos inventados\n\n"
            f"5. ❌ Lógica de teste errada:\n"
            f"   - Loops incorretos, condições erradas nos testes\n\n"
            f"🎯 AÇÕES OBRIGATÓRIAS:\n"
            f"1. Analise TODOS os testes existentes criticamente\n"
            f"2. Identifique testes com expectativas CONTRADITÓRIAS\n"
            f"3. Corrija asserções incorretas\n"
            f"4. Simplifique testes muito complexos\n"
            f"5. Remova testes que validam comportamento errado\n"
            f"6. Garanta consistência entre todos os testes\n"
            f"7. Certifique-se de que os testes refletem a especificação real\n\n"
            f"📝 EXEMPLO DE CORREÇÃO:\n"
            f"```python\n"
            f"# ❌ ANTES (testes contraditórios):\n"
            f"def test_empty_string():\n"
            f"    assert {function_name}('') == 0  # Expectativa A\n\n"
            f"def test_empty():\n"
            f"    assert {function_name}('') == ''  # Expectativa B (contradiz A!)\n\n"
            f"# ✅ DEPOIS (consistente):\n"
            f"def test_empty_string():\n"
            f"    # String vazia retorna 0 (comportamento correto)\n"
            f"    assert {function_name}('') == 0\n"
            f"```\n\n"
            f"📝 EXEMPLO 2 - ASSERÇÃO INCORRETA:\n"
            f"```python\n"
            f"# ❌ ANTES (asserção errada):\n"
            f"def test_basic():\n"
            f"    assert {function_name}('abc') == 'xyz'  # Expectativa errada!\n\n"
            f"# ✅ DEPOIS (corrigido):\n"
            f"def test_basic():\n"
            f"    # Segundo especificação: 'abc' deve retornar 6\n"
            f"    assert {function_name}('abc') == 6\n"
            f"```\n\n"
            f"⚠️ FORMATO DE RESPOSTA:\n"
            f"Retorne TODOS os testes (corrigidos + novos se necessário).\n"
            f"Use comentários para explicar as correções feitas:\n"
            f"# CORRIGIDO: [breve explicação]\n\n"
            f"🚨 IMPORTANTE:\n"
            f"- SEMPRE use: from {module_name} import {function_name}\n"
            f"- SEMPRE chame: {function_name}() nos testes\n"
            f"- NÃO invente outro nome de função\n"
            f"- FOQUE em corrigir, não em adicionar testes novos (a menos que seja necessário)"
        ))

        human_msg = HumanMessage(content=(
            f"🎯 FUNÇÃO: {function_name}\n"
            f"📝 SUB-REQUISITO ATUAL: {sub_requirement}\n\n"
            f"{context}\n\n"
            f"🔧 TAREFA DE REVISÃO:\n"
            f"1. Analise TODOS os testes existentes acima\n"
            f"2. Identifique e CORRIJA:\n"
            f"   - Testes contraditórios\n"
            f"   - Asserções incorretas\n"
            f"   - Expectativas que não refletem a especificação\n"
            f"3. Garanta que todos os testes sejam CONSISTENTES entre si\n"
            f"4. Adicione comentários explicando as correções\n"
            f"5. Se necessário, adicione o teste para o sub-requisito atual\n\n"
            f"⚠️ FOCO: Corrigir testes problemáticos, não reescrever tudo."
        ))

    # ==================== MODO NORMAL (ADICIONAR TESTE) ====================
    else:
        system_msg = SystemMessage(content=(
            f"Você é especialista em Test-Driven Development (TDD) e escreve testes pytest incrementais.\n\n"
            f"⚠️⚠️⚠️ ATENÇÃO CRÍTICA ⚠️⚠️⚠️\n"
            f"A função que você DEVE testar se chama: **{function_name}**\n"
            f"NÃO invente outro nome! Use EXATAMENTE: {function_name}\n\n"
            f"📋 REGRAS FUNDAMENTAIS:\n"
            f"1. Mantenha TODOS os testes existentes intactos.\n"
            f"2. Adicione APENAS UM novo teste por sub-requisito.\n"
            f"3. SEMPRE use o import: from {module_name} import {function_name}\n"
            f"4. SEMPRE chame a função {function_name}() nos testes.\n"
            f"5. Use nomes descritivos: test_something_specific\n\n"
            f"🚫 PROIBIÇÕES CRÍTICAS:\n"
            f"6. NÃO crie testes que falhem de propósito:\n"
            f"   ❌ assert {function_name}('') == 'WRONG'  # PROIBIDO!\n"
            f"   ✅ assert {function_name}('') == expected_correct_result\n\n"
            f"7. NÃO crie testes contraditórios:\n"
            f"   ❌ test_a: assert {function_name}('x') == 5\n"
            f"   ❌ test_b: assert {function_name}('x') == 6  # CONTRADIZ test_a!\n"
            f"   ✅ Todos os testes para mesma entrada devem ter mesma expectativa\n\n"
            f"8. NÃO crie testes com expectativas incorretas:\n"
            f"   ❌ assert {function_name}('abc') != expected_result  # Teste negativo inútil\n"
            f"   ✅ assert {function_name}('abc') == expected_result\n\n"
            f"📝 EXEMPLOS CORRETOS:\n"
            f"```python\n"
            f"import pytest\n"
            f"from {module_name} import {function_name}\n\n"
            f"def test_empty_input():\n"
            f"    # Entrada vazia deve retornar valor padrão correto\n"
            f"    assert {function_name}('') == 0\n\n"
            f"def test_basic_case():\n"
            f"    # Caso simples, comportamento esperado segundo especificação\n"
            f"    assert {function_name}('abc') == 6\n"
            f"```\n\n"
            f"❌ EXEMPLOS INCORRETOS (NÃO FAZER):\n"
            f"```python\n"
            f"# TESTE CONTRADITÓRIO - PROIBIDO\n"
            f"def test_empty_a():\n"
            f"    assert {function_name}('') == 0\n"
            f"def test_empty_b():\n"
            f"    assert {function_name}('') == ''  # CONTRADIZ test_empty_a!\n\n"
            f"# TESTE COM EXPECTATIVA ERRADA - PROIBIDO\n"
            f"def test_wrong_expectation():\n"
            f"    assert {function_name}('abc') == 'ERRADO'  # Expectativa inventada!\n"
            f"```\n\n"
            f"⚠️ LEMBRE-SE: Use {function_name}, garanta consistência, valide comportamento correto!"
        ))

        human_msg = HumanMessage(content=(
            f"🎯 FUNÇÃO: {function_name}\n"
            f"📝 SUB-REQUISITO: {sub_requirement}\n\n"
            f"{context}\n\n"
            f"✅ INSTRUÇÕES:\n"
            f"1. Mantenha TODOS os testes existentes\n"
            f"2. Adicione UM novo teste para o sub-requisito atual\n"
            f"3. Certifique-se de que o novo teste:\n"
            f"   - NÃO contradiz testes existentes\n"
            f"   - Tem expectativa CORRETA segundo a especificação\n"
            f"   - Usa {function_name}() corretamente\n"
            f"4. Use comentários para explicar o teste\n\n"
            f"⚠️ CRÍTICO: Consistência e correção são essenciais!"
        ))

    # ==================== INVOCA LLM ====================
    response = llm.invoke([system_msg, human_msg])
    clean_code = extract_code(response.content.strip())

    if not clean_code:
        raise ValueError("LLM retornou código vazio")

    if "import pytest" not in clean_code:
        clean_code = "import pytest\n" + clean_code

    # ⚠️ VALIDAÇÃO: Verifica se a função correta está sendo usada
    if f"from {module_name} import {function_name}" not in clean_code:
        raise ValueError(
            f"Código de teste não importa a função {function_name} corretamente.\n"
            f"Código gerado:\n{clean_code}"
        )

    return clean_code