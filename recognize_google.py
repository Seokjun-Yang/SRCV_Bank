import speech_recognition as sr

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