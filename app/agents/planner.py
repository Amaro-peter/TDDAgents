from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List, Dict, Any
from app.config import Config
import json
import logging

def generate_plan(specification: str) -> List[str]:
    """Gera um plano de TDD (lista de sub-requisitos) a partir da especificação."""
    llm = ChatOpenAI(model=Config.MODEL, temperature=0.1)
    
    messages = [
        SystemMessage(content=(
            "Você é o Planejador (Planner), um especialista em Test Driven Development (TDD). "
            "Sua função é receber um requisito de alto nível e dividi-lo em um plano de TDD passo a passo. "
            "Cada passo representa um pequeno sub-requisito incremental e segue o ciclo clássico do TDD: "
            "\n1. O Tester escreve o próximo teste mais simples para o sub-requisito. "
            "\n2. O Developer implementa o código mínimo necessário para passar no teste. "
            "\n3. O Executor executa todos os testes. "
            "\n4. Se os testes passarem, o Reviewer analisa o código. "
            "\n5. Repita para o próximo sub-requisito."
            "\n\nREGRAS DE FORMATAÇÃO:"
            "\n1. Retorne **apenas** um JSON válido. Não inclua nenhuma explicação ou texto fora do JSON."
            "\n2. O JSON deve conter a chave 'tdd_plan' com uma lista de etapas (objetos JSON)."
            "\n3. Cada etapa deve conter:"
            "\n   - 'sub_requirement': descrição curta e específica do objetivo do teste (ex: 'Testar soma de números positivos')."
            "\n   - 'actions': lista com as instruções para Tester, Developer, Executor e Reviewer, seguindo o ciclo TDD."
            "\n\nFormato esperado:"
            "\n{\n  'tdd_plan': [\n    {\n      'sub_requirement': '...',\n      'actions': [\n        'Tester: ...',\n        'Developer: ...',\n        'Executor: ...',\n        'Reviewer: ...'\n      ]\n    }\n  ]\n}"
        )),
        HumanMessage(content=(
            f"📝 Requisito Principal:\n{specification}\n\n"
            "Gere o plano de TDD detalhado e sequencial para este requisito."
        ))
    ]

    response = llm.invoke(messages)
    content = response.content.strip()
    
    try:
        # Tenta corrigir a resposta se o LLM incluiu markdown
        if content.startswith('```json'):
            content = content.strip('```json').strip()
        elif content.startswith('```'):
            content = content.strip('```').strip()
            
        data = json.loads(content)
        
        # FIX: Usar a chave correta 'tdd_plan' conforme especificado no prompt
        tdd_plan = data.get('tdd_plan', [])
        
        # Extrair apenas os 'sub_requirement' de cada etapa
        sub_requirements = [step['sub_requirement'] for step in tdd_plan if 'sub_requirement' in step]
        
        return sub_requirements
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logging.error(f"❌ Erro ao decodificar JSON do Planner: {e}")
        logging.error(f"Conteúdo do LLM: {content}")
        # Retorna um plano de falha se houver erro
        return ["Falha ao gerar o plano, escreva um teste que valide a falha de implementação."]