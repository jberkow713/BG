import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

stemmer = PorterStemmer()
stopwords = set(stopwords.words('english'))

def tokenize(sent):
    return nltk.word_tokenize(sent)

def stem(word):
    return stemmer.stem(word.lower()) 

def stem_sent(sent):
    return [stem(token) for token in tokenize(sent) if token not in stopwords]

print(stem_sent('organize the park'))
