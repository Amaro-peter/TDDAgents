from app.orchestrator import TDDOrchestrator

if __name__ == "__main__":
    orchestrator = TDDOrchestrator()
    
    # Exemplo 1: FizzBuzz
    spec_fizzbuzz = (
        "Implemente a função fizzbuzz(n) que retorna 'Fizz' se n for múltiplo de 3, "
        "'Buzz' se for múltiplo de 5, 'FizzBuzz' se for múltiplo de ambos, "
        "ou o número como string caso contrário."
    )
    
    # Exemplo 2: Calculadora
    spec_calculator = (
        "Implemente uma classe Calculator com métodos add(a, b), subtract(a, b), "
        "multiply(a, b) e divide(a, b). O método divide deve lançar ValueError se b for zero."
    )
    
    # Exemplo 3: Palíndromo
    spec_palindrome = (
        "Implemente a função is_palindrome(text) que retorna True se o texto for "
        "um palíndromo (ignorando espaços e maiúsculas/minúsculas), False caso contrário."
    )
    
    # Exemplo 4: Ordenação
    spec_sort = (
        "Implemente a função bubble_sort(arr) que ordena uma lista de números "
        "usando o algoritmo bubble sort e retorna a lista ordenada."
    )
    
    # ESCOLHA QUALQUER ESPECIFICAÇÃO AQUI:
    orchestrator.run(spec_fizzbuzz)

