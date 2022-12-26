import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import spacy
import copy
import torch
from transformers import BertTokenizer, BertModel
import numpy as np
from scipy import spatial
import json

nlp = spacy.load("en_core_web_sm")
model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
bert = BertTokenizer.from_pretrained('bert-base-uncased')
model.eval()
words = [x for x in bert.vocab.keys()]

def find_types(word_list, tenses):
    # Finds tense specified words from given word list and list of tenses    
    doc = nlp(' '.join(word_list))
    return [x.text for x in doc if x.text.isalpha()==True and len(x.text)>1 and x.pos_ in tenses]    

def bert_vectors(sent):
    # Creates contextualized vectors for given sentence
    d = {}      
    tokenized_text = bert.tokenize(sent)
    token_ids = bert.convert_tokens_to_ids(tokenized_text)
    tokens_tensor = torch.tensor([token_ids])    
    with torch.no_grad():
        outputs = model(tokens_tensor)    
    w = [words[x] for x in token_ids]
    count = 0
    while count < len(w):
        d[w[count]]=np.array(outputs[0][0][count])
        count+=1    
    return d

def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)

def avg_vectors(vec_list):
    Avg_Vector =  np.average(vec_list, axis=0)
    return Avg_Vector

def create_json(filepath, list):
    with open(filepath, 'w') as fp:
        json.dump(list, fp)

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

# A = bert_vectors('pigeon')
# B = bert_vectors('sparrow')
# print(compare_words(A['pigeon'], B['sparrow']))

ADJ= find_types(words, ['ADJ'])
create_json('Bert_Adjs.json',ADJ)


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


