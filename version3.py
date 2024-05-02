import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import RandomOverSampler
from sklearn.preprocessing import LabelEncoder
import time
from memory_profiler import memory_usage

def preprocess_data(filename):
    try:
        data = pd.read_csv(filename)
        
        # Drop rows with missing values
        data.dropna(inplace=True)
        
        # Encode categorical variables
        label_encoder = LabelEncoder()
        data['url'] = label_encoder.fit_transform(data['url'])
        
        X = data.drop('label', axis=1)
        y = data['label']
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        return X_train, X_test, y_train, y_test
    except Exception as e:
        print(f"Failed to preprocess data: {e}")
        raise

def train_model(X_train, y_train):
    try:
        # Balancing the data
        oversampler = RandomOverSampler(random_state=42)
        X_train_resampled, y_train_resampled = oversampler.fit_resample(X_train, y_train)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_resampled, y_train_resampled)
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
    filename = '/Users/aminahsoueidan/Desktop/AI class/project/AIProjectMalwareDectection_RivasFloresSoueidan/cleaned_data.csv'
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