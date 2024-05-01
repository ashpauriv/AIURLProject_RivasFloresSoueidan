#!/usr/bin/env python3
#Preprocesses the data in training and testing 
#sets and then trains the AI model with random forests

import pandas as pd #for datasets
import numpy as np #for data analysis 
from sklearn.model_selection import train_test_split #to split dataset into subsets for training and testing 
from sklearn.preprocessing import StandardScaler #to normalize features 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import classification_report, accuracy_score
from joblib import Parallel, delayed
import tldextract #takes apart components inside url links
import matplotlib.pyplot as plt #for graphs

def extract_features(url): #extracts features from url 
    ext = tldextract.extract(url)
    return {
        'length': len(url),
        'num_special_chars': sum(not c.isalnum() for c in url),
        'contains_login': int('login' in url),
        'contains_free': int('free' in url),
        'contains_click_here': int('click here' in url),
        'is_https': int(url.startswith('https')),
        'domain_hash': hash(ext.domain),  # Using hash to convert to numeric
        'tld_hash': hash(ext.suffix),     # Using hash to convert to numeric
        'num_subdomains': len(ext.subdomain.split('.')) if ext.subdomain else 0
    }

def preprocess_data(filename):
    try:
        # Load data ensuring that mixed types in columns are handled correctly
        data = pd.read_csv(filename, header=None, names=['url', 'label'], dtype={'url': str}, low_memory=False)
        data['label'] = pd.to_numeric(data['label'], errors='coerce').fillna(-1)  # Handle non-numeric labels gracefully

        # Parallelize feature extraction
        results = Parallel(n_jobs=-1)(
            delayed(extract_features)(url.lower().replace('www.', '')) for url in data['url']
        )
        features_df = pd.DataFrame(results)
        data = pd.concat([data, features_df], axis=1)

        scaler = StandardScaler()
        numeric_cols = [col for col in features_df.columns if 'hash' not in col]
        data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

        X_train, X_test, y_train, y_test = train_test_split(
            data.drop(['url', 'label'], axis=1), data['label'], test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test
    except Exception as e:
        print(f"Failed to preprocess data: {e}")
        raise

def train_model(X_train, y_train):
    try:
        #estimators is number of trees generated
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        print(f"Failed to train model: {e}")
        raise

def evaluate_model(model, X_test, y_test):
    try:
        y_pred = model.predict(X_test)
        class_report = classification_report(y_test, y_pred)
        print("Classification Report:")
        print(class_report)
        print("Accuracy Score:", accuracy_score(y_test, y_pred))
    except Exception as e:
        print(f"Failed to evaluate model: {e}")
        raise
def graph_data(y_test, y_pred): #graphs precision and accuracy
    class_report = classification_report(y_test,y_pred, output_dict=True)

    #precision and accuracy label on the x axis 
    pax = ['Precision (Weighted Avg)', 'Accuracy']
    pa_values = [class_report['weighted avg']['precision'], class_report['accuracy']]

    plt.figure(figsize=(10,6))
    plt.title("Precision and Accuracy")
    plt.yticks(np.arange(0, 1, 0.05))
    plt.bar(range(len(pa_values)), pa_values)
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.xticks(range(len(pax)), pax) 
    plt.show()

if __name__ == "__main__":
    filename = 'cleaned_data.csv'  # Make sure to replace with the actual filename
    try:
        X_train, X_test, y_train, y_test = preprocess_data(filename)
        model = train_model(X_train, y_train)
        evaluate_model(model, X_test, y_test)
        y_pred= model.predict(X_test)
        graph_data(y_test, y_pred)
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
