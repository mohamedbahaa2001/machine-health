import requests
import json

# Define the URL of the Flask endpoint
url = 'http://localhost:3000/api'

# Define the data to send in the request
data = {
    'Type': ['L'],  # 'M', 'L', or 'H'
    'Air temperature [K]': [298.5],
    'Process temperature [K]': [309.0],
    'Rotational speed [rpm]': [1500],
    'Torque [Nm]': [40.5],
    'Tool wear [min]': [10]
}

# Convert the data to JSON
json_data = json.dumps(data)

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send the POST request
response = requests.post(url, data=json_data, headers=headers)

# Get the response JSON data
response_data = response.json()
unique_failure_types = [
    'No Failure',
    'Power Failure',
    'Tool Wear Failure',
    'Overstrain Failure',
    'Random Failures',
    'Heat Dissipation Failure'
]
# Print the predicted failure type
outputs = response_data['predicted_failure_type']
for output in outputs:
    print(unique_failure_types[output - 1])
