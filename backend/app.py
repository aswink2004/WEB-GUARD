import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import joblib
with open('models/ensemble_model.pkl', 'rb') as f:
    ensemble_model = pickle.load(f)

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

with open('models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)

with open('models/ensemble_model.pkl', 'rb') as f:
    ensemble_model = pickle.load(f)


@app.route('/', methods=['GET'])
def home():
    return "WebGuard : An AI Machine Learning Extension For Spam Prevention."

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json['message']
    vectorized_message = tfidf_vectorizer.transform([data])
    prediction = ensemble_model.predict(vectorized_message)

    result = 'spam' if prediction[0] == 1 else 'not spam'
    return jsonify({'prediction': result})

@app.route('/check-url', methods=['POST'])
def check_url():
    try:
        data = request.get_json()
        url = data['url']

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        website_text = soup.get_text(separator=' ')

        spam_sentences = predict_sentences(website_text)

        return jsonify({'success': True, 'spamSentences': spam_sentences})

    except Exception as e:
        print(f"Error processing URL: {e}")
        return jsonify({'success': False, 'error': str(e)})

def predict_sentences(website_text):
    sentences = re.split(r'[.;—]', website_text)
    spam_sentences = []

    for sentence in sentences:
        if sentence.strip():
            if predict_sentence(sentence):
                spam_sentences.append(sentence.strip())
    return spam_sentences


def predict_sentence(sentence):
    vectorized_sentence = tfidf_vectorizer.transform([sentence])
    prediction = ensemble_model.predict(vectorized_sentence)
    return True if prediction[0] == 1 else False


# def check_spam():
#     data = request.get_json()
#     sentence = data.get('text')
#     # Replace this with actual spam detection logic
#     is_spam = predict_spam(sentence)
#     return jsonify({'isSpam': is_spam})
#
# def predict_spam(sentence):
#     message_sentence=tfidf_vectorizer.transform(sentence)
#     predict=ensemble_model.predict(message_sentence)
#     # print(predict)
#     return True if predict[0]==1 else False;


if __name__ == '__main__':
    app.run(debug=True)