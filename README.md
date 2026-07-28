## Setup & Run Instructions

### 1. Terminal1
cd backend
pip3 install -r requirements.txt
python app.py

### Terminal2(wsl)
sudo service redis-server start
redis-cli ping

### Terminal3(wsl)
pip3 install --break-system-packages --upgrade vine celery redis flask flask-sqlalchemy flask-jwt-extended flask-cors flask-caching flask-restful jinja2 requests
cd backend
celery -A app.celery worker --loglevel=info

### Terminal4(wsl)
cd backend
celery -A app.celery beat --loglevel=info

### Terminal5(Email Server) (wsl)
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
./MailHog_linux_amd64
http://localhost:8025

### Terminal6(wsl)
cd frontend
npm install
npm run dev