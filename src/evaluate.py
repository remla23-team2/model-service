from sklearn.metrics import confusion_matrix, accuracy_score

def evaluate_model(classifier, X_test, y_test):
    y_pred = classifier.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)   
    return accuracy_score(y_test, y_pred), cm