# Job Easy

Job Easy is a web application designed to simplify the job search process. This application helps users find job listings, manage applications, and track their job search progress.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

- Browse job listings
- Apply for jobs
- Track application status
- Manage job search progress

## Installation

### Prerequisites

- Python 3.x
- Django
- MySQL

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/sai-harsha-k/Job-Easy.git
    cd Job-Easy/jobeasy
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure MySQL settings in `jobeasy/settings.py`.

5. Apply migrations:
    ```bash
    python manage.py migrate
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

Once the server is running, open your web browser and navigate to `http://127.0.0.1:8000` to access the Job Easy application.

## Project Structure

- `core/`: Contains the core Django application files including models, views, and URLs.
  - `models.py`: Defines the database models including user profiles and job details.
  - `views.py`: Contains the logic for handling user requests and responses.
  - `urls.py`: Maps URLs to corresponding views.
  - `admin.py`: Configures the Django admin interface.
- `jobeasy/`: Contains the main application logic and configurations.
  - `settings.py`: Django settings configuration file, including MySQL database settings.
  - `urls.py`: Root URL configuration for the Django project.
  - `wsgi.py`: Web Server Gateway Interface configuration for deploying the project.
  - `asgi.py`: Asynchronous Server Gateway Interface configuration for deploying the project.
- `manage.py`: Django's command-line utility for administrative tasks.
- `staticfiles/`: Directory for static files (e.g., CSS, JavaScript, images).
- `templates/`: Directory for HTML templates used in rendering web pages.
  - `index.html`: Main page template.
  - `dashboard.html`: User dashboard template.
  - `job_recommendations.html`: Template for displaying job recommendations.
- `media/`: Directory for uploaded files such as user resumes.
- `ml_models/`: Directory containing serialized machine learning models and vectorizers.
  - `vectorizer_I-E.pkl`: TF-IDF vectorizer for I-E dimension.
  - `vectorizer_N-S.pkl`: TF-IDF vectorizer for N-S dimension.
  - `vectorizer_T-F.pkl`: TF-IDF vectorizer for T-F dimension.
  - `vectorizer_J-P.pkl`: TF-IDF vectorizer for J-P dimension.
  - `I-E_LogisticRegression.pkl`: Serialized Logistic Regression model for I-E dimension.
  - `N-S_CatBoost.pkl`: Serialized CatBoost model for N-S dimension.
  - `T-F_SVM.pkl`: Serialized SVM model for T-F dimension.
  - `J-P_XGBoost.pkl`: Serialized XGBoost model for J-P dimension.
- `scripts/`: Directory for utility scripts and data preprocessing.
  - `preprocess.py`: Script for preprocessing text data.
  - `train_models.py`: Script for training and saving machine learning models.
  - `evaluate_models.py`: Script for evaluating models and generating ROC and precision-recall curves.
- `data/`: Directory for storing datasets used in the project.
  - `mbti_1.csv`: Dataset containing MBTI types and text posts.
  - `skills.csv`: Dataset containing a list of skills.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.
