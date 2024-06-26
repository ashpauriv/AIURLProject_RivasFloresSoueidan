#!/usr/bin/env python3

import sys
import pandas as pd

def load_and_clean_data(filename):
    try:
        # Load data assuming the first row is the header
        data = pd.read_csv(filename)

        # Print the initial data to verify correct loading
        print("Initial data preview:")
        print(data.head())

        # Encode labels: 'bad' as 1 (malicious) and 'good' as 0 (benign)
        data['label'] = data['label'].map({'bad': 1, 'good': 0})

        # Drop duplicates
        data = data.drop_duplicates()

        # Print cleaned data preview to ensure it's correct
        print("\nData preview after cleaning:")
        print(data.head())
        print("\nTotal rows after cleaning:", len(data))
        print("\nDistribution of labels:")
        print(data['label'].value_counts())

        return data

    except FileNotFoundError:
        print("Error: The file was not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred:", e)
        sys.exit(1)

def save_cleaned_data(data, output_filename):
    # Explicitly set header and index options when saving to CSV
    data.to_csv(output_filename, index=False, header=True)
    print(f"\nCleaned data saved to {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleandata.py <filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    cleaned_data = load_and_clean_data(input_file)

    # Optionally save the cleaned data to a new file
    output_file = "cleaned_data.csv"
    save_cleaned_data(cleaned_data, output_file)
