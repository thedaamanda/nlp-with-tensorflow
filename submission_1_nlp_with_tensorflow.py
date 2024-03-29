# -*- coding: utf-8 -*-
"""Submission 1 - NLP with Tensorflow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nZdT1cxzdCAzLog1I-bQIo6KBwyHZXxu

# **Submission 1 - NLP with Tensorflow**

## **Muhammad Theda Amanda**

Dataset: https://www.kaggle.com/datasets/lokkagle/movie-genre-data

### **Import Libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
# %matplotlib inline

from google.colab import files

import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

"""### **Data Loading**"""

data = pd.read_csv('kaggle_movie_train.csv')
data.head()

print('Data size:\n')
print(f'{data.shape[0]} rows')
print(f'{data.shape[1]} columns')

print("**"*20)
print(" "*10 + str('Dataset Information'))
print("**"*20)
data.info()

"""### **Data Cleaning**"""

genre = pd.get_dummies(data.genre)
new_data = pd.concat([data, genre], axis=1)
new_data = new_data.sample(frac=1).reset_index()
new_data = new_data.drop(columns=['index', 'id'])
new_data.text = new_data.text.astype(str)
new_data

"""### **Text Preprocessing**"""

# function to get all of strings from dataframe column, and used lower function here.
def get_all_str(df):
    sentence = ''
    for i in range(len(df)):
        sentence += df['text'][i]
    sentence = sentence.lower()
    return sentence

# function to get words from text(string). used RegexpTokenizer
def get_word(text):
    result = nltk.RegexpTokenizer(r'\w+').tokenize(text.lower())
    return result

# function to add stopwords to nltp stopword list.
def stopword_list(stop):
    lst = stopwords.words('english')
    for stopword in stop:
        lst.append(stopword)
    return lst

# function to remove stopwords from list.
def remove_stopword(stopwords, lst):
    stoplist = stopword_list(stopwords)
    txt = ''
    for idx in range(len(lst)):
        txt += lst[idx]
        txt += '\n'
    cleanwordlist = [word for word in txt.split() if word not in stoplist]
    return cleanwordlist

nltk.download('stopwords')

string = get_all_str(new_data)
words = get_word(string)
removed = remove_stopword('1',words)
print(removed[:10])

"""### **Tokenizing, Sequencing, dan Padding**"""

text = new_data['text'].values
label = new_data[['action', 'comedy',	'sci-fi', 'horror', 'drama', 'thriller', 'other', 'adventure', 'romance']].values

text_train, text_test, label_train, label_test = train_test_split(text, label, test_size=0.2, random_state=42)
max_len = max([len(s.split()) for s in text_train])

tokenizer = Tokenizer(num_words=10000, oov_token='<oov>', filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
tokenizer.fit_on_texts(text_train)

sekuens_train = tokenizer.texts_to_sequences(text_train)
sekuens_test = tokenizer.texts_to_sequences(text_test)

padded_train = pad_sequences(sekuens_train, padding='post', maxlen=max_len, truncating='post')
padded_test = pad_sequences(sekuens_test, padding='post', maxlen=max_len, truncating='post')

"""### **Modeling**"""

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=10000, output_dim=64),
    tf.keras.layers.LSTM(128, return_sequences=True),
    tf.keras.layers.GlobalMaxPooling1D(),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(9, activation='softmax')
])

model.summary()

"""### **Compile and Fit Model**"""

model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy')

models_dir = 'save_models'
if not os.path.exists(models_dir):
  os.makedirs(models_dir)

checkpointer = ModelCheckpoint(filepath=os.path.join(models_dir, 'model.hdf5'),
                               monitor='val_accuracy', mode='max',
                               verbose=1, save_best_only=True)

reduce_learning_rate = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.9 and logs.get('val_accuracy')>0.9):
      self.model.stop_training = True
      print("\nThe accuracy of the training set and the validation set has reached > 90%!")

stop_callback = myCallback()

callbacks = [stop_callback, checkpointer, reduce_learning_rate]

history = model.fit(padded_train, label_train, epochs=50, validation_data=(padded_test, label_test), verbose=2, callbacks=[callbacks])

"""### **Evaluate Model**"""

model.evaluate(padded_test, label_test)

"""### **Plot Accuracy & Loss**"""

plt.figure(figsize=(15, 5))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'], linestyle='--')
plt.title('Accuracy Model')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Training Set', 'Validation Set'])
plt.grid(linestyle='--', linewidth=1, alpha=0.5)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'], linestyle='--')
plt.title('Loss Model')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Training Set', 'Validation Set'])
plt.grid(linestyle='--', linewidth=1, alpha=0.5)

plt.show()