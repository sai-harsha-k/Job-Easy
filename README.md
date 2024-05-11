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

4. Apply migrations:
    ```bash
    python manage.py migrate
    ```

5. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

Once the server is running, open your web browser and navigate to `http://127.0.0.1:8000` to access the Job Easy application.

## Project Structure

- `core/`: Contains the core Django application files.
- `db.sqlite3`: SQLite database file.
- `jobeasy/`: Contains the main application logic and configurations.
- `manage.py`: Django's command-line utility for administrative tasks.
- `staticfiles/`: Directory for static files (e.g., CSS, JavaScript, images).

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.
