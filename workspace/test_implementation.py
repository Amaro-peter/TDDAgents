import pytest
from implementation import fizzbuzz

def test_fizzbuzz_multiplo_de_3():
    assert fizzbuzz(3) == 'Fizz'
    assert fizzbuzz(6) == 'Fizz'
    assert fizzbuzz(9) == 'Fizz'

def test_fizzbuzz_multiplo_de_5():
    assert fizzbuzz(5) == 'Buzz'
    assert fizzbuzz(10) == 'Buzz'
    assert fizzbuzz(20) == 'Buzz'

def test_fizzbuzz_multiplo_de_15():
    assert fizzbuzz(15) == 'FizzBuzz'
    assert fizzbuzz(30) == 'FizzBuzz'
    assert fizzbuzz(45) == 'FizzBuzz'

def test_fizzbuzz_nao_multiplo_de_3_ou_5():
    assert fizzbuzz(1) == '1'
    assert fizzbuzz(2) == '2'
    assert fizzbuzz(4) == '4'
    assert fizzbuzz(7) == '7'
    assert fizzbuzz(8) == '8'

def test_fizzbuzz_zero():
    assert fizzbuzz(0) == 'FizzBuzz'

def test_fizzbuzz_negativos():
    assert fizzbuzz(-3) == 'Fizz'
    assert fizzbuzz(-5) == 'Buzz'
    assert fizzbuzz(-15) == 'FizzBuzz'
    assert fizzbuzz(-1) == '-1'