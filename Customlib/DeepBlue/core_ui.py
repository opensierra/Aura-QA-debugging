from flask import render_template
from .config import LANGUAGE_TAG, BASE_DIR
def build_routes(app):

    @app.route('/')
    def home():
        return render_template(
            'app.html', 
            language=LANGUAGE_TAG, 
            w_dir=BASE_DIR)