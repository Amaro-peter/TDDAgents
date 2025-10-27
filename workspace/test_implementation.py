import pytest
from implementation import is_palindrome

def test_palindrome_normal_cases():
    assert is_palindrome("A man a plan a canal Panama") == True
    assert is_palindrome("Madam Im Adam") == True
    assert is_palindrome("Racecar") == True
    assert is_palindrome("No lemon no melon") == True

def test_palindrome_edge_cases():
    assert is_palindrome("") == True  # Empty string is a palindrome
    assert is_palindrome(" ") == True  # Single space is a palindrome
    assert is_palindrome("  ") == True  # Multiple spaces are a palindrome

def test_palindrome_non_palindrome_cases():
    assert is_palindrome("Hello World") == False
    assert is_palindrome("Python") == False
    assert is_palindrome("This is not a palindrome") == False

def test_palindrome_special_characters():
    assert is_palindrome("A man, a plan, a canal, Panama!") == True
    assert is_palindrome("Was it a car or a cat I saw?") == True
    assert is_palindrome("No 'x' in Nixon") == True
    assert is_palindrome("Not a palindrome!") == False