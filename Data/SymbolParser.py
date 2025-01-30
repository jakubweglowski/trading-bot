import json

def parse_symbols():
    with open('Data/spolki.json') as f:
        data = json.load(f)
    
    symbols = {}
    for key in data.keys():
        symbols[key] = [key+'.US' for key in data[key].keys()]
    
    return symbols