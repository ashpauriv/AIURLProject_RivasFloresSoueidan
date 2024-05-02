import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from joblib import Parallel, delayed
from tldextract import extract
from xgboost import XGBClassifier  # Add this import statement
import time
from memory_profiler import memory_usage

def extract_features(url):
    ext = extract(url)
    return {
        'length': len(url),
        'num_special_chars': sum(not c.isalnum() for c in url),
        'contains_login': int('login' in url),
        'contains_free': int('free' in url),
        'contains_click_here': int('click here' in url),
        'is_https': int(url.startswith('https')),
        'domain_hash': hash(ext.domain),
        'tld_hash': hash(ext.suffix),
        'num_subdomains': len(ext.subdomain.split('.')) if ext.subdomain else 0
    }

def preprocess_data(filename):
    try:
        data = pd.read_csv(filename, header=None, names=['url', 'label'], dtype={'url': str}, low_memory=False)
        
        # Drop rows with missing values
        data.dropna(inplace=True)
        
        # Encode labels: 'bad' as 1 (malicious) and 'good' as 0 (benign)
        label_encoder = LabelEncoder()
        data['label'] = label_encoder.fit_transform(data['label'])
        
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
        model = XGBClassifier(n_estimators=100, random_state=42)  # Use XGBClassifier
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        print(f"Failed to train model: {e}")
        raise

def evaluate_model(model, X_test, y_test):
    try:
        y_pred = model.predict(X_test)
        print("Classification Report:")
        print(classification_report(y_test, y_pred))
        print("Accuracy Score:", accuracy_score(y_test, y_pred))
    except Exception as e:
        print(f"Failed to evaluate model: {e}")
        raise

if __name__ == "__main__":
    filename = 'cleaned_data.csv'
    try:
        start_time = time.time()
        X_train, X_test, y_train, y_test = preprocess_data(filename)
        model = train_model(X_train, y_train)
        evaluate_model(model, X_test, y_test)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        mem_usage = memory_usage((preprocess_data, (filename,)))
        print(f"Peak memory usage: {max(mem_usage)} MB")
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")