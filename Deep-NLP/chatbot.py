# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 11:41:17 2018
Building a chatbot with NLP
@author: CURIACOSI1
"""
import numpy as np
import tensorflow as tf
import re
import time

##############  PART 1 - DATA PREPROCESSING #################

# Importing the datasets
lines = open('movie_lines.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')

# Creating a dictionary that maps each line and its id
id2line ={}
for line in lines:
    _line= line.split('+++$+++') 
    if len(_line) == 5:
        id2line[_line[0].replace(" ", "")] = _line[4]

# Creating a list of all the conversations
conversation_ids = []
for conversation in conversations[:-1]:  # The last row is empty
    # take the last element and remuve the square braket
    _conversation = conversation.split('+++$+++')[-1][2:-1].replace("'", "").replace(" ", "") 
    conversation_ids.append(_conversation.split(','))

# Getting seperately the questions and the answers
# NOTE: In the 'conversation_ids' lis the first code of every element is the answer
#       and the second code is the answer
questions = []
answers = []
for conversation in conversation_ids:
    for i in range(len(conversation) -1):
        questions.append(id2line[conversation[i]])
        answers.append(id2line[conversation[i+1]])

# Cleaning of the text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"there's", "there is", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"can ' t", "cannot", text)
    text = re.sub(r"didn't", "did not", text)
    text = re.sub(r"don't", "do not", text)
    text = re.sub(r"doesn't", "does not", text)
    text = re.sub(r"aren't", "are not", text)
    text = re.sub(r"isn't", "is not", text)
    text = re.sub(r"haven't", "have not", text)
    text = re.sub(r"couldn't", "could not", text)
    text = re.sub(r"it's", "it is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"/", "", text)
    text = re.sub(r"[-|'.?,;:<>{}!]", "", text)
    text = re.sub(r'[-#"...]', "", text)
    text = re.sub(r"[-@+=-]", "", text)
    text = re.sub(r"[-()]", "", text)
    text = re.sub(r"  ", " ", text)
    text = text.strip()
    return text
        
# Cleaning questions
clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))
# Cleaning answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))


# Mapping the words occurences in order to remove not frequent words
word2count = {}
for question in clean_questions:
    for word in question.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1

for answer in clean_answers:
    for word in answer.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1






