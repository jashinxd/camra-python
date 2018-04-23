import requests

def getSynonym(tag):
    synonyms = []
    url = 'https://api.datamuse.com/words?rel_syn='+tag
    results = requests.get(url).json()
    for result in results:
        if (int(result["score"]) > 1000):
            synonyms.append(str(result["word"]))
    return synonyms

print(getSynonym("happy"))
