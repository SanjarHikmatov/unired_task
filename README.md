# Task by "Unired"

## 1. Clone the Repository
git clone https://github.com/SanjarHikmatov/unired_task.git
## 2. Change Directory
cd unired_task
## 3. Create .env file using .env.example
cp .env.example .env
## 4. Create a virtual environment using Python 3.10 
python3 -m venv venv 
## 5. Activate the Virtual Environment On Linux/MacOS
source venv/bin/activate
## 5. Activate the Virtual Environment On Windows
venv\Scripts\activate
## 6. Install Packages from requirements.txt Inside the Virtual Environment:
pip install -r requirements.txt

## 7. Run the makemigrations and apply the changes to the database:
./manage.py makemigrations
./manage.py migrate
## 8. To start the server, run the following command inside your Django project directory:
./manage.py runserver

## 9. Start Redis server (default port 6379):
redis-server --port 6380
# If using custom port (e.g., 6380):
# redis-server --port 6380

## 10. Start Celery worker for processing tasks:
celery -A config worker --loglevel=info
# -A config  -> your Django project celery app
# --loglevel=info  -> show logs

## 11. Start Celery Beat scheduler (for periodic tasks):
celery -A config beat --loglevel=info

## 12. Start Celery worker with Beat together (one command):
celery -A config worker --beat --loglevel=info
# This will run both the worker and the scheduler in the same process

# Available APIs

1. Transfer (create, confirm, cancel)
   [http://127.0.0.1:8000/transfer/jsonrpc/(http://127.0.0.1:8000/transfer/)# My Project

2. Card (info)
   [http://127.0.0.1:8000/card/card-info/(http://127.0.0.1:8000/card/)

