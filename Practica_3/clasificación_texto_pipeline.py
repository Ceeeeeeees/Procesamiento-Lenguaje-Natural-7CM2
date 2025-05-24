from sklearn.datasets import fetch_20newsgroups
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD

#Separación en entrenamiento y prueba
newsgroups_train = fetch_20newsgroups(subset='train')
newsgroups_test = fetch_20newsgroups(subset='test')
X_train = newsgroups_train.data
y_train = newsgroups_train.target
X_test = newsgroups_test.data
y_test = newsgroups_test.target

# ~ #Pipeline
pipe = Pipeline([('text_representation', TfidfVectorizer()), ('classifier', MultinomialNB())])
print (pipe)
pipe.fit(X_train, y_train)
print (len(pipe['text_representation'].get_feature_names_out()))
y_pred = pipe.predict(X_test)
print (classification_report(y_test, y_pred))

# ~ pipe = Pipeline([('text_representation', TfidfVectorizer()), ('classifier', LogisticRegression())])
# ~ print (pipe)
# ~ pipe.fit(X_train, y_train)
# ~ print (pipe['text_representation'].get_feature_names_out())
# ~ print (len(pipe['text_representation'].get_feature_names_out()))
# ~ y_pred = pipe.predict(X_test)
# ~ print (classification_report(y_test, y_pred))






