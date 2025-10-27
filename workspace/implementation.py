def fizzbuzz(n):
    """Retorna 'Fizz' se n é múltiplo de 3, 'Buzz' se n é múltiplo de 5, 
    'FizzBuzz' se n é múltiplo de 15, ou o próprio número como string se não for múltiplo de 3 ou 5."""
    if n % 15 == 0:
        return 'FizzBuzz'
    elif n % 3 == 0:
        return 'Fizz'
    elif n % 5 == 0:
        return 'Buzz'
    else:
        return str(n)