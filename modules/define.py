#Written by Jake Schultz
#TODO Add more lang support, limit number of results returned
from PyDictionary import PyDictionary


def Define(word):
    return_value = []
    dic = PyDictionary()
    words = dic.meaning(word)
    if 'Verb' in words:
        return_value.append(words['Verb'][0])
    if 'Adjective' in words:
        return_value.append(words['Adjective'][0])
    if 'Noun' in words:
        return_value.append(words['Noun'][0])
        
    return return_value

