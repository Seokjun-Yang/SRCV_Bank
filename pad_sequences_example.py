from keras.preprocessing.sequence import pad_sequences

train_inputs = pad_sequences(train_seq, maxlen=MAX_SEQ, padding='post', value = 0)
label_inputs = pad_sequences(train_lab, maxlen=1, padding='post', value = 0)

i = []
i = pad_sequences(seque, maxlen=MAX_SEQ, padding='post', value = 0)