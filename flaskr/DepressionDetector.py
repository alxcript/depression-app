import joblib

class DepressionDetector:
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        self.modelDetector = svm = joblib.load('nb_depression_model.sav')

    def predict(self, text):
        example_counts = vectorizer.transform([a])
        prediction =nb.predict(example_counts)
        pass

    def preprocess(text):
        #preprocess
        a = re.sub('[^a-zA-Z]',' ',text)
        a = a.lower()
        a = a.split()
        a = [wo.lemmatize(word) for word in a ]
        a = ' '.join(a)  
        return a