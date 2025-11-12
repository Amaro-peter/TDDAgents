from app.orchestrator import TDDOrchestrator

if __name__ == "__main__":
    orchestrator = TDDOrchestrator()
    
    # === ESPECIFICAÇÕES ===
    
    spec_roman_to_int = (
        "Implemente a função roman_to_int que recebe uma string "
        "representando um numeral romano (ex: 'IX', 'MCMXCIV') e retorna o valor inteiro "
        "correspondente. A função deve suportar os símbolos I, V, X, L, C, D, M "
        "e aplicar corretamente a regra de subtração (ex: IV = 4, CM = 900).\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. Apenas os símbolos I, V, X, L, C, D, M são válidos.\n"
        "2. Repetições máximas:\n"
        "   - I, X, C, M podem repetir até 3 vezes consecutivas (III ✅, IIII ❌)\n"
        "   - V, L, D NÃO podem repetir NUNCA (VV ❌, LL ❌, DD ❌)\n"
        "3. Ordem válida: símbolos maiores devem vir antes dos menores, exceto em subtrações.\n"
        "4. Subtrações válidas: apenas I antes de V ou X, X antes de L ou C, C antes de D ou M.\n"
        "5. Para entradas inválidas, retornar 'not a valid roman number.\n"
        "6. String vazia deve retornar 0.\n"
        "7. Desconsiderar maiúsculas ou minúsculas (converter tudo para uppercase).\n\n"

    spec_is_prime = (
        "Implemente a função is_prime que recebe um número inteiro n e retorna True se ele for um número primo, "
        "ou False caso contrário.\n\n"
        
        "⚙️ DEFINIÇÃO:\n"
        "Um número primo é aquele maior que 1 que possui exatamente dois divisores positivos distintos: "
        "1 e ele mesmo. Exemplos: 2, 3, 5, 7, 11.\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. O parâmetro n deve ser do tipo inteiro (int). Caso contrário, retornar 'invalid input'.\n"
        "2. Se n for menor ou igual a 1, retornar False (números ≤ 1 não são primos por definição).\n"
        "3. A verificação de divisores deve ser feita apenas até a raiz quadrada de n, "
        "incluindo otimização para pular números pares após o 2.\n"
        "4. A função deve retornar True se n for primo e False caso contrário.\n"
        "5. A função deve lidar corretamente com números negativos e zero.\n\n"
        
        "💡 EXEMPLOS:\n"
        ">>> is_prime(2)\n"
        "True\n\n"
        ">>> is_prime(9)\n"
        "False\n\n"
        ">>> is_prime(17)\n"
        "True\n\n"
        ">>> is_prime(1)\n"
        "False\n\n"
        ">>> is_prime('10')\n"
        "'invalid input'\n"
    )

    spec_sort_numbers = (
        "Implemente a função sort_numbers que recebe uma lista de números inteiros e retorna uma nova lista "
        "com os mesmos elementos em ordem crescente.\n\n"
        
        "⚙️ DEFINIÇÃO:\n"
        "A ordenação deve ser feita de forma que o menor número apareça primeiro e o maior por último. "
        "A função deve preservar todos os elementos originais, sem removê-los ou alterá-los, apenas reordenando.\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. O parâmetro de entrada deve ser uma lista (list) contendo apenas valores inteiros (int).\n"
        "   - Caso a entrada não seja uma lista, ou contenha elementos não inteiros, retornar 'invalid input'.\n"
        "2. A função deve retornar uma **nova lista**, sem modificar a lista original (sem efeitos colaterais).\n"
        "3. É permitido o uso de métodos ou funções internas de ordenação do Python (ex: sorted, list.sort).\n"
        "4. Implementações manuais de ordenação (ex: bubble sort, insertion sort) também são aceitas, "
        "desde que mantenham a complexidade esperada.\n"
        "5. A função deve lidar corretamente com listas vazias (retornar []).\n"
        "6. Números negativos devem ser ordenados corretamente antes dos positivos.\n\n"
        
        "💡 EXEMPLOS:\n"
        ">>> sort_numbers([3, 1, 4, 1, 5, 9])\n"
        "[1, 1, 3, 4, 5, 9]\n\n"
        ">>> sort_numbers([-2, 0, 10, -5])\n"
        "[-5, -2, 0, 10]\n\n"
        ">>> sort_numbers([])\n"
        "[]\n\n"
        ">>> sort_numbers([3, 'a', 2])\n"
        "'invalid input'\n"
    )
    
    spec_fizzbuzz = (
        "Implemente a função fizzbuzz que recebe um número inteiro positivo n "
        "e retorna uma lista de strings representando os números de 1 até n, aplicando as seguintes regras:\n\n"
        
        "⚙️ REGRAS:\n"
        "1. Para cada número i de 1 até n:\n"
        "   - Se i for divisível por 3 e por 5, adicione 'FizzBuzz' à lista.\n"
        "   - Se i for divisível apenas por 3, adicione 'Fizz' à lista.\n"
        "   - Se i for divisível apenas por 5, adicione 'Buzz' à lista.\n"
        "   - Caso contrário, adicione o próprio número (como string).\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. O parâmetro n deve ser um número inteiro positivo (> 0).\n"
        "2. Se n <= 0 ou não for um número inteiro, retornar 'invalid input'.\n"
        "3. O retorno deve ser uma lista de strings (por exemplo: ['1', '2', 'Fizz', ...]).\n"
        "4. Não usar bibliotecas externas.\n"
        "5. A função deve ter complexidade O(n).\n\n"
        
        "💡 EXEMPLOS:\n"
        ">>> fizzbuzz(5)\n"
        "['1', '2', 'Fizz', '4', 'Buzz']\n\n"
        ">>> fizzbuzz(15)\n"
        "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']\n"
    )

    spec_palindrome = (
        "Implemente a função is_palindrome que recebe uma string e retorna True se ela for um palíndromo "
        "(ou seja, se pode ser lida da mesma forma de trás para frente), ou False caso contrário.\n\n"
        
        "⚙️ DEFINIÇÃO:\n"
        "Uma string é considerada palíndromo se, após remover espaços, pontuações e ignorar diferenças "
        "de maiúsculas e minúsculas, sua sequência de caracteres for igual à sua inversa.\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. A função deve ignorar espaços (' '), vírgulas, pontos, exclamações, interrogações e outros sinais de pontuação.\n"
        "2. A comparação não deve ser sensível a maiúsculas/minúsculas (ex: 'A' == 'a').\n"
        "3. Caracteres acentuados (como 'á', 'ã', 'ç') devem ser considerados normalmente — ou seja, "
        "não há necessidade de removê-los.\n"
        "4. Se a string for vazia, retornar True (string vazia é considerada palíndromo por definição).\n"
        "5. Não utilizar bibliotecas externas.\n\n"
        
        "💡 EXEMPLOS:\n"
        ">>> is_palindrome('Ame a ema')\n"
        "True\n\n"
        ">>> is_palindrome('Socorram-me, subi no ônibus em Marrocos!')\n"
        "True\n\n"
        ">>> is_palindrome('OpenAI')\n"
        "False\n"
    )

    spec_password_validator = (
        "Implemente a função is_strong_password que recebe uma string representando uma senha "
        "e retorna True se ela for considerada forte, ou False caso contrário.\n\n"
        
        "⚙️ DEFINIÇÃO:\n"
        "Uma senha é considerada forte se atender a critérios mínimos de segurança, garantindo "
        "complexidade e resistência contra ataques de força bruta.\n\n"
        
        "⚠️ REQUISITOS:\n"
        "1. A senha deve conter pelo menos 8 caracteres.\n"
        "2. Deve incluir pelo menos uma letra maiúscula (A–Z).\n"
        "3. Deve incluir pelo menos uma letra minúscula (a–z).\n"
        "4. Deve conter pelo menos um dígito numérico (0–9).\n"
        "5. Deve conter pelo menos um caractere especial (ex: !, @, #, $, %, &, *).\n"
        "6. Não pode conter espaços em branco.\n"
        "7. A função deve retornar False se a entrada for vazia ou não for uma string.\n\n"

        "💡 EXEMPLOS:\n"
        ">>> is_strong_password('Abc123!@#')\n"
        "True\n\n"
        ">>> is_strong_password('senha123')\n"
        "False\n\n"
        ">>> is_strong_password('A1!')\n"
        "False\n"
    )
    
    final_state = orchestrator.run(
        specification=spec_roman_to_int,
        function_name="roman_to_int",
    )
