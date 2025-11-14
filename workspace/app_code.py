def roman_to_int(s):
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    prev_value = 0
    count = {key: 0 for key in values.keys()}
    
    for char in s.upper():
        if char not in values:
            return 'WRONG'
        count[char] += 1
        if count[char] > 3 and char in ['I', 'X', 'C', 'M']:
            return 'WRONG'
        if count[char] > 1 and char in ['V', 'L', 'D']:
            return 'WRONG'
    
    for i in range(len(s)):
        current_value = values[s[i].upper()]
        if i > 0 and current_value > values[s[i - 1].upper()]:
            total += current_value - 2 * values[s[i - 1].upper()]
        else:
            total += current_value
    
    if 'IC' in s or 'IL' in s or 'VX' in s:
        return 'WRONG'
    
    return total if total > 0 else 0