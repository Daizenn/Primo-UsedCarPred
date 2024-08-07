from pycaret.regression import *
import logging
import pandas as pd
from pipelines.preprocessing import preprocess_data

def modelling():
    # Load the dataset
    df = pd.read_csv('data/clean_data.csv')

    # Set up the PyCaret regression environment
    s = setup(df, target='harga', session_id=42)

    # Compare models and select the best one
    best = compare_models()

    # Plot residuals of the best model
    plot_model(best, plot='residuals')

    # Save the best model
    save_model(best, 'model/best_model')

if __name__ == "__main__":
    modelling()
