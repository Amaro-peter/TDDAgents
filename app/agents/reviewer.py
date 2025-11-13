import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import Config

def extract_relevant_spec_context(
    specification: str,
    sub_requirement: str,
    test_output: str,
    current_code: str
) -> str:
    """
    Usa LLM para extrair APENAS a parte relevante da especificação.
    Sem heurísticas frágeis - deixa a LLM decidir o que é relevante.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # Modelo rápido e barato
    
    system_msg = SystemMessage(content=(
        "Você é um assistente que extrai APENAS as informações relevantes de uma especificação.\n\n"
        "TAREFA:\n"
        "Dado:\n"
        "1. Uma especificação completa\n"
        "2. Um sub-requisito atual\n"
        "3. Saída de um teste falhado\n"
        "4. Código atual\n\n"
        "Extraia APENAS as regras/requisitos da especificação que são DIRETAMENTE RELEVANTES "
        "para resolver a falha do teste.\n\n"
        "REGRAS:\n"
        "- Se a falha envolve validação, extraia as regras de validação\n"
        "- Se a falha envolve cálculo, extraia as regras de cálculo\n"
        "- NÃO inclua informações irrelevantes\n"
        "- Seja CIRÚRGICO - apenas o necessário\n"
        "- Se nada é relevante, retorne: 'Nenhum contexto específico da especificação é necessário.'\n\n"
        "FORMATO DE RESPOSTA:\n"
        "Retorne apenas as regras extraídas, sem comentários ou explicações extras."
    ))
    
    human_msg = HumanMessage(content=(
        f"📋 ESPECIFICAÇÃO COMPLETA:\n{specification}\n\n"
        f"🎯 SUB-REQUISITO ATUAL:\n{sub_requirement}\n\n"
        f"📊 SAÍDA DO TESTE (falha):\n{test_output}\n\n"
        f"💻 CÓDIGO ATUAL:\n```python\n{current_code}\n```\n\n"
        f"Extraia APENAS as regras da especificação relevantes para corrigir esta falha."
    ))
    
    response = llm.invoke([system_msg, human_msg])
    return response.content.strip()


def analyze_failures(
    test_output: str,
    specification: str,
    sub_requirement: str,
    iteration: int = 0,
    max_retries: int = 3,
    current_code: str = "",
    test_code: str = ""
) -> str:
    """
    Analisa falhas com feedback GRADUAL usando LLM para filtragem.
    """
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.3)

    # --- Extrai métricas do pytest ---
    passed_match = re.search(r'(\d+)\s+passed', test_output)
    failed_match = re.search(r'(\d+)\s+failed', test_output)
    
    passed_count = int(passed_match.group(1)) if passed_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0
    
    total = passed_count + failed_count
    
    # --- ESTRATÉGIA DE FEEDBACK GRADUAL ---
    if iteration == 0:
        feedback_mode = "MINIMAL"
        spec_context = ""  # Sem contexto de spec
        
    elif iteration == 1:
        feedback_mode = "CONTEXTUAL"
        # ⚠️ LLM extrai contexto relevante
        spec_context = extract_relevant_spec_context(
            specification=specification,
            sub_requirement=sub_requirement,
            test_output=test_output,
            current_code=current_code
        )
        
    else:  # iteration >= 2
        feedback_mode = "ARCHITECTURAL"
        spec_context = specification  # Spec completa para análise profunda

    # --- SYSTEM MESSAGE (instruções de comportamento) ---
    system_msg = SystemMessage(content=(
        f"Você é um REVISOR SÊNIOR de TDD.\n\n"
        f"🎯 MODO ATUAL: {feedback_mode} (iteração {iteration}/{max_retries})\n\n"
        f"📋 PRINCÍPIO DE FEEDBACK GRADUAL:\n\n"
        f"MINIMAL (iteração 0):\n"
        f"- Identifique APENAS o que está falhando\n"
        f"- NÃO explique regras da especificação\n"
        f"- NÃO sugira implementações completas\n"
        f"- Formato: 'O teste espera X mas recebe Y. Analise o motivo.'\n\n"
        f"CONTEXTUAL (iteração 1):\n"
        f"- Você receberá APENAS a parte RELEVANTE da especificação\n"
        f"- Explique POR QUE o teste espera aquele resultado\n"
        f"- Dê dica de ONDE implementar (não o código completo)\n"
        f"- Formato: 'Segundo a spec: [regra]. Adicione validação em [local].'\n\n"
        f"ARCHITECTURAL (iteração 2+):\n"
        f"- Você receberá a especificação COMPLETA\n"
        f"- Analise se há conflito de requisitos\n"
        f"- Sugira mudança de abordagem se necessário\n"
        f"- Considere redesign da arquitetura\n\n"
        f"⚠️ REGRA CRÍTICA EM TODOS OS MODOS:\n"
        f"NUNCA sugira implementar recursos além do teste atual.\n"
        f"Foque APENAS em fazer o teste falhado passar.\n"
        f"O TDD é incremental - uma falha por vez."
    ))

    # --- HUMAN MESSAGE (contexto específico por modo) ---
    if feedback_mode == "MINIMAL":
        human_msg = HumanMessage(content=(
            f"🎯 SUB-REQUISITO: {sub_requirement}\n\n"
            f"📊 SITUAÇÃO:\n"
            f"- Testes passados: {passed_count}\n"
            f"- Testes falhados: {failed_count}\n\n"
            f"📊 SAÍDA PYTEST:\n```\n{test_output}\n```\n\n"
            f"TAREFA (MINIMAL):\n"
            f"Identifique o erro de forma direta e objetiva.\n"
            f"NÃO explique regras ou dê soluções completas.\n"
            f"Apenas: 'O teste espera X mas retorna Y.'"
        ))
        
    elif feedback_mode == "CONTEXTUAL":
        human_msg = HumanMessage(content=(
            f"🎯 SUB-REQUISITO: {sub_requirement}\n\n"
            f"📊 SITUAÇÃO:\n"
            f"- Testes passados: {passed_count}\n"
            f"- Testes falhados: {failed_count}\n"
            f"- Tentativa: {iteration + 1}\n\n"
            f"📋 CONTEXTO RELEVANTE DA ESPECIFICAÇÃO:\n{spec_context}\n\n"
            f"💻 CÓDIGO ATUAL:\n```python\n{current_code}\n```\n\n"
            f"📊 SAÍDA PYTEST:\n```\n{test_output}\n```\n\n"
            f"TAREFA (CONTEXTUAL):\n"
            f"Use o contexto da especificação para explicar POR QUE o teste falha.\n"
            f"Dê dica de ONDE implementar a correção (não o código completo).\n"
            f"Mantenha o foco APENAS no teste atual."
        ))
        
    else:  # ARCHITECTURAL
        human_msg = HumanMessage(content=(
            f"🎯 SUB-REQUISITO: {sub_requirement}\n\n"
            f"📊 SITUAÇÃO CRÍTICA:\n"
            f"- Testes passados: {passed_count}\n"
            f"- Testes falhados: {failed_count}\n"
            f"- Tentativa: {iteration + 1}/{max_retries}\n"
            f"- ⚠️ Múltiplas falhas no mesmo teste\n\n"
            f"📋 ESPECIFICAÇÃO COMPLETA:\n{specification}\n\n"
            f"💻 CÓDIGO ATUAL:\n```python\n{current_code}\n```\n\n"
            f"📋 TODOS OS TESTES:\n```python\n{test_code}\n```\n\n"
            f"📊 SAÍDA PYTEST:\n```\n{test_output}\n```\n\n"
            f"TAREFA (ARCHITECTURAL):\n"
            f"1. Analise se há conflito entre testes ou requisitos\n"
            f"2. Identifique se a arquitetura atual pode resolver o problema\n"
            f"3. Sugira redesign se necessário\n"
            f"4. Se não houver conflito, identifique o erro de implementação específico"
        ))

    response = llm.invoke([system_msg, human_msg])
    return response.content.strip()