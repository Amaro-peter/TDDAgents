import pytest
from implementation import is_palindrome

def test_palindrome_com_texto_simples():
    assert is_palindrome("arara") == True

def test_palindrome_com_espacos():
    assert is_palindrome("a man a plan a canal panama") == True

def test_palindrome_com_maiusculas():
    assert is_palindrome("Aibohphobia") == True

def test_palindrome_com_texto_nao_palindromo():
    assert is_palindrome("hello") == False

def test_palindrome_com_texto_vazio():
    assert is_palindrome("") == True

def test_palindrome_com_espacos_apenas():
    assert is_palindrome("   ") == True

def test_palindrome_com_caracteres_especiais():
    assert is_palindrome("Able , was I saw eLba") == True

def test_palindrome_com_texto_misto():
    assert is_palindrome("No 'x' in Nixon") == True

def test_palindrome_com_texto_misto_nao_palindromo():
    assert is_palindrome("This is not a palindrome") == False