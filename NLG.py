import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import string
import random
import numpy as np
from scipy import spatial
import spacy

Spacy= spacy.load("en_core_web_sm")
Gpt= GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.add_special_tokens({
    "eos_token": "</s>",
    "bos_token": "<s>",
    "unk_token": "<unk>",
    "pad_token": "<pad>",
    "mask_token": "<mask>"
})

def remove_punc(sent):
    # Removes punctuation given sentence
    test_str = sent.translate(str.maketrans('', '', string.punctuation))
    return test_str

def get_vector(word,model_type):
    if model_type=='GPT':
        text_index = tokenizer.encode(word,add_prefix_space=True)
        vector = Gpt.transformer.wte.weight[text_index,:]
        return vector[0].detach().numpy()
    elif model_type == 'SPACY':
        vector = Spacy(word)[0].vector
        return vector    

def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)

def avg_vectors(vec_list):
    Avg_Vector =  np.average(vec_list, axis=0)
    return Avg_Vector

def compare_sentences(a,b):    
    d1 = Spacy(a)
    d2 = Spacy(b)
    tenses = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PART', 'PRON']
    words = [x.text for x in d1 if x.pos_ in tenses]
    words2 = [x.text for x in d2 if x.pos_ in tenses]
    avg_a = [get_vector(x, 'SPACY') for x in words]
    avg_b = [get_vector(x, 'SPACY') for x in words2]
    return compare_words(avg_vectors(avg_a), avg_vectors(avg_b))

class Chatbot:
    # Initial version of chatbot    
    def __init__(self, input, min_reply,randomness):
        self.input = input
        self.min_reply = min_reply
        self.randomness=randomness
        self.count = 0
        self.responses = {}
        self.output = None

    def generate_response(self):
        # Generates response with certain restrictions
        if self.count == 10:            
            vals = sorted([x for x in self.responses.values()],reverse=True)
            count = 0
            for k,v in self.responses.items():
                
                if v == vals[count]:
                    self.output=k
                    return                        

        inputs = tokenizer.encode(self.input, return_tensors='pt')
        outputs = Gpt.generate(inputs, max_length=50, do_sample=True, temperature=self.randomness,top_k=50)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        original = list(set(text.replace('\n','').split('.')))                   
        final = [x for x in original if x!=remove_punc(self.input) and len(x)>0 and len(x.split())>self.min_reply]
        if len(final)==0:
            return "I don't know what to tell you..."
        rand_response = final[random.randint(0,len(final)-1)]
        compared = compare_sentences(self.input,rand_response)
        
        orig = self.input.split()
        new = rand_response.split()
        count = 0
        for x in orig:
            if x in new:
                count+=1
        similarity = count/len(orig)

        if compared>.8 and rand_response!=None and similarity<.8:
            self.output=rand_response
            return 
        else:            
            self.count+=1
            self.responses[rand_response]=compared
            self.generate_response()

sent = "i like walking on the beach"
sent2 = "I enjoy going to see a movie"
# print(compare_sentences(sent,sent2))
C = Chatbot(sent,4,1.3)
C.generate_response()
print(C.output)
# a = get_vector('pigeon','SPACY')
# b = get_vector('sparrow', 'GPT')