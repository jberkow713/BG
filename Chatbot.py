import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import copy
import torch
from transformers import BertTokenizer, BertModel
import numpy as np
from scipy import spatial

model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
model.eval()

def bert_vectors(sent):
    # Creates contextualized vectors for given sentence
    d = {}
    bert = BertTokenizer.from_pretrained('bert-base-uncased')    
    words = [x for x in bert.vocab.keys()]    
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

A = bert_vectors('pizza is tasty')
B = bert_vectors('i like pizza')

def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)

print(compare_words(A['pizza'], B['pizza']))

# TODO
# Language converter
# Only want to create the relationships which provide information, as in the relationships 
# between parts of the sentence that matter, and matter is contextual and interpretable

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
           

# TODO
# Clean the vocab, store the usable words in json file, as dictionary objects {word:bert_vector}
# print(c.bert.vocab.__dict__) represents all trained words, needs cleaning and storage

