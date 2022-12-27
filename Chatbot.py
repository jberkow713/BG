import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import spacy
import copy
import torch
from transformers import BertTokenizer, BertModel
import numpy as np
from scipy import spatial
import json
import io



nlp = spacy.load("en_core_web_lg")
# model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
# bert = BertTokenizer.from_pretrained('bert-base-uncased')
# model.eval()
# words = [x for x in bert.vocab.keys()]

def find_types(word_list, tenses):
    # Finds tense specified words from given word list and list of tenses    
    doc = nlp(' '.join(word_list))
    return [x.text for x in doc if x.text.isalpha()==True and x.text in word_list and len(x.text)>1 and x.pos_ in tenses]

def find_words(tenses):
    words = list(nlp.vocab.strings)[:50000]
    doc = nlp(' '.join(words))
    
    return [x.text for x in doc if x.text.isalpha()==True and len(x.text)>1 and x.pos_ in tenses]

def bert_vectors(word):
    # Creates contextualized vectors for given sentence
    tokenized_text = bert.tokenize(word)
    token_ids = bert.convert_tokens_to_ids(tokenized_text)
    tokens_tensor = torch.tensor([token_ids])    
    with torch.no_grad():
        outputs = model(tokens_tensor)    
    return np.array(outputs[0][0][0])    

def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)

def avg_vectors(vec_list):
    Avg_Vector =  np.average(vec_list, axis=0)
    return Avg_Vector

def create_json(filepath, item):
    with open(filepath, 'w') as fp:
        json.dump(item, fp)

class Converter:
    def __init__(self, sentence):
        self.sentence = sentence
        self.original = copy.deepcopy(sentence)
        self.stemmer = PorterStemmer()
        self.stopwords = set(stopwords.words('english'))
        self.subject = None
        self.action = []
        self.descriptors = []
        self.relatives = []
        self.act_rel_dict = {}         
        
    def tokenize(self,sent):
        return nltk.word_tokenize(sent)

    def stem(self,word):
        return self.stemmer.stem(word.lower()) 

    def stem_sent(self,sent):
        return [self.stem(token) for token in self.tokenize(sent) if token not in self.stopwords]

def closest_vals(list, index,top_n):

    Compared = {}
    Word = list[index]
    list.remove(Word)
    count = 0
    for word in list:
        Compared[word]=compare_words(Word,word)
        count+=1
        if count %100 == 0:
            print(count)
    Top_Vals = sorted([x for x in Compared.values()],reverse=True)[:top_n]
    Close = {}
    Closest = []
    for val in Top_Vals:
        for k,v in Compared.items():
            if v == val:
                Closest.append(k)
    Close[Word]=Closest
    return Close


# create_json('Spacy_Adjs.json', find_words(['ADJ']))
# create_json('Spacy_Nouns.json', find_words(['NOUN']))
# create_json('Spacy_Verbs.json', find_words(['VERB']))

# with open("Spacy_Nouns.json") as file:
#     Nouns = json.load(file)

# print(Nouns[0:100])


sent = 'airplane'
sent_2 = 'helicopter'
doc = nlp(sent)
doc2 = nlp(sent_2)
a = doc[0].vector
b = doc2[0].vector
print(compare_words(a,b))



# with open("Bert_Nouns.json") as file:
#     Nouns = json.load(file)

# print(compare_words('time', 'years'))

# print(closest_vals(Nouns,1,20))

    




# A = bert_vectors('pigeon')
# B = bert_vectors('sparrow')
# print(compare_words(A['pigeon'], B['sparrow']))

# ADJ= find_types(words, ['ADJ'])
# create_json('Bert_Adjs.json',ADJ)


# TODO
# First link words together based on tense, then going to compare each word to all the other usable words,
# Rank them all, as similar, opposite, [{Word:{Opposites:[], Similar:[]}}, ....,....]

# Basically then create some kind of generalized word list, response list, etc
# Store that information in json file

# TODO
# Break down the sentences by relationship, and tense, 
# Then going to access this list of top related, or opposite words, 
# randomized a bit, 
# Then piece the sentence back together
# Need an entire format to then piece these 'value' words, back together, return a sentence


