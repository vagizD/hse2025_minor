from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.utils import get_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Для сессий и CSRF защиты
CORS(app)  # Разрешаем CORS для разработки

# Database configuration
engine = create_engine(get_url())
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

from app import routes
