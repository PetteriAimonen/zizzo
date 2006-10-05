alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def ord(char):
    try:
        return alphabet.index(char)
    except ValueError:
        raise ValueError, "Only characters 0-9 and A-Z are allowed."

def chr(value):
    value = value % len(alphabet)
    return alphabet[value]

def split(string):
    '''Split a string to parts at any character other than 0-9 and A-Z'''
    result = []
    
    while string:
        while string and string[0] not in alphabet:
            string = string[1:]
        
        block = ""
        while string and string[0] in alphabet:
            block += string[0]
            string = string[1:]
        
        if block != "":
            result.append(block)
        
    
    return result

if __name__ == "__main__":
    print "Unit testing"
    
    assert split('1,2 3-4') == ['1', '2', '3', '4']
    
    print "OK"
