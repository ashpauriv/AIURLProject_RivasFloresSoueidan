import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import tldextract
from concurrent.futures import ProcessPoolExecutor

def extract_features(url):
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
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(extract_features, data['url'].str.lower().str.replace('www.', '').tolist()))

        features_df = pd.DataFrame(results)
        data = pd.concat([data, features_df], axis=1)

        scaler = StandardScaler()
        numeric_cols = [col for col in features_df.columns if 'hash' not in col]
        data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

        X_train, X_test, y_train, y_test = train_test_split(
            data.drop(['url', 'label'], axis=1), data['label'], test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test, data
    except Exception as e:
        print(f"Failed to preprocess data: {e}")
        raise

def train_model(X_train, y_train):
    try:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
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
        return y_pred
    except Exception as e:
        print(f"Failed to evaluate model: {e}")
        raise

def visualize_feature_importance(model, X_train, top_n=10):
    feature_importance = model.feature_importances_
    sorted_idx = np.argsort(feature_importance)[::-1]
    feature_names = X_train.columns

    plt.figure(figsize=(10, 6))
    plt.bar(range(top_n), feature_importance[sorted_idx[:top_n]], align='center')
    plt.xticks(range(top_n), feature_names[sorted_idx[:top_n]], rotation=45)
    plt.title("Top {} Most Important Features".format(top_n))
    plt.xlabel('Features')
    plt.ylabel('Importance')
    plt.show()

if __name__ == "__main__":
    filename = '/Users/aminahsoueidan/Desktop/AI class/project/AIProjectMalwareDectection_RivasFloresSoueidan/cleaned_data.csv'  # Make sure to replace with the actual filename
    try:
        X_train, X_test, y_train, y_test, data = preprocess_data(filename)
        model = train_model(X_train, y_train)
        y_pred = evaluate_model(model, X_test, y_test)
        
        visualize_feature_importance(model, X_train, top_n=9)  # Top 9 features
        
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")