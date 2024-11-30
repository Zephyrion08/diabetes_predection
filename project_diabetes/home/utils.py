import joblib
import numpy as np
import os
from sklearn.preprocessing import StandardScaler

# Helper function to get prediction from the model
def get_model_prediction(input_data, model, model_name):
    prediction = model.predict(input_data)
    if prediction[0] == 0:
        return f'From {model_name}: The person is not diabetic'
    else:
        return f'From {model_name}: The person is diabetic'

# Function to calculate BMI
def calculate_bmi(weight_kg, height_m):
    return weight_kg / (height_m ** 2)

# Function to interpret BMI
def interpret_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# Function to load models dynamically
def load_model(file_name, base_dir):
    file_path = os.path.join(base_dir, 'static', file_name)
    return joblib.load(file_path)
