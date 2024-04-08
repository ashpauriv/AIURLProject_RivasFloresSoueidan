import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the dataset
data = pd.read_csv("data.csv")

print(data.head())
print(data.describe())

# Drop unnecessary columns
if 'Unnamed: 0' in data.columns:
    data.drop(['Unnamed: 0'], axis=1, inplace=True)
# Handle missing values (if any)
data.dropna(inplace=True)

# Encode the target variable
data['type'] = data['type'].map({'good': 0, 'bad': 1})

# Feature extraction from URLs
# You might want to add a custom regex pattern in TfidfVectorizer to capture URL tokens better
vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
X = vectorizer.fit_transform(data['url'])

# Split the data into features and target variable
y = data['type']

# Further split the data into training and testing sets, using stratify to preserve class distribution
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)