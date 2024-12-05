import pandas as pd
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report
import pickle

nltk.download('stopwords')
nltk.download('wordnet')

df = pd.read_csv('C:/Users/KamarajanVD/PycharmProjects/WebGuard/frontend/Spam Email raw text for NLP.csv')

lemmatizer = WordNetLemmatizer()
stopwords_list = set(stopwords.words('english'))

corpus = []
for message in df['MESSAGE']:
    message = re.sub('[^a-zA-Z0-9]', ' ', message.lower())
    message = [lemmatizer.lemmatize(
        word) for word in message.split() if word not in stopwords_list]
    corpus.append(' '.join(message))

tfidf = TfidfVectorizer(ngram_range=(1, 3), max_features=2500)
X = tfidf.fit_transform(corpus).toarray()
y = df['CATEGORY']

with open('models/tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=1)


bnb = BernoulliNB()
mnb = MultinomialNB()
rfc = RandomForestClassifier(n_estimators=100)

bnb.fit(x_train, y_train)
mnb.fit(x_train, y_train)
rfc.fit(x_train, y_train)


voting_model = VotingClassifier(estimators=[
    ('bnb', bnb),
    ('mnb', mnb),
    ('rfc', rfc)
], voting='hard')

voting_model.fit(x_train, y_train)


with open('models/ensemble_model.pkl', 'wb') as f:
    pickle.dump(voting_model, f)


y_pred = voting_model.predict(x_test)
print(classification_report(y_test, y_pred))

print("Training complete.")