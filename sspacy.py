import spacy

nlp = spacy.load('en_core_web_lg')

words = 'semiconductor material'

tokens = nlp(words)

print('similarity: ', tokens[0].similarity(tokens[1]))