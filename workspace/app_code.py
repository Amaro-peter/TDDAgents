def roman_to_int(s):
    if not s:
        return 0
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    prev_value = 0
    count = 1
    for i in range(len(s)):
        char = s[i].upper()
        if char not in values:
            return 0
        current_value = values[char]
        
        if i > 0 and current_value > prev_value:
            if (prev_value == 1 and current_value in [5, 10]) or \
               (prev_value == 10 and current_value in [50, 100]) or \
               (prev_value == 100 and current_value in [500, 1000]):
                total += current_value - 2 * prev_value
            else:
                return 0
        else:
            total += current_value
        
        if i > 0 and char == s[i - 1]:
            count += 1
            if (char in ['V', 'L', 'D'] and count > 1) or (char in ['I', 'X', 'C', 'M'] and count > 3):
                return 0
        else:
            count = 1
        
        prev_value = current_value
    
    return total