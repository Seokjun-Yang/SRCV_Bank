import speech_recognition as sr
from konlpy.tag import Okt
from konlpy.tag import Komoran
from nltk.corpus import stopwords


okt = Okt()
komoran = Komoran(userdic='./dic/user_dictionary.txt')
r = sr.Recognizer()

with sr.Microphone() as source:
    print("소음 측정..")
    r.adjust_for_ambient_noise(source)
    print("음성 입력..")
    speech= r.listen(source)

try:
    audio= r.recognize_google(speech, language='ko-KR')
    print("음성 입력 결과:", audio, end='\n\n')
except sr.UnknownValueError:
  print("음성 인식 실패")
  exit()
except sr.RequestError as e:
  print("Google Speech Recognition 서비스 오류 {0}".format(e))
  exit()


stopwords = ['은', '는', '이', '가', '을', '를', '으로', '쪽으로', '원',
             '쪽', '쪽에', '에', '에게', '의', '과', '와', '한테', '다',
             '하다', '정도만', '정도', '만', '만큼','주다', '하고']

morphs_result = okt.morphs(audio, stem=True, norm=True)
print("morphs_result:", morphs_result, end='\n\n')

t_words = [word for word in morphs_result if not word in stopwords]
print("t_words:", t_words, end='\n\n')

t_words_join = ' '.join(t_words)
temp_pos = komoran.pos(t_words_join)
print("temp_pos:", temp_pos, end='\n\n')

t_words_pos = []
for word, pos in temp_pos:
    t_words_pos.append(f'{word}/{pos}')
print("t_words_pos:", ' '.join(t_words_pos), end='\n\n')