import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import re
from nltk.stem import WordNetLemmatizer

class DepressionDetector:
    def __init__(self):
        self.modelDetector = joblib.load('./flaskr/nb_depression_model.sav')
        self.vectorizer = joblib.load('./flaskr/vectorize.pkl')

    def predict(self, text):
        wo = WordNetLemmatizer()
        a = re.sub('[^a-zA-Z]', ' ', text)
        a = a.lower()
        a = a.split()
        a = [wo.lemmatize(word) for word in a]
        a = ' '.join(a)
        example_counts = self.vectorizer.transform([a])
        prediction = self.modelDetector.predict(example_counts)
        if prediction[0] == 1:
            return "Depression"
        else:
            return "Positive"
