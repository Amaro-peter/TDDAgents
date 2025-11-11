import os
import re
import logging
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END, START
from app.agents.planner import generate_plan
from app.agents.tester import generate_test_for_sub_req
from app.agents.developer import generate_code_incremental
from app.agents.runner import run_pytest
from app.agents.reviewer import analyze_failures
from app.config import Config
from app.persistence import PersistenceStrategy, PersistenceFactory
import shutil

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class AgentState(TypedDict):
    specification: str
    function_name: str  # ⚠️ NOVO: nome da função principal
    plan: List[str]
    current_sub_req: str
    tests_code: str
    implementation_code: str
    feedback: str
    iteration: int
    plan_index: int
    status: str
    max_retries: int
    red_attempts: int

class TDDOrchestrator:
    def __init__(
        self, 
        task_key: str = "tdd_task",
        persistence: Optional[PersistenceStrategy] = None,
        max_retries: int = 10
    ):
        self.persistence = persistence or PersistenceFactory.create_persistence("redis")
        self.state_key = f"state:{task_key}"
        self.task_key = task_key
        self.max_retries = max_retries
        self.graph = self._build_graph()

    def _setup_workspace(self, clean: bool = True):
        """Configura o diretório de trabalho."""
        if clean and os.path.exists(Config.WORKSPACE_PATH):
            shutil.rmtree(Config.WORKSPACE_PATH)
        
        os.makedirs(Config.WORKSPACE_PATH, exist_ok=True)
        
        impl_path = os.path.join(Config.WORKSPACE_PATH, f"{Config.IMPLEMENTATION_MODULE}.py")
        if not os.path.exists(impl_path) or clean:
            with open(impl_path, "w", encoding="utf-8") as f:
                f.write("# Implementação incremental via TDD\n")
        
        test_path = os.path.join(Config.WORKSPACE_PATH, Config.TEST_FILE)
        if not os.path.exists(test_path) or clean:
            with open(test_path, "w", encoding="utf-8") as f:
                f.write("import pytest\n")
        
        logging.info(f"✅ Workspace '{Config.WORKSPACE_PATH}' configurado.")

    def _save_state(self, state: AgentState):
        """Persiste o estado atual."""
        self.persistence.save_state(self.task_key, state)
        current = state.get('plan_index', 0) + 1
        total = len(state.get('plan', []))
        logging.info(f"💾 Estado salvo: [{current}/{total}] {state.get('status')}")

    def _load_state(self) -> Optional[AgentState]:
        """Carrega o estado persistido."""
        state = self.persistence.load_state(self.task_key)
        if state:
            current = state.get('plan_index', 0) + 1
            total = len(state.get('plan', []))
            logging.info(f"📂 Estado carregado: [{current}/{total}] {state.get('status')}")
        return state

    def _restore_files_from_state(self, state: AgentState):
        """Restaura arquivos de teste e implementação do estado."""
        if state.get("tests_code"):
            test_path = os.path.join(Config.WORKSPACE_PATH, Config.TEST_FILE)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(state["tests_code"])
            logging.info(f"📋 Testes restaurados: {len(state['tests_code'])} chars")
        
        if state.get("implementation_code"):
            impl_path = os.path.join(Config.WORKSPACE_PATH, f"{Config.IMPLEMENTATION_MODULE}.py")
            with open(impl_path, "w", encoding="utf-8") as f:
                f.write(state["implementation_code"])
            logging.info(f"💻 Código restaurado: {len(state['implementation_code'])} chars")

    def _build_graph(self):
        
        def plan_task(state: AgentState) -> AgentState:
            logging.info("=" * 70)
            logging.info("🧠 FASE 1: PLANNER - Gerando plano de sub-requisitos TDD")
            logging.info("=" * 70)
            
            plan = generate_plan(state["specification"])
            
            if not plan:
                logging.error("❌ Planner falhou ao gerar o plano.")
                return {**state, "status": "plan_failed", "plan": []}
            
            logging.info(f"✅ Plano TDD gerado com {len(plan)} sub-requisitos:")
            for idx, step in enumerate(plan, 1):
                logging.info(f"  {idx}. {step}")
            
            new_state = {
                **state,
                "plan": plan,
                "plan_index": 0,
                "current_sub_req": plan[0],
                "iteration": 0,
                "status": "planning_complete"
            }
            self._save_state(new_state)
            return new_state

        def execute_tester(state: AgentState) -> AgentState:
            sub_req = state["current_sub_req"]
            plan_idx = state.get("plan_index", 0)
            total = len(state.get("plan", []))
            tests_code = state.get("tests_code", "")
            feedback = state.get("feedback", "")
            function_name = state.get("function_name", "process")  # ⚠️ NOVO
            
            logging.info("=" * 70)
            logging.info(f"🧪 FASE 2: TESTER - Sub-requisito [{plan_idx + 1}/{total}]")
            logging.info(f"📝 '{sub_req}'")
            logging.info(f"🎯 Função: {function_name}")  # ⚠️ NOVO
            logging.info(f"📊 Testes existentes: {len([l for l in tests_code.split('\\n') if 'def test_' in l])} funções")
            logging.info("=" * 70)
            
            new_tests_code = generate_test_for_sub_req(
                sub_requirement=sub_req,
                function_name=function_name,  # ⚠️ NOVO
                all_tests_code=tests_code,
                feedback=feedback
            )
            
            test_path = os.path.join(Config.WORKSPACE_PATH, Config.TEST_FILE)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(new_tests_code)
            
            num_tests = len([l for l in new_tests_code.split('\n') if 'def test_' in l])
            logging.info(f"✅ Total de testes agora: {num_tests}")
            
            new_state = {
                **state,
                "tests_code": new_tests_code,
                "feedback": "",
                "status": "test_written"
            }
            self._save_state(new_state)
            return new_state

        def execute_runner_red(state: AgentState) -> AgentState:
            sub_req = state["current_sub_req"]
            plan_idx = state.get("plan_index", 0)
            iteration = state.get("iteration", 0)
            max_retries = state.get("max_retries", self.max_retries)
            
            # ⚠️ NOVO: Contador específico para tentativas no RED
            red_attempts = state.get("red_attempts", 0)
            
            logging.info("=" * 70)
            logging.info(f"🔴 FASE 3: RUNNER RED - Verificando falha do NOVO teste")
            logging.info(f"🎯 Sub-requisito [{plan_idx + 1}]: '{sub_req}'")
            logging.info(f"🔄 Tentativa RED: {red_attempts + 1}/3")
            logging.info("=" * 70)
            
            output = run_pytest()
            logging.info(f"📊 Resultado pytest:\n{output}")
            
            has_failures = "failed" in output.lower() or "error" in output.lower()
            
            if has_failures:
                logging.info("✅ RED confirmado! O novo teste falha como esperado.")
                feedback = analyze_failures(
                    test_output=output,
                    specification=state["specification"],
                    sub_requirement=state["current_sub_req"],
                    iteration=iteration,
                    max_retries=max_retries,
                    current_code=state.get("implementation_code", ""),
                    test_code=state.get("tests_code", "")
                )
                new_state = {
                    **state, 
                    "status": "red_confirmed", 
                    "feedback": feedback,
                    "red_attempts": 0  # ⚠️ Reset contador RED
                }
            else:
                logging.warning("⚠️ ATENÇÃO: Nenhum teste falhou!")
                
                new_red_attempts = red_attempts + 1
                
                # ⚠️ PROTEÇÃO: Após 3 tentativas no RED sem falhas
                if new_red_attempts >= 3:
                    logging.warning("=" * 70)
                    logging.warning(f"⚠️ 3 TENTATIVAS NO RED SEM FALHAS DETECTADAS")
                    logging.warning("⚠️ Comportamento já implementado ou teste inadequado")
                    logging.warning("⚠️ Forçando progressão para DEVELOPER com feedback especial")
                    logging.warning("=" * 70)
                    
                    feedback = (
                        f"⚠️ ATENÇÃO ESPECIAL - RED NÃO CONFIRMADO:\n\n"
                        f"Após 3 tentativas, nenhum teste falhou no RED.\n"
                        f"Isso indica uma de duas situações:\n\n"
                        f"1. A implementação existente JÁ ATENDE este sub-requisito\n"
                        f"   → Neste caso, apenas verifique se não falta nada\n\n"
                        f"2. O teste NÃO ESTÁ VALIDANDO o comportamento correto\n"
                        f"   → Neste caso, implemente o comportamento esperado\n\n"
                        f"SUB-REQUISITO ATUAL:\n{sub_req}\n\n"
                        f"AÇÃO REQUERIDA:\n"
                        f"- Analise os testes cuidadosamente\n"
                        f"- Se falta implementação, adicione o código necessário\n"
                        f"- Se já está implementado, apenas valide que está correto\n"
                        f"- Mantenha o código existente que funciona"
                    )
                    
                    new_state = {
                        **state,
                        "status": "red_confirmed",  # ⚠️ Força progressão
                        "feedback": feedback,
                        "red_attempts": 0  # ⚠️ Reset contador
                    }
                    
                # Primeira ou segunda tentativa no primeiro sub-requisito
                elif plan_idx == 0 and new_red_attempts < 3:
                    feedback = (
                        f"⚠️ Tentativa {new_red_attempts}/3 no RED:\n\n"
                        f"O teste passou sem implementação.\n"
                        f"No TDD, o teste DEVE FALHAR antes da implementação.\n\n"
                        f"PROBLEMA COMUM:\n"
                        f"O teste pode estar validando um valor padrão (ex: False, None, 0)\n"
                        f"que a função já retorna sem implementação real.\n\n"
                        f"CORREÇÃO NECESSÁRIA:\n"
                        f"Ajuste o teste para validar comportamento ESPECÍFICO que ainda não existe.\n"
                        f"Exemplo: Se espera validação de senha forte, teste casos que exigem lógica real.\n\n"
                        f"SUB-REQUISITO: {sub_req}"
                    )
                    new_state = {
                        **state,
                        "status": "invalid_test",
                        "feedback": feedback,
                        "red_attempts": new_red_attempts
                    }
                    
                # Sub-requisitos posteriores ou já tentou corrigir
                else:
                    logging.info("⏭️ Implementação existente cobre este caso. Prosseguindo...")
                    feedback = (
                        f"Teste passou sem nova implementação (tentativa {new_red_attempts}).\n"
                        f"A implementação existente aparenta cobrir este comportamento.\n"
                        f"Verifique se há algo adicional a implementar ou se pode prosseguir."
                    )
                    new_state = {
                        **state,
                        "status": "red_confirmed",
                        "feedback": feedback,
                        "red_attempts": 0  # ⚠️ Reset contador
                    }
            
            self._save_state(new_state)
            return new_state
            
        def execute_developer(state: AgentState) -> AgentState:
            sub_req = state["current_sub_req"]
            iteration = state.get("iteration", 0) + 1
            plan_idx = state.get("plan_index", 0)
            total = len(state.get("plan", []))
            function_name = state.get("function_name", "process")  # ⚠️ NOVO
            
            logging.info("=" * 70)
            logging.info(f"💻 FASE 4: DEVELOPER - [{plan_idx + 1}/{total}] Iteração {iteration}")
            logging.info(f"🎯 Implementando: '{sub_req}'")
            logging.info(f"🎯 Função: {function_name}")  # ⚠️ NOVO
            logging.info(f"📦 Código anterior: {len(state.get('implementation_code', '').split('\\n'))} linhas")
            logging.info("=" * 70)
            
            tests_code = state["tests_code"]
            feedback = state["feedback"]
            previous_code = state.get("implementation_code", "")
            
            new_code = generate_code_incremental(
                test_code=tests_code,
                function_name=function_name,  # ⚠️ NOVO
                feedback=feedback,
                previous_code=previous_code
            )
            
            impl_path = os.path.join(Config.WORKSPACE_PATH, f"{Config.IMPLEMENTATION_MODULE}.py")
            with open(impl_path, "w", encoding="utf-8") as f:
                f.write(new_code)
            
            logging.info(f"✅ Código atualizado: {len(new_code.split('\\n'))} linhas")
            
            new_state = {
                **state,
                "implementation_code": new_code,
                "iteration": iteration,
                "feedback": "",
                "status": "code_written"
            }
            self._save_state(new_state)
            return new_state

        def execute_runner_green(state: AgentState) -> AgentState:
            sub_req = state["current_sub_req"]
            iteration = state.get("iteration", 0)
            max_retries = state.get("max_retries", self.max_retries)
            plan_idx = state.get("plan_index", 0)
            
            logging.info("=" * 70)
            logging.info(f"🟢 FASE 5: RUNNER GREEN - TODOS os testes devem passar!")
            logging.info(f"🔄 Iteração {iteration}/{max_retries}")
            logging.info(f"🎯 Sub-requisito [{plan_idx + 1}]: '{sub_req}'")
            logging.info("=" * 70)
            
            output = run_pytest()
            logging.info(f"📊 Resultado pytest:\n{output}")
            
            all_passed = "passed" in output.lower() and "failed" not in output.lower() and "error" not in output.lower()
            
            if all_passed:
                logging.info("=" * 70)
                logging.info("✅✅✅ GREEN COMPLETO! TODOS OS TESTES PASSARAM! ✅✅✅")
                logging.info(f"✅ Sub-requisito [{plan_idx + 1}] completado com sucesso!")
                logging.info("=" * 70)
                new_state = {**state, "status": "green_passed", "feedback": "", "iteration": 0}
            else:
                # ⚠️ NOVO: Após 5 iterações, volta ao Tester para revisar testes
                if iteration >= 5 and iteration < max_retries:
                    logging.warning("=" * 70)
                    logging.warning(f"⚠️ REVISÃO DE TESTES NECESSÁRIA!")
                    logging.warning(f"🔄 Tentativa {iteration}/{max_retries} - Falhas persistentes")
                    logging.warning("🔧 Voltando para o Tester revisar os testes...")
                    logging.warning("=" * 70)
                    
                    feedback = analyze_failures(
                        test_output=output,
                        specification=state["specification"],
                        sub_requirement=state["current_sub_req"],
                        iteration=iteration,
                        max_retries=max_retries,
                        current_code=state.get("implementation_code", ""),
                        test_code=state.get("tests_code", "")
                    )
                    
                    # Adiciona contexto específico para revisão de testes
                    test_review_feedback = (
                        f"⚠️ REVISÃO DE TESTES NECESSÁRIA (iteração {iteration}/{max_retries}):\n\n"
                        f"Após {iteration} tentativas, os testes ainda estão falhando.\n"
                        f"Isso pode indicar problemas nos próprios testes:\n\n"
                        f"POSSÍVEIS PROBLEMAS:\n"
                        f"1. Testes com expectativas contraditórias\n"
                        f"2. Testes que validam comportamento incorreto\n"
                        f"3. Testes com asserções muito rígidas ou incorretas\n"
                        f"4. Testes que não refletem a especificação real\n\n"
                        f"ANÁLISE DO REVIEWER:\n{feedback}\n\n"
                        f"AÇÃO REQUERIDA:\n"
                        f"Revise TODOS os testes relacionados a este sub-requisito.\n"
                        f"Corrija testes incorretos ou contraditórios.\n"
                        f"Garanta que os testes refletem o comportamento especificado."
                    )

                    logging.info("=" * 70)
                    logging.info("🔍 FEEDBACK PARA REVISÃO DE TESTES:")
                    logging.info("=" * 70)
                    for line in test_review_feedback.split('\n'):
                        logging.info(line)
                    logging.info("=" * 70)

                    new_state = {**state, "status": "test_review_needed", "feedback": test_review_feedback}
                    
                elif iteration >= max_retries:
                    logging.error("=" * 70)
                    logging.error(f"❌ FALHA CRÍTICA: Excedeu {max_retries} tentativas!")
                    logging.error(f"❌ Sub-requisito [{plan_idx + 1}] NÃO pôde ser completado.")
                    logging.error("=" * 70)
                    
                    feedback = analyze_failures(
                        test_output=output,
                        specification=state["specification"],
                        sub_requirement=state["current_sub_req"],
                        iteration=iteration,
                        max_retries=max_retries,
                        current_code=state.get("implementation_code", ""),
                        test_code=state.get("tests_code", "")
                    )

                    logging.info("=" * 70)
                    logging.info("🔍 FEEDBACK ESTRUTURADO DO REVIEWER:")
                    logging.info("=" * 70)
                    for line in feedback.split('\n'):
                        logging.info(line)
                    logging.info("=" * 70)

                    new_state = {**state, "status": "max_retries_exceeded", "feedback": feedback}
                else:
                    logging.warning("=" * 70)
                    logging.warning(f"❌ GREEN FALHOU! Alguns testes não passaram.")
                    logging.warning(f"🔄 Tentativa {iteration}/{max_retries}")
                    logging.warning("🔧 Voltando para o Developer com feedback...")
                    logging.warning("=" * 70)
                    
                    feedback = analyze_failures(
                        test_output=output,
                        specification=state["specification"],
                        sub_requirement=state["current_sub_req"],
                        iteration=iteration,
                        max_retries=max_retries,
                        current_code=state.get("implementation_code", ""),
                        test_code=state.get("tests_code", "")
                    )

                    logging.info("=" * 70)
                    logging.info("🔍 FEEDBACK ESTRUTURADO DO REVIEWER:")
                    logging.info("=" * 70)
                    for line in feedback.split('\n'):
                        logging.info(line)
                    logging.info("=" * 70)

                    new_state = {**state, "status": "green_failed", "feedback": feedback}
            
            self._save_state(new_state)
            return new_state


        def execute_reviewer(state: AgentState) -> AgentState:
            logging.info("=" * 70)
            logging.info("♻️  FASE 6: REVIEWER - Avaliando progresso")
            logging.info("=" * 70)
            
            current_index = state["plan_index"]
            next_index = current_index + 1
            plan = state["plan"]
            total = len(plan)
            
            logging.info(f"✅ Sub-requisito [{current_index + 1}/{total}] COMPLETO!")
            
            if next_index < total:
                next_req = plan[next_index]
                logging.info(f"⏭️  Avançando para o próximo sub-requisito [{next_index + 1}/{total}]")
                logging.info(f"📝 Próximo: '{next_req}'")
                logging.info("=" * 70)
                
                new_state = {
                    **state,
                    "status": "next_req",
                    "plan_index": next_index,
                    "current_sub_req": next_req,
                    "feedback": "",
                    "iteration": 0
                }
            else:
                logging.info("=" * 70)
                logging.info("🎉 🎉 🎉 PLANO COMPLETO! 🎉 🎉 🎉")
                logging.info(f"✅ Todos os {total} sub-requisitos foram implementados!")
                logging.info("✅ Todos os testes passam cumulativamente!")
                logging.info("=" * 70)
                new_state = {**state, "status": "plan_complete"}
            
            self._save_state(new_state)
            return new_state

        # ==================== ROTAS DO GRAFO ====================
        
        def route_after_planner(state: AgentState) -> str:
            status = state.get("status")
            has_plan = state.get("plan") and len(state.get("plan", [])) > 0
            
            if status == "planning_complete" and has_plan:
                logging.info("🔀 Rota: PLANNER → TESTER")
                return "execute_tester"
            else:
                logging.error("🔀 Rota: PLANNER → END (sem plano)")
                return END

        def route_after_tester(state: AgentState) -> str:
            logging.info("🔀 Rota: TESTER → RUNNER_RED")
            return "execute_runner_red"
        
        def route_after_red(state: AgentState) -> str:
            status = state.get("status")
            
            if status == "red_confirmed":
                logging.info("🔀 Rota: RUNNER_RED → DEVELOPER (implementar)")
                return "execute_developer"
            elif status == "invalid_test":
                logging.info("🔀 Rota: RUNNER_RED → TESTER (corrigir teste)")
                return "execute_tester"
            else:
                logging.error(f"🔀 Rota: RUNNER_RED → END (status: {status})")
                return END
        
        def route_after_developer(state: AgentState) -> str:
            logging.info("🔀 Rota: DEVELOPER → RUNNER_GREEN")
            return "execute_runner_green"
        
        def route_after_green(state: AgentState) -> str:
            status = state.get("status")
            
            if status == "green_passed":
                logging.info("🔀 Rota: RUNNER_GREEN → REVIEWER (testes passaram!)")
                return "execute_reviewer"
            elif status == "test_review_needed":
                logging.info("🔀 Rota: RUNNER_GREEN → TESTER (revisar testes)")
                return "execute_tester"
            elif status == "green_failed":
                logging.info("🔀 Rota: RUNNER_GREEN → DEVELOPER (corrigir código)")
                return "execute_developer"
            elif status == "max_retries_exceeded":
                logging.error("🔀 Rota: RUNNER_GREEN → END (excedeu tentativas)")
                return END
            else:
                logging.error(f"🔀 Rota: RUNNER_GREEN → END (status: {status})")
                return END

        def route_after_reviewer(state: AgentState) -> str:
            status = state.get("status")
            
            if status == "next_req":
                logging.info("🔀 Rota: REVIEWER → TESTER (próximo sub-requisito)")
                return "execute_tester"
            elif status == "plan_complete":
                logging.info("🔀 Rota: REVIEWER → END (plano completo!)")
                return END
            else:
                logging.error(f"🔀 Rota: REVIEWER → END (status: {status})")
                return END

        # ==================== CONSTRUÇÃO DO GRAFO ====================
        
        workflow = StateGraph(AgentState)
        
        workflow.add_node("plan_task", plan_task)
        workflow.add_node("execute_tester", execute_tester)
        workflow.add_node("execute_runner_red", execute_runner_red)
        workflow.add_node("execute_developer", execute_developer)
        workflow.add_node("execute_runner_green", execute_runner_green)
        workflow.add_node("execute_reviewer", execute_reviewer)
        
        workflow.add_edge(START, "plan_task")
        
        workflow.add_conditional_edges("plan_task", route_after_planner)
        workflow.add_conditional_edges("execute_tester", route_after_tester)
        workflow.add_conditional_edges("execute_runner_red", route_after_red)
        workflow.add_conditional_edges("execute_developer", route_after_developer)
        workflow.add_conditional_edges("execute_runner_green", route_after_green)
        workflow.add_conditional_edges("execute_reviewer", route_after_reviewer)
        
        return workflow.compile()

    def run(self, specification: str = None, resume: bool = False, function_name: str = None) -> Dict[str, Any]:
        """
        Executa o workflow TDD incremental e cumulativo.
        
        Args:
            specification: Especificação completa do projeto (obrigatória se resume=False)
            resume: Se True, retoma do estado salvo
            function_name: Nome explícito da função (opcional, extraído da spec se None)
        
        Returns:
            Estado final do workflow
        """
        logging.info("🚀 " * 25)
        
        if resume:
            logging.info("🔄 RETOMANDO WORKFLOW TDD INCREMENTAL DO ESTADO SALVO")
            logging.info("🚀 " * 25)
            
            saved_state = self._load_state()
            
            if not saved_state:
                logging.error("❌ Nenhum estado salvo encontrado.")
                return {"status": "error", "error_message": "No saved state found"}
            
            self._setup_workspace(clean=False)
            self._restore_files_from_state(saved_state)
            
            initial_state = saved_state
            
        else:
            logging.info("🚀 INICIANDO WORKFLOW TDD INCREMENTAL E CUMULATIVO")
            logging.info("🚀 " * 25)
            
            if not specification:
                logging.error("❌ Especificação é obrigatória para novo workflow.")
                return {"status": "error", "error_message": "Specification required"}
            
            self._setup_workspace(clean=True)
            
            logging.info(f"🎯 Função principal detectada: {function_name}")
            
            initial_state: AgentState = {
                "specification": specification,
                "function_name": function_name,  # ⚠️ NOVO
                "plan": [],
                "current_sub_req": "",
                "tests_code": "",
                "implementation_code": "",
                "feedback": "",
                "iteration": 0,
                "plan_index": 0,
                "status": "starting",
                "max_retries": self.max_retries,
                "red_attempts": 0 
            }
        
        final_state = None
        
        try:
            config = {"recursion_limit": 1000}
            final_state = self.graph.invoke(initial_state, config=config)
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no workflow: {e}")
            import traceback
            logging.error(traceback.format_exc())
            final_state = {**initial_state, "status": "error", "error_message": str(e)}
            self._save_state(final_state)
        
        logging.info("\n" + "=" * 70)
        logging.info("📊 RESULTADO FINAL DO WORKFLOW TDD INCREMENTAL")
        logging.info("=" * 70)
        logging.info(f"✅ Status: {final_state.get('status', 'unknown')}")
        completed = final_state.get('plan_index', 0)
        total = len(final_state.get('plan', []))
        if final_state.get('status') == 'plan_complete':
            completed = total
        logging.info(f"🔢 Sub-requisitos completos: {completed}/{total}")
        logging.info(f"📄 Implementação: {Config.WORKSPACE_PATH}/{Config.IMPLEMENTATION_MODULE}.py")
        logging.info(f"📋 Testes: {Config.WORKSPACE_PATH}/{Config.TEST_FILE}")
        logging.info("=" * 70)
        
        return final_state
    
    def continue_from_sub_req(self, sub_req_index: int) -> Dict[str, Any]:
        saved_state = self._load_state()
        
        if not saved_state:
            return {"status": "error", "error_message": "No saved state"}
        
        plan = saved_state.get("plan", [])
        if sub_req_index >= len(plan):
            return {"status": "error", "error_message": f"Invalid index {sub_req_index}"}
        
        saved_state["plan_index"] = sub_req_index
        saved_state["current_sub_req"] = plan[sub_req_index]
        saved_state["status"] = "next_req"
        saved_state["iteration"] = 0
        saved_state["feedback"] = ""
        
        self._save_state(saved_state)
        
        return self.run(resume=True)