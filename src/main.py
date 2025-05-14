from flask import Flask, render_template
from dotenv import load_dotenv
import os

from api.routes import api
from api.utils import ensure_upload_folder

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config.from_object('config.default')

# Ensure upload folder exists
ensure_upload_folder(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api/v1')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 