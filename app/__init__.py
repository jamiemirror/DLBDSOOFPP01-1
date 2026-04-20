"""Application init/index for server """
from flask import Flask 
from app.db import Database
#create Flask Application
app = Flask(__name__)
#initialize Database
db_manager = Database()
#points to Routes
from app import routes