import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import string
import random
import numpy as np
from scipy import spatial
import spacy

nlp = spacy.load("en_core_web_sm")

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.add_special_tokens({
    "eos_token": "</s>",
    "bos_token": "<s>",
    "unk_token": "<unk>",
    "pad_token": "<pad>",
    "mask_token": "<mask>"
})

model = GPT2LMHeadModel.from_pretrained('gpt2')

def remove_punc(sent):
    # Removes punctuation given sentence
    test_str = sent.translate(str.maketrans('', '', string.punctuation))
    return test_str

def get_vector(word,model_type):
    if model_type=='GPT':
        text_index = tokenizer.encode(word,add_prefix_space=True)
        vector = model.transformer.wte.weight[text_index,:]
        return vector[0].detach().numpy()
    elif model_type == 'SPACY':
        vector = nlp(word)[0].vector
        return vector
        
    # Gets specific word vector for GPT2 model
    

def compare_words(a,b):
    #compares word vectors using Bert model 
    return 1 - spatial.distance.cosine(a,b)

def avg_vectors(vec_list):
    Avg_Vector =  np.average(vec_list, axis=0)
    return Avg_Vector

class Chatbot:
    # Initial version of chatbot
    
    def __init__(self, input, min_reply,randomness):
        self.input = input
        self.min_reply = min_reply
        self.randomness=randomness
    def generate_response(self):
        inputs = tokenizer.encode(self.input, return_tensors='pt')
        outputs = model.generate(inputs, max_length=50, do_sample=True, temperature=self.randomness,top_k=50)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        original = list(set(text.replace('\n','').split('.')))
                   
        final = [x for x in original if x!=remove_punc(self.input) and len(x)>0 and len(x.split())>self.min_reply]
        if len(final)==0:
            return "I don't know what to tell you..."
        rand_response = final[random.randint(0,len(final)-1)]            
        return rand_response

# a = get_vector('pigeon','SPACY')
# b = get_vector('sparrow', 'GPT')

sent = "I love watching television with my pants off in delaware"
vectors = [get_vector(x, 'SPACY') for x in sent.split()]
print(vectors)

C = Chatbot(sent,4,1.2)
print(C.generate_response())