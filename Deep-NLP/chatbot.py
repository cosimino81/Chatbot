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
# NOTE: In the 'conversation_ids' list the first code of every element is the question
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
    text = re.sub(r"\[", "", text)
    text = re.sub(r"\]", "", text)
    text = re.sub(r'"', '', text)
    text = re.sub(r"[-|'.&?*,;:<>{}!]", "", text)
    text = re.sub(r'[-#%".]', "", text)
    text = re.sub(r"[-@+=-]", "", text)
    text = re.sub(r"[-()$]", "", text)
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
            word2count[word] +=1

# FILTERING AND TOKENIZATION 
# Creating two dictionaries that map the questions words and the answer words to unique integer
threshold = 20
questionwords2int ={}
word_number = 0
for word, count in word2count.items():
    if count >= threshold:
        questionwords2int[word] = word_number
        word_number +=1
        
answerwords2int ={}
word_number = 0
for word, count in word2count.items():
    if count >= threshold:
        answerwords2int[word] = word_number
        word_number +=1

# Adding the last tokens to the two dictionaries
tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']
for token in tokens:
    questionwords2int[token] = len(questionwords2int) + 1
for token in tokens:
    answerwords2int[token] = len(answerwords2int) + 1 



# Creating the inverse dictionary of the answerwords2int dictionary
answerints2word = {w_i: w for w, w_i in answerwords2int.items()}

# Adding the End of String token to the end of every answer
for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>' 

# Translate all the questions and answers (clean_answers, clean_questions) 
# into the unique integer that was mapped into answerints2word
# and replacing all the words that were filtered out with <OUT>
questions_to_int = []
for question in clean_questions:
    ints = []
    for word in question.split():
        if word not in questionwords2int:
            ints.append(questionwords2int['<OUT>'])
        else:
            ints.append(questionwords2int[word])
    questions_to_int.append(ints)
        

answers_to_int = []
for answer in clean_answers:
    ints = []
    for word in answer.split():
        if word not in answerwords2int:
            ints.append(answerwords2int['<OUT>'])
        else:
            ints.append(answerwords2int[word])
    answers_to_int.append(ints)   

# Sorting both the questions and answers by the lenght of the questions
sorted_clean_questions = []
sorted_clean_answers = []
for length in range(1, 25 + 1):
    for i in enumerate(questions_to_int):
        if len(i[1]) == length:
            sorted_clean_questions.append(questions_to_int[i[0]])
            sorted_clean_answers.append(answers_to_int[i[0]])
    

############# PART 2 - BUILDING THE SEQ2SEQ MODEL ##############

# Creating the placeholders for input and targhets
def model_inputs():
    # Arguments: placeholder(type of input, matrix dimension, name of input)
    inputs = tf.placeholder(tf.int32, [None, None], name = 'input')
    targets = tf.placeholder(tf.int32, [None, None], name = 'target')
    lr = tf.placeholder(tf.float32, name = 'learning_rate')
    keep_prob = tf.placeholder(tf.float32, name = 'keep_prob')
    return inputs, targets, lr, keep_prob

# Processing the targets
def preprocess_targets(targets, word2int, batch_size):
    # Arguments: tf.fill(size of the matrix, )
    left_side = tf.fill([batch_size, 1], word2int['<SOS>'])
    right_side = tf.strided_slice(targets, [0,0], [batch_size, -1], [1,1])
    preprocessed_targets = tf.concat([left_side, right_side], 1)
    return preprocessed_targets

# Creating the Encoder RNN Layer           




