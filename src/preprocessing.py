import re
import pickle
import pandas as pd
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

ps = PorterStemmer()
all_stopwords = stopwords.words('english')
all_stopwords.remove('not')

def process_review(review: str):
    review = re.sub('[^a-zA-Z]', ' ', review)
    review = review.lower()
    review = review.split()
    review = [ps.stem(word) for word in review if not word in set(all_stopwords)]
    review = ' '.join(review)
    return review

def pre_process(dataset: pd.DataFrame):
    corpus = []
    for i in range(0, 900):
        processed_review = process_review(dataset['Review'][i])
        corpus.append(processed_review)

    cv = CountVectorizer(max_features=1420)
    X = cv.fit_transform(corpus).toarray()
    y = dataset.iloc[:, -1].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)
    
    # Save the CountVectorizer
    pickle.dump(cv, open('data/models/c1_BoW_Sentiment_Model.pkl', "wb"))
    
    return X_train, X_test, y_train, y_test
