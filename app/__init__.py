from flask import Flask

app = Flask(__name__)

from app.config import Config
app.config.from_object(Config)

from app import routes