import joblib

from sklearn.naive_bayes import GaussianNB


def train(X, y):
    classifier = GaussianNB()
    classifier.fit(X, y)

    # Save the trained model and the CountVectorizer
    joblib.dump(classifier, 'data/models/c2_Classifier_Sentiment_Model')
    
    return classifier