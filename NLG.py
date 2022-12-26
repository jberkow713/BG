import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import string
import random
import numpy as np
from scipy import spatial

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

def remove_punc(sent):
    # Removes punctuation given sentence
    test_str = sent.translate(str.maketrans('', '', string.punctuation))
    return test_str

def get_vector(word):
    # Gets specific word vector for GPT2 model
    text_index = tokenizer.encode(word,add_prefix_space=True)
    vector = model.transformer.wte.weight[text_index,:]
    return vector[0].detach().numpy()
def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)


class Chatbot:
    # Initial version of chatbot
    def __init__(self, input, min_reply):
        self.input = input
        self.min_reply = min_reply
    def generate_response(self):
        inputs = tokenizer.encode(self.input, return_tensors='pt')
        outputs = model.generate(inputs, max_length=50, do_sample=True, temperature=.5,top_k=50)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        original = list(set(text.split('.')))        
        final = [x for x in original if x!=remove_punc(self.input) and len(x)>0 and '\n' not in x and len(x.split())>self.min_reply]
        if len(final)==0:
            return "I don't know what to tell you..."

        rand_response = final[random.randint(0,len(final)-1)]
            
        return rand_response
# a = get_vector('pigeon')
# b = get_vector('sparrow')
# print(compare_words(a,b))

sent = "Have a good night"
C = Chatbot(sent,4)
print(C.generate_response())



