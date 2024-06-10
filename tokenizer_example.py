from keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer(10000)
tokenizer.fit_on_texts(train_X)
train_seq = tokenizer.texts_to_sequences(train_X)
train_lab = tokenizer.texts_to_sequences(train_y)

tokenizer.fit_on_texts(tr)
seque = tokenizer.texts_to_sequences(tr)