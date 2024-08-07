from flask import Flask, request, render_template, jsonify, send_from_directory
import pandas as pd
from pycaret.regression import load_model, predict_model
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Import the scraping and model training functions
from pipelines.scraping_mobil123 import scheduled_scraping_job
from pipelines.preprocessing import preprocess_data
from pipelines.modelling import modelling as model_training

app = Flask(__name__)

# File path for prediction history
history_file_path = 'data/prediction_history.csv'

@app.route('/data/<path:filename>')
def download_file(filename):
    return send_from_directory(directory='data', path=filename)

def load_current_model(model_path):
    try:
        model = load_model(model_path)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")

def save_prediction_to_history(data, predicted_price):
    """Save the prediction data to the history CSV file."""
    try:
        data['predicted_price'] = predicted_price
        df_new = pd.DataFrame([data])
        
        if not os.path.isfile(history_file_path):
            df_new.to_csv(history_file_path, index=False)
        else:
            df = pd.read_csv(history_file_path)
            df_combined = pd.concat([df, df_new], ignore_index=True)
            df_combined.to_csv(history_file_path, index=False)
    except Exception as e:
        print(f"Error saving prediction to history: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    model = load_current_model('models/best_model')
    try:
        data = {
            'brand': request.form['brand'],
            'jenis_mobil': request.form['jenis_mobil'],
            'tahun_kendaraan': int(request.form['tahun_kendaraan']),
            'warna': request.form['warna'],
            'transmisi': request.form['transmisi'],
            'kilometer': int(request.form['kilometer']),
            'mesin_enginecc': int(request.form['mesin_enginecc']),
            'bahan_bakar': request.form['bahan_bakar'],
            'dirakit': request.form['dirakit'],
            'penumpang': int(request.form['penumpang']),
            'pintu': int(request.form['pintu'])
        }
        
        df = pd.DataFrame([data])
        
        # Predict car price
        prediction = predict_model(model, data=df)
        predicted_price = prediction['prediction_label'][0]
        
        # Save the prediction to history
        save_prediction_to_history(data, predicted_price)
        
        response = {
            'predicted_price': f'Rp {predicted_price:,.2f}'
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

@app.route('/car_list')
def car_list():
    try:
        # Load data from a CSV file or database
        data = pd.read_csv('data/clean_data.csv')
        cars = data.to_dict(orient='records')
        return render_template('car_list.html', cars=cars)
    except Exception as e:
        print(f"Error loading car list: {e}")
        return render_template('car_list.html', cars=[])


@app.route('/history')
def history():
    try:
        if os.path.isfile(history_file_path):
            history_df = pd.read_csv(history_file_path)
            history_records = history_df.to_dict(orient='records')
        else:
            history_records = []
        return render_template('history.html', history=history_records)
    except Exception as e:
        print(f"Error loading history: {e}")
        return render_template('history.html', history=[])

# Schedule scraping and model training
##scheduler = BackgroundScheduler()

#def update_model_and_scrape():
    scheduled_scraping_job()
    model_training()
    load_current_model('models/best_model')

#scheduler.add_job(func=update_model_and_scrape, trigger=CronTrigger(hour=22, minute=59))
#scheduler.start()

# Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)
