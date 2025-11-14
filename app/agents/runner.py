import subprocess
import re  # Adicione esta importação
import logging # Adicione esta importação
from app.config import Config

def run_pytest() -> str:
    """Executa pytest no arquivo de testes."""
    test_file = Config.TEST_FILE
    
    try:
        result = subprocess.run(
            ["pytest", f"workspace/{test_file}", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Combina stdout e stderr para análise completa
        output = result.stdout
        if result.stderr:
            output += f"\n\nERROS:\n{result.stderr}"
        
        return output.strip()
    except subprocess.TimeoutExpired:
        return "❌ Erro: execução de testes expirou (timeout de 30s)."
    except FileNotFoundError:
        return "❌ Erro: pytest não está instalado. Execute: pip install pytest"
    except Exception as e:
        return f"❌ Erro ao executar testes: {str(e)}"

def get_test_coverage() -> float:
    """Executa pytest-cov e retorna o percentual de cobertura."""
    try:
        cmd = [
            "pytest",
            f"workspace/{Config.TEST_FILE}",
            f"--cov=workspace.{Config.IMPLEMENTATION_MODULE}",
            "--cov-report=term-missing",
            "--no-cov-on-fail"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="."
        )
        
        output = result.stdout + result.stderr
        
        # Formato: "TOTAL    100   0   100%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+([\d\.]+)%", output)
        
        if match:
            coverage = float(match.group(1))
            logging.info(f"📊 Cobertura de Teste: {coverage}%")
            return coverage
        
        # Formato alternativo
        match = re.search(rf"{Config.IMPLEMENTATION_MODULE}\.py\s+\d+\s+\d+\s+([\d\.]+)%", output)
        if match:
            coverage = float(match.group(1))
            logging.info(f"📊 Cobertura de Teste: {coverage}%")
            return coverage
            
        logging.warning(f"⚠️ Não foi possível extrair cobertura:\n{output}")
        return 0.0
            
    except Exception as e:
        logging.error(f"❌ Erro ao executar get_test_coverage: {str(e)}")
        return 0.0

def get_mutation_score() -> float:
    """Executa mutmut e retorna o score de mutação."""
    try:
        # Limpa cache anterior
        subprocess.run(["mutmut", "clear-cache"], capture_output=True, timeout=10)
        
        # Usa configuração do pyproject.toml - sem argumentos extras
        cmd = [
            "mutmut",
            "run",
            "--no-progress"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd="."
        )
        
        output = result.stdout + result.stderr
        
        # Busca no output
        killed = 0
        survived = 0
        total = 0
        
        killed_match = re.search(r"(?:Killed|killed):\s*(\d+)", output)
        survived_match = re.search(r"(?:Survived|survived):\s*(\d+)", output)
        timeout_match = re.search(r"(?:Timeout|timeout):\s*(\d+)", output)
        
        if killed_match:
            killed = int(killed_match.group(1))
        if survived_match:
            survived = int(survived_match.group(1))
        if timeout_match:
            timeout = int(timeout_match.group(1))
            total = killed + survived + timeout
        else:
            total = killed + survived
        
        if total > 0:
            score = (killed / total) * 100
            logging.info(f"🧬 Score de Mutação: {score:.1f}% ({killed}/{total} mutantes mortos)")
            return round(score, 1)
        
        logging.warning(f"⚠️ Não foi possível extrair score de mutação:\n{output}")
        return 0.0

    except subprocess.TimeoutExpired:
        logging.error("❌ Mutmut timeout - operação muito demorada")
        return 0.0
    except Exception as e:
        logging.error(f"❌ Erro ao executar get_mutation_score: {str(e)}")
        return 0.0