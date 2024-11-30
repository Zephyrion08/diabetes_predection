import os
import numpy as np
import pandas as pd
import re
import matplotlib
matplotlib.use('Agg')  # Ensures Matplotlib works in a headless environment
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from django.views.decorators.csrf import csrf_exempt

# Project-specific imports
from .forms import BMICalculatorForm  # If a BMI calculator is used
from .utils import get_model_prediction, calculate_bmi, interpret_bmi, load_model  # Custom utility functions

data = pd.read_csv('project_diabetes/static/diabetes_dataset.csv')
X=data.drop(columns='Outcome',axis=1)
Y=data['Outcome']

scaler=StandardScaler()
scaler.fit(X)

standardized_data=scaler.transform(X)

X=standardized_data
Y=data['Outcome']
#train test split
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.2, stratify=Y, random_state=2)


# Load models and scaler dynamically
SVMmodel = load_model('svc', settings.BASE_DIR)
lrmodel = load_model('LRmodel', settings.BASE_DIR)
scaler = load_model('scaler.pkl', settings.BASE_DIR)

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            messages.success(request, "Login successful!")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("login")

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Password Match Check
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        # Password Strength Check
        

        # Username Existence Check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        # Email Format and Existence Check
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, email):
            messages.error(request, "Invalid email format!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        # Create User
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect("index")
        except Exception as e:
            messages.error(request, "An error occurred during registration. Please try again.")
            # Log error for debugging
            print(f"Error creating user: {e}")
            return redirect("register")

    return render(request, "register.html")

@login_required
def prediction(request):
    if request.method == "POST":
        input_features = [
            request.POST.get(key)
            for key in ['pregnancies', 'glucose', 'bloodPressure', 
                        'skinThickness', 'insulin', 'bmi', 
                        'diabetesPedigreeFunction', 'age']
        ]
        input_data = np.array(input_features, dtype=float).reshape(1, -1)

        # Standardize input data
        standardized_input = scaler.transform(input_data)

        model_select = request.POST.get('model_select')
        results = []

        # Store predictions for each model
        if model_select in ['SVM', 'Both']:
            svm_prediction = get_model_prediction(standardized_input, SVMmodel, 'SVM')
            results.append(f"From SVM: {svm_prediction}")
        
        if model_select in ['LR', 'Both']:
            lr_prediction = get_model_prediction(standardized_input, lrmodel, 'LR')
            results.append(f"From LR: {lr_prediction}")

        # Join results to display in template
        prediction_result = " | ".join(results)

        # Determine if the prediction is diabetic or not (from any model)
        is_diabetic = "is diabetic" in prediction_result

        return render(request, 'prediction.html', {
            'pred': prediction_result,
            'is_diabetic': is_diabetic
        })

    return render(request, 'prediction.html')




@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def prediction_view(request):
    if request.method == 'POST':
        form = BMICalculatorForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            height = form.cleaned_data['height']
            bmi = calculate_bmi(weight, height)
            interpretation = interpret_bmi(bmi)
            return render(request, 'prediction.html', {'pred': interpretation})
    else:
        form = BMICalculatorForm()
    
    return render(request, 'prediction.html', {'form': form})

def faq(request):
    return render(request, 'faq.html')

def logout_view(request):
    django_logout(request)  # Log the user out
    messages.success(request, "You have been logged out.")
    return redirect('index')

def doctor(request):
    user = request.user
    context = {
        'name': user.get_full_name() if user.get_full_name() else user.username,
        'email': user.email,
    }
    return render(request, 'doctor.html', context)