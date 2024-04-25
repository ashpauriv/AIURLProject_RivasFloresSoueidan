#!/usr/bin/env python3
#Preprocesses the data in training and testing 
#sets and then trains the AI model with random forests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from joblib import Parallel, delayed
import tldextract

def extract_features(url):
    ext = tldextract.extract(url)
    return {
        'length': len(url),
        'num_special_chars': sum(not c.isalnum() for c in url),
        'contains_login': 'login' in url,
        'contains_free': 'free' in url,
        'contains_click_here': 'click here' in url,
        'is_https': url.startswith('https'),
        'domain': ext.domain,
        'tld': ext.suffix,
        'num_subdomains': len(ext.subdomain.split('.')) if ext.subdomain else 0
    }

def preprocess_data(filename):
    data = pd.read_csv(filename, header=None, names=['url', 'label'])
    data['label'] = data['label'].map({'bad': 1, 'good': 0})

    # Parallelize feature extraction
    results = Parallel(n_jobs=-1)(delayed(extract_features)(url.lower().replace('www.', '')) for url in data['url'])
    features_df = pd.DataFrame(results)
    
    data = pd.concat([data, features_df], axis=1)

    scaler = StandardScaler()
    numeric_features = ['length', 'num_special_chars', 'num_subdomains']
    data[numeric_features] = scaler.fit_transform(data[numeric_features])

    X_train, X_test, y_train, y_test = train_test_split(data.drop(['url', 'label'], axis=1), data['label'], test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred))

if __name__ == "__main__":
    filename = 'cleaned_data.csv'
    X_train, X_test, y_train, y_test = preprocess_data(filename)
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
