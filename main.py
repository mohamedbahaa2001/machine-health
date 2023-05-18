from flask import Flask, request, jsonify, render_template, send_from_directory
import joblib
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Load the trained model
model = joblib.load('trained_model.joblib')

# Load the label encoder
label_encoder = joblib.load('label_encoder.joblib')

# Define the column order used during training
column_order = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
unique_failure_types = [
    'No Failure',
    'Power Failure',
    'Tool Wear Failure',
    'Overstrain Failure',
    'Random Failures',
    'Heat Dissipation Failure'
]

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()  # Get the JSON data from the request
    
    # Create a DataFrame from the JSON data
    new_data = pd.DataFrame(data)
    
    # Map 'Type' values to numerical representation
    type_mapping = {'M': 0, 'L': 1, 'H': 2}
    new_data['Type'] = new_data['Type'].map(type_mapping)
    
    # Make predictions
    prediction = model.predict(new_data)
    predicted_failure_type = label_encoder.inverse_transform(prediction)
    
    # Prepare the response
    response = {'predicted_failure_type': predicted_failure_type.tolist()}
    
    return jsonify(response)
@app.route('/predict', methods=['POST'])
def predict(data=None):
    data = request.get_json()  # Get the JSON data from the request
    # Create a DataFrame from the JSON data
    new_data = pd.DataFrame(data, index=[0])
    # Fill the DataFrame with the JSON data
    for column in column_order:
        if column in data:
            new_data[column] = [data[column]]
        else:
            new_data[column] = [None]
    # Map 'Type' values to numerical representation
    type_mapping = {'M': 0, 'L': 1, 'H': 2}
    new_data['Type'] = new_data['Type'].map(type_mapping)
    
    # Make predictions
    prediction = model.predict(new_data)
    # Prepare the response
    response = unique_failure_types[int(prediction[0]) - 1]
    return jsonify({'prediction': response})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        return predict(data)
    return render_template('index.html')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csvFile' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['csvFile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Load the CSV file into a DataFrame
        data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Apply the same preprocessing logic as in the predict() function
        type_mapping = {'M': 0, 'L': 1, 'H': 2}
        data['Type'] = data['Type'].map(type_mapping)

        # Make predictions
        predictions = model.predict(data)
        predicted_failure_types = [unique_failure_types[int(prediction) - 1] for prediction in predictions]

        return jsonify({'predictions': predicted_failure_types})

    return jsonify({'error': 'Invalid file format'}), 400
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000,debug=True)
