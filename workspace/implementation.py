def is_palindrome(s):
    """Verifica se a string fornecida é um palíndromo, ignorando espaços, maiúsculas e caracteres especiais."""
    # Remove espaços e converte para minúsculas
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    return cleaned == cleaned[::-1]