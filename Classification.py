import speech_recognition as sr
from konlpy.tag import Okt
from nltk.corpus import stopwords


MAX_SEQ = 8
train_X = []
train_y = []
okt = Okt()
tr = []


train_data = {
    'document': [
        "돈 보내줘",
        "송금해줘",
        "이체해라",
        "신한은행 홍길동에게 50만원을 송금해줘",
        "국민은행 김철수한테 10만원 만큼 보내라",
        "농협은행 이철수에게 30만원 이체"
    ],

    'label': [
        '송금',
        '송금',
        '송금',
        '송금',
        '송금',
        '송금'
    ]
}


stopwords = ['은', '는', '이', '가', '을', '를', '으로', '쪽으로', '원',
             '쪽', '쪽에', '에', '에게', '의', '과', '와', '한테', '다',
             '하다', '정도만', '정도', '만', '만큼','주다', '하고']


for sentence in train_data['document']:
    tmp_x = []
    tmp_x = okt.morphs(sentence, stem=True, norm=True)

    tmp_x = [word for word in tmp_x if not word in stopwords]
    train_X.append(tmp_x)

for sentence in train_data['label']:
    tmp_y = []
    tmp_y = okt.morphs(sentence, stem=True, norm=True)

    tmp_y = [word for word in tmp_y if not word in stopwords]
    train_y.append(tmp_y)


from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(10000)
tokenizer.fit_on_texts(train_X)
train_seq = tokenizer.texts_to_sequences(train_X)
train_lab = tokenizer.texts_to_sequences(train_y)

train_inputs = pad_sequences(train_seq, maxlen=MAX_SEQ, padding='post', value = 0)
label_inputs = pad_sequences(train_lab, maxlen=1, padding='post', value = 0)


from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

clf = OneVsRestClassifier(LogisticRegression(class_weight='balanced'))
clf.fit(train_inputs, label_inputs)


r = sr.Recognizer()

with sr.Microphone() as source:
    print("소음 측정..")
    r.adjust_for_ambient_noise(source)
    print("음성 입력..")
    speech= r.listen(source)

try:
    audio = r.recognize_google(speech, language='ko-KR')
    print("음성 입력 결과:", audio, end='\n\n')
except sr.UnknownValueError:
  print("음성 인식 실패")
  exit()
except sr.RequestError as e:
  print("Google Speech Recognition 서비스 오류 {0}".format(e))
  exit()


morphs_result = okt.morphs(audio, stem=True)
t_words = [word for word in morphs_result if not word in stopwords]
tr.append(t_words)
print(tr)


tokenizer.fit_on_texts(tr)
seque = tokenizer.texts_to_sequences(tr)

i = []
i = pad_sequences(seque, maxlen=MAX_SEQ, padding='post', value = 0)
print(clf.decision_function(i))
print("Accuracy: ", format((int)(clf.score)))

print(clf.predict(i))