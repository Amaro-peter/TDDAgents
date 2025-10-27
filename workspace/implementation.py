def is_palindrome(s: str) -> bool:
    """Verifica se a string fornecida é um palíndromo, ignorando espaços, pontuação e capitalização."""
    # Remove espaços e pontuação, e converte para minúsculas
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    # Verifica se a string limpa é igual à sua reversa
    return cleaned == cleaned[::-1]