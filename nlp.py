import nltk
nltk.download('stopwords')
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

query = "Intel semiconductor supplier in India"
query2 = "Semiconductor for Apple from India"
query3 = "who is the best supplier of Apple  for  raw material of semicondctor ?"

""" NOUN     : NN
    ADJECTIVE: JJ
"""

is_adj = lambda pos: pos[:2] == 'JJ'
is_noun = lambda pos: pos[:2] == 'NN'
is_verb = lambda pos: pos[:2] == "VB"

tokenizer = RegexpTokenizer(r'\w+')
tokenized = tokenizer.tokenize(query3)

filtered_tokenized = [word for word in tokenized if word not in stopwords.words('english')]

print(filtered_tokenized)
nouns = [word for (word, pos) in nltk.pos_tag(filtered_tokenized) if is_noun(pos)]
print(nouns)
adj = [word for (word, pos) in nltk.pos_tag(filtered_tokenized) if is_adj(pos)]
print(adj)
verb = [word for (word, pos) in nltk.pos_tag(filtered_tokenized) if is_verb(pos)]
print(verb)