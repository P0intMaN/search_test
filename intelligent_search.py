import pandas as pd
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from sematch.semantic.similarity import WordNetSimilarity
import spacy

# global inits
wns = WordNetSimilarity()
nlp = spacy.load('en_core_web_lg')

# errors
def something_is_wrong():
    print("Must Search couldn't find what you are looking for. Refine your query.")
    return ["Must Search couldn't find what you are looking for. Refine your query."]

def no_results():
    print("No Results.")
    return ["No Results."]

# read csv
df = pd.read_csv('raw_training_data.csv')

# data pre-processing
def make_data_case_insensitive(df):
    df = df.applymap(lambda s: s.lower() if type(s) == str else s)
    return df
    

def clean_date(df):
    df['company_founded'] = pd.DatetimeIndex(df['company_founded']).year
    df['customer_founded'] = pd.DatetimeIndex(df['customer_founded']).year
    return df


def remove_na(df):
    df = df.dropna(axis=0)
    return df


def correct_revenue(list):
    corrected_revenue_list = []

    for i in list:
        if i not in corrected_revenue_list:
            corrected_revenue_list.append(i)
    
    # print(corrected_revenue_list)

    for i in list:
        if i == "design and manufacture of frequency control devices including- packaged quartz":
            list[list.index(i)] = 10**6
        elif i == "more.\xa0":
            list[list.index(i)] = 10**6

data_preprocess_steps = [clean_date, make_data_case_insensitive]

for step in data_preprocess_steps:
    df = step(df)

# print(wns.word_similarity('nice', 'good'))

# preparing reference tables (degenerating pandas)
company_list = [company for company in df['company_name']]
customer_list = [customer for customer in df['customer_name']]

company_segment = [seg for seg in df['company_high_tech_market_segment']]
customer_segment = [seg for seg in df['customer_high_tech_market_segment']]

company_revenue = [rev for rev in df['company_estimated_revenue_range']]
customer_revenue = [rev for rev in df['customer_estimated_revenue_range']]

company_year = [yr for yr in df['company_founded']]
customer_year = [yr for yr in df['customer_founded']]

company_country = [cntry for cntry in df['company_country']]
customer_country = [cntry for cntry in df['customer_country']]

company_investors = [inv for inv in df['company_number_of_investors']]
customer_investors = [inv for inv in df['customer_number_of_investors']]

# for i in range(len(customer_list)):
#     if customer_list[i] == "intel":
#         print(company_segment[i], company_revenue[i], company_year[i], company_country[i], company_list[i])

# fixing faulty revenue values
correct_revenue(company_revenue)
correct_revenue(customer_revenue)

"""
SEARCH FORMATS:
    - FULL: Best supplier for Apple semiconductor raw-materials from France (DONE)
    - PARTIAL: Apple semiconductor supplier from France (DONE)
    - CASUAL: When was Apple established? (TODO)

    - IDEAL FORMAT: <OPT: ADJ> <COMPANY IDENTIFIER> <CUSTOMER> <HIGH-TECH-SEGMENT> <OPT: COUNTRY>

IMPLICIT FORMAT CONVERSION STRATEGY:
    - full_format = [ADJ, COMPANY IDENTIFIER, CUSTOMER, SEGMENT, COUNTRY]
    - partial_format = [COMPANY IDENTIFIER, CUSTOMER, SEGMENT, COUNTRY]
    - casual_format = [COMPANY IDENTIFIER, CUSTOMER, SEGMENT]
"""

# search logic

def tokenize_and_filter(query):
    tokenizer = RegexpTokenizer(r'\w+')
    tokenized = tokenizer.tokenize(query)
    filtered_tokenized = [word for word in tokenized if word not in stopwords.words('english')]
    return filtered_tokenized


def noun_adj_verb_splitter(filter_query):
    is_adj = lambda pos: pos[:2] == 'JJ'
    is_noun = lambda pos: pos[:2] == 'NN'

    # to be implemented for CASUAL queries
    is_verb = lambda pos: pos[:2] == "VB"

    noun_list = [word for (word, pos) in nltk.pos_tag(filter_query) if is_noun(pos)]
    # print(noun_list)
    adj_list = [word for (word, pos) in nltk.pos_tag(filter_query) if is_adj(pos)]
    # print(adj_list)
    verb_list = [word for (word, pos) in nltk.pos_tag(filter_query) if is_verb(pos)]
    # print(verb_list)

    return adj_list, noun_list
    # TODO: CASUAL QUERIES
    # return adj_list, noun_list, verb_list

# perform a semantic similarity to rule out unwanted adjectives
# implicitly, makes use of the cosine similarity to factor semantics
def process_adjective(adj):
    if len(adj) == 0:
        return adj

    for token in adj:
        tokens = nlp(f'best {token}')

        if tokens[0].similarity(tokens[1]) < 0.5:
            adj.pop(adj.index(token))
    
    return adj
            

# perform a semantic similarity to rule out unwanted nouns
# implicitly, makes use of the cosine similarity to factor semantics
def process_nouns(nouns):
    if len(nouns) == 0:
        return nouns

    for token in nouns:
        tokens = nlp(f'material {token}')

        if tokens[0].similarity(tokens[1]) > 0.5:
            nouns.pop(nouns.index(token))
    
    return nouns
            

# search queries
query = "who is the best supplier of Apple  for  raw material of semiconductor in France?"
query2 = "From France, Who is the best supplier of semiconductor raw material for Apple?"
query3 = "semiconductor supplier for Apple from France"
querye = "this is an erranoues query for monkey testing."

filter_query = tokenize_and_filter(query)
# print(filter_query)

adj, nouns = noun_adj_verb_splitter(filter_query)
# print(adj, nouns)

adj = process_adjective(adj)
nouns = process_nouns(nouns)
print(adj, nouns)

# programmable search
def full_format_search(adj, nouns):
    print('In full format search')
    index = assign_search_index(adj, nouns, 'full')
    print(index)
    # implement from hereeeeee


def partial_format_search(adj, nouns):
    print('In partial format search')
    index = assign_search_index(adj, nouns, 'partial')
    print(index)


# TODO:
def casual_format_search(adj, nouns):
    print('In casual format search')
    index = assign_search_index(adj, nouns, 'casual')
    print(index)


def assign_search_index(adj, nouns, search_format):
    index = ['', '', '']
    indexc = ['', '']

    # pop off company identifier
    pop_identifier(nouns)

    if search_format == 'full':
        print(adj, nouns)

        for token in nouns:
            if token.lower() == "semiconductor" or token.lower() == "electronical & electronics":
                index[1] = token.lower()
            elif token.lower() in company_country and index[2] == '':
                index[2] = token.lower()
            elif token.lower() in customer_list and index[0] == '':
                index[0] = token.lower()
            else:
                no_results()
        
        return index

    elif search_format == 'partial':
        print(adj, nouns)

        for token in nouns:
            if token.lower() == "semiconductor" or token.lower() == "electronical & electronics":
                index[1] = token.lower()
            elif token.lower() in company_country and index[2] == '':
                index[2] = token.lower()
            elif token.lower() in customer_list and index[0] == '':
                index[0] = token.lower()
            else:
                no_results()
        
        return index

    # TODO: CASUAL
    elif search_format == 'casual':
        print(adj, nouns)

        for token in nouns:
            if token.lower() == "semiconductor" or token.lower() == "electronical & electronics":
                index[1] = token.lower()
            elif token.lower() in customer_list and index[0] == '':
                index[0] = token.lower()
            else:
                no_results()
        
        return index

    # return index

# pop off identifier based on cosine similarity
def pop_identifier(nouns):
    reference = 'supplier'
    for token in nouns:
        tokens = nlp(f'{reference} {token}')

        if tokens[0].similarity(tokens[1]) > 0.5:
            nouns.pop(nouns.index(token))
    

if len(adj) == 1 and len(nouns) == 4:
    full_format_search(adj, nouns)

elif len(adj) == 0 and len(nouns) == 4:
    partial_format_search(adj, nouns)

# TODO: CASUAL
elif len(adj) == 0 and len(nouns) == 3:
    casual_format_search(adj, nouns)

else:
    something_is_wrong()
