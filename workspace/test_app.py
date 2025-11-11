import pytest
from app_code import roman_to_int

def test_single_roman_numerals():
    # Testando a conversão de numerais romanos simples
    assert roman_to_int('I') == 1  # 'I' deve ser convertido para 1
    assert roman_to_int('V') == 5  # 'V' deve ser convertido para 5
    assert roman_to_int('X') == 10  # 'X' deve ser convertido para 10
    assert roman_to_int('L') == 50  # 'L' deve ser convertido para 50
    assert roman_to_int('C') == 100  # 'C' deve ser convertido para 100
    assert roman_to_int('D') == 500  # 'D' deve ser convertido para 500
    assert roman_to_int('M') == 1000  # 'M' deve ser convertido para 1000

def test_roman_numerals_with_subtraction():
    # Testando a conversão de numerais romanos que utilizam subtração
    assert roman_to_int('IV') == 4  # 'IV' deve ser convertido para 4 (5 - 1)
    assert roman_to_int('IX') == 9  # 'IX' deve ser convertido para 9 (10 - 1)
    assert roman_to_int('XL') == 40  # 'XL' deve ser convertido para 40 (50 - 10)
    assert roman_to_int('XC') == 90  # 'XC' deve ser convertido para 90 (100 - 10)
    assert roman_to_int('CD') == 400  # 'CD' deve ser convertido para 400 (500 - 100)
    assert roman_to_int('CM') == 900  # 'CM' deve ser convertido para 900 (1000 - 100)

def test_complex_roman_numerals():
    # Testando a conversão de numerais romanos complexos
    assert roman_to_int('MCMXCIV') == 1994  # 'MCMXCIV' deve ser convertido para 1994 (1000 + 900 + 90 + 4)

def test_empty_input():
    # Entrada vazia deve retornar 0, que é o valor padrão correto para conversão
    assert roman_to_int('') == 0

def test_invalid_roman_numerals():
    # Testando a conversão de uma entrada inválida (não romano)
    assert roman_to_int('ABC') == 0  # 'ABC' não é um numeral romano válido, deve retornar 0

def test_repeated_invalid_symbols():
    # Testando a conversão de símbolos romanos inválidos repetidos
    assert roman_to_int('IIII') == 0  # 'IIII' não é um numeral romano válido, deve retornar 0

def test_invalid_order_of_symbols():
    # Testando a conversão de símbolos romanos em ordem inválida
    assert roman_to_int('IL') == 0  # 'IL' não é uma representação válida, deve retornar 0

def test_lowercase_roman_numerals():
    # Testando a conversão de numerais romanos em letras minúsculas
    assert roman_to_int('i') == 1  # 'i' deve ser convertido para 1
    assert roman_to_int('v') == 5  # 'v' deve ser convertido para 5
    assert roman_to_int('x') == 10  # 'x' deve ser convertido para 10
    assert roman_to_int('l') == 50  # 'l' deve ser convertido para 50
    assert roman_to_int('c') == 100  # 'c' deve ser convertido para 100
    assert roman_to_int('d') == 500  # 'd' deve ser convertido para 500
    assert roman_to_int('m') == 1000  # 'm' deve ser convertido para 1000