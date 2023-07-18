
def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip('{}')
 
    # split the string into key-value pairs
    pairs = string.split(',')
 
    # use a dictionary comprehension to createm
    # the dictionary, converting the values to
    # integers and removing the quotes from the keys
    return {key[1:-2]: int(value) for key, value in (pair.split(':') for pair in pairs)}