# app.py
from pathlib import Path
import os
from dotenv import dotenv_values

config = os.environ
if Path(".env").is_file():
  config = dotenv_values(".env")

from flask import Flask, request, jsonify, render_template
from translate_excel import translate_API

app = Flask(__name__, template_folder="templates")
app.register_blueprint(translate_API)
app.secret_key = config["SECRET_KEY"]

# A welcome message to test our server
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)