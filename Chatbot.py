import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import copy
from bert_embedding import BertEmbedding
import mxnet as mx
from bert_embedding import BertEmbedding






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
        
    def tokenize(self,sent):
        return nltk.word_tokenize(sent)

    def stem(self,word):
        return self.stemmer.stem(word.lower()) 

    def stem_sent(self,sent):
        return [self.stem(token) for token in self.tokenize(sent) if token not in self.stopwords]
    
    def get_embeddings(self):
        # gets bert embeddings for the tokenized sentence
        return self.bert(self.tokenize(self.sentence))

c = Converter('hello I am a cat')
print(c.get_embeddings())