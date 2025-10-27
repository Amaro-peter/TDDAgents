import os
import time
import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from app.agents.tester import generate_tests
from app.agents.developer import generate_code
from app.agents.runner import run_pytest
from app.agents.reviewer import analyze_failures
from app.config import Config
from app.redis_state import RedisState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class AgentState(TypedDict):
    specification: str
    tests: str
    code: str
    feedback: str
    status: str
    iteration: int
    test_phase: str  # 'red' or 'green'

class TDDOrchestrator:
    def __init__(self, task_key: str = "tdd_task"):
        self.redis = RedisState()
        self.state_key = f"state:{task_key}"
        self.graph = self._build_graph()
        os.makedirs(Config.WORKSPACE_PATH, exist_ok=True)

    def _build_graph(self):
        def create_tests(state: AgentState) -> AgentState:
            logging.info("=" * 60)
            logging.info("📝 FASE 1 (TDD): Gerando testes")
            logging.info("=" * 60)
            
            tests = generate_tests(state["specification"])
            
            # Validação rigorosa
            if not tests or len(tests.strip()) < 50:
                logging.error("❌ Testes inválidos ou muito curtos")
                raise ValueError("Falha ao gerar testes válidos")
            
            # Verificar se contém imports corretos
            module_name = Config.IMPLEMENTATION_MODULE
            if f"from {module_name} import" not in tests and f"import {module_name}" not in tests:
                logging.warning(f"⚠️ Testes não importam de '{module_name}', corrigindo...")
                tests = f"from {module_name} import *\n\n" + tests
            
            # Verificar se não há implementação
            if "def " in tests and "def test_" not in tests:
                logging.warning("⚠️ Testes parecem conter implementação, verificando...")
                non_test_funcs = []
                for line in tests.split('\n'):
                    stripped = line.strip()
                    if (stripped.startswith('def ') and 
                        'def test_' not in stripped and 
                        '@pytest.fixture' not in tests[max(0, tests.find(line)-100):tests.find(line)]):
                        non_test_funcs.append(stripped)
                
                if len(non_test_funcs) > 0:
                    logging.error(f"❌ Testes contêm implementação: {non_test_funcs}")
                    logging.error("Regenerando testes...")
                    tests = generate_tests(state["specification"])
            
            test_path = os.path.join(Config.WORKSPACE_PATH, Config.TEST_FILE)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(tests)
            
            logging.info(f"✅ Testes salvos em: {Config.TEST_FILE}")
            logging.info(f"📄 Preview:\n{tests[:400]}...")
            
            # Marcar que estamos na fase RED (sem implementação ainda)
            return {"tests": tests, "test_phase": "red", "code": ""}

        def execute_tests_red(state: AgentState) -> AgentState:
            """Executa testes na fase RED - DEVE falhar pois não há implementação"""
            logging.info("=" * 60)
            logging.info("🔴 FASE 2 (TDD - RED): Executando testes SEM implementação")
            logging.info("=" * 60)
            logging.info("⚠️  Esperado: testes devem FALHAR (não há código ainda)")
            
            # Criar arquivo vazio de implementação para testes falharem corretamente
            impl_path = os.path.join(Config.WORKSPACE_PATH, f"{Config.IMPLEMENTATION_MODULE}.py")
            with open(impl_path, "w", encoding="utf-8") as f:
                f.write("# Arquivo vazio - implementação virá na fase GREEN\n")
            
            output = run_pytest()
            logging.info(f"📊 Resultado pytest:\n{output}")
            
            # Verificar se falhou (como esperado no TDD)
            has_failures = "failed" in output.lower() or "error" in output.lower()
            
            if has_failures:
                logging.info("=" * 60)
                logging.info("✅ RED confirmado: Testes falharam conforme esperado!")
                logging.info("=" * 60)
                # Analisar falhas para passar contexto ao Developer
                feedback = analyze_failures(output)
                return {"status": "red_confirmed", "feedback": feedback, "test_phase": "red"}
            else:
                logging.error("=" * 60)
                logging.error("⚠️  PROBLEMA: Testes passaram sem implementação!")
                logging.error("⚠️  Isso indica que os testes podem estar incorretos.")
                logging.error("=" * 60)
                return {"status": "invalid_tests", "feedback": "Testes passam sem implementação", "test_phase": "red"}

        def create_code(state: AgentState) -> AgentState:
            iteration = state.get("iteration", 1)
            logging.info("=" * 60)
            if iteration == 1:
                logging.info("💻 FASE 3 (TDD - GREEN): Gerando código inicial")
            else:
                logging.info(f"💻 FASE 5 (TDD - REFACTOR): Refatorando código (iteração {iteration})")
            logging.info("=" * 60)
            
            tests = state.get("tests", "")
            feedback = state.get("feedback", "")
            prev_code = state.get("code", "")
            
            code = generate_code(tests, feedback, prev_code)
            
            # Validação
            if not code or len(code.strip()) < 20:
                logging.error("❌ Código inválido ou muito curto")
                raise ValueError("Falha ao gerar código válido")
            
            # Verificar se não contém testes
            if "def test_" in code or "import pytest" in code:
                logging.warning("⚠️ Código contém testes, removendo...")
                filtered_lines = []
                for line in code.split('\n'):
                    if ("def test_" not in line and 
                        "import pytest" not in line and 
                        ("assert " not in line or "# assert" in line)):
                        filtered_lines.append(line)
                code = "\n".join(filtered_lines)
            
            impl_path = os.path.join(Config.WORKSPACE_PATH, f"{Config.IMPLEMENTATION_MODULE}.py")
            with open(impl_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            logging.info(f"✅ Código salvo em: {Config.IMPLEMENTATION_MODULE}.py")
            logging.info(f"📄 Preview:\n{code[:400]}...")
            return {"code": code, "test_phase": "green"}

        def execute_tests_green(state: AgentState) -> AgentState:
            """Executa testes na fase GREEN - deve passar com a implementação"""
            iteration = state.get("iteration", 1)
            logging.info("=" * 60)
            if iteration == 1:
                logging.info("🧪 FASE 4 (TDD - GREEN): Executando testes COM implementação")
            else:
                logging.info(f"🧪 FASE 6 (TDD - REFACTOR CHECK): Verificando refatoração (iteração {iteration})")
            logging.info("=" * 60)
            logging.info("✅ Esperado: testes devem PASSAR agora")
            
            output = run_pytest()
            logging.info(f"📊 Resultado pytest:\n{output}")
            
            # Verificar se passou
            has_passed_tests = "passed" in output.lower()
            has_failures = "failed" in output.lower() or "error" in output.lower()
            
            # Sucesso = tem testes passando E não tem falhas
            if has_passed_tests and not has_failures:
                logging.info("=" * 60)
                logging.info("✅ ✅ ✅ GREEN: Todos os testes passaram! ✅ ✅ ✅")
                logging.info("=" * 60)
                logging.info("🎉 Ciclo TDD completo: RED → GREEN → REFACTOR")
                return {"status": "passed", "feedback": ""}
            else:
                logging.warning("=" * 60)
                logging.warning("❌ GREEN falhou: Testes ainda não passam")
                logging.warning("=" * 60)
                feedback = analyze_failures(output)
                logging.info(f"📋 Feedback do Reviewer:\n{feedback}")
                return {"status": "failed", "feedback": feedback}

        def route_after_tests(state: AgentState) -> str:
            """Decide o próximo passo após criar os testes"""
            return "run_red_phase"

        def route_after_red(state: AgentState) -> str:
            """Decide o próximo passo após fase RED"""
            status = state.get("status")
            
            if status == "red_confirmed":
                # RED confirmado, pode gerar código
                return "generate_code"
            elif status == "invalid_tests":
                # Testes inválidos (passaram sem código)
                logging.error("Testes inválidos detectados. Encerrando.")
                return "end"
            else:
                return "end"

        def route_after_green(state: AgentState) -> str:
            """Decide o próximo passo após fase GREEN"""
            status = state.get("status")
            
            if status == "passed":
                return "end"
            
            iteration = state.get("iteration", 0)
            if iteration >= Config.MAX_ITERATIONS:
                logging.error("=" * 60)
                logging.error("⚠️ ⚠️ ⚠️ LIMITE DE ITERAÇÕES ATINGIDO ⚠️ ⚠️ ⚠️")
                logging.error("=" * 60)
                return "end"
            
            # Precisa refatorar
            return "refactor"

        # Build graph
        workflow = StateGraph(AgentState)
        
        # Adicionar nós
        workflow.add_node("create_tests", create_tests)
        workflow.add_node("run_red_phase", execute_tests_red)
        workflow.add_node("generate_code", create_code)
        workflow.add_node("run_green_phase", execute_tests_green)
        
        # Fluxo TDD: Tests → RED → Code → GREEN → (REFACTOR se falhar)
        workflow.add_edge(START, "create_tests")
        
        workflow.add_conditional_edges(
            "create_tests",
            route_after_tests,
            {
                "run_red_phase": "run_red_phase"
            }
        )
        
        workflow.add_conditional_edges(
            "run_red_phase",
            route_after_red,
            {
                "generate_code": "generate_code",
                "end": END
            }
        )
        
        workflow.add_edge("generate_code", "run_green_phase")
        
        workflow.add_conditional_edges(
            "run_green_phase",
            route_after_green,
            {
                "end": END,
                "refactor": "generate_code"
            }
        )
        
        return workflow.compile()

    def run(self, specification: str):
        logging.info("🚀 " * 20)
        logging.info("🚀 INICIANDO WORKFLOW TDD COMPLETO")
        logging.info("🚀 " * 20)
        logging.info(f"📋 Especificação:\n{specification}\n")
        logging.info("📖 Fluxo TDD: RED (falha) → GREEN (passa) → REFACTOR (melhora)")
        
        # Load or initialize state
        saved_state = self.redis.load(self.state_key)
        
        initial_state: AgentState = {
            "specification": specification,
            "tests": saved_state.get("tests", ""),
            "code": saved_state.get("code", ""),
            "feedback": saved_state.get("feedback", ""),
            "status": saved_state.get("status", ""),
            "iteration": 0,
            "test_phase": "red"
        }
        
        for i in range(Config.MAX_ITERATIONS):
            initial_state["iteration"] = i + 1
            
            # Execute graph
            final_state = None
            for state in self.graph.stream(initial_state):
                final_state = state
                if final_state:
                    node_name = list(state.keys())[0]
                    current_state = state[node_name]
                    self.redis.save(self.state_key, current_state)
            
            # Update state
            if final_state:
                node_name = list(final_state.keys())[0]
                initial_state.update(final_state[node_name])

            if initial_state.get("status") == "passed":
                break
            else:
                if i < Config.MAX_ITERATIONS - 1:
                    logging.info(f"⏳ Aguardando 2s antes da iteração {i + 2}...")
                    time.sleep(2)

        logging.info("\n" + "=" * 60)
        logging.info("📊 RESULTADO FINAL DO TDD")
        logging.info("=" * 60)
        logging.info(f"✅ Status: {initial_state.get('status', 'unknown')}")
        logging.info(f"🔢 Iterações: {initial_state.get('iteration', 0)}")
        logging.info(f"📄 Implementação: {Config.WORKSPACE_PATH}/{Config.IMPLEMENTATION_MODULE}.py")
        logging.info(f"📄 Testes: {Config.WORKSPACE_PATH}/{Config.TEST_FILE}")
        
        if initial_state.get("status") == "passed":
            logging.info("🎉 Ciclo TDD concluído com sucesso!")
            logging.info("   ✓ RED: Testes falharam inicialmente")
            logging.info("   ✓ GREEN: Implementação passou todos os testes")
            logging.info("   ✓ REFACTOR: Código refinado (se necessário)")
        
        logging.info("=" * 60)
        
        return initial_state