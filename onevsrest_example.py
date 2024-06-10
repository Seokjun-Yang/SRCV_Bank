from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

clf = OneVsRestClassifier(LogisticRegression(class_weight='balanced'))
clf.fit(train_inputs, label_inputs)

print(clf.decision_function(i))
print("Accuracy: ", format((int)(clf.score)))

print(clf.predict(i))