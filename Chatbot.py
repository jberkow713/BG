import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import copy

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
        
    def tokenize(self,sent):
        return nltk.word_tokenize(sent)

    def stem(self,word):
        return self.stemmer.stem(word.lower()) 

    def stem_sent(self,sent):
        return [self.stem(token) for token in self.tokenize(sent) if token not in self.stopwords]

c = Converter('organize the park')
print(c.stem_sent(c.sentence))