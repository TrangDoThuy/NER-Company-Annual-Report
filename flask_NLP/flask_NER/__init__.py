from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///annual_reports.db'
app.config['SECRET_KEY'] = 'e056ff842ed2b9c80b505e33912ff182'
db = SQLAlchemy(app)
from flask_NER import routes