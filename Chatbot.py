import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import copy
from bert_embedding import BertEmbedding
import numpy as np
from scipy import spatial

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
        self.bert = BertEmbedding()
        self.embeddings = self.get_embeddings()  
        
    def tokenize(self,sent):
        return nltk.word_tokenize(sent)

    def stem(self,word):
        return self.stemmer.stem(word.lower()) 

    def stem_sent(self,sent):
        return [self.stem(token) for token in self.tokenize(sent) if token not in self.stopwords]
    
    def get_embeddings(self):
        # gets bert embeddings for the tokenized sentence
        return self.bert(self.tokenize(self.sentence))
    def compare_words(self, a,b):        
        return 1 - spatial.distance.cosine(a, b)    

c = Converter('dog wolf')

# TODO
# Clean the vocab, store the usable words in json file, as dictionary objects {word:bert_vector}
# print(c.bert.vocab.__dict__) represents all trained words, needs cleaning and storage

print(c.compare_words(c.embeddings[0][1], c.embeddings[1][1]))
print(c.bert.vocab.__dict__)