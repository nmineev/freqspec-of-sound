# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    # create the app
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"]='dev'
    
    bootstrap = Bootstrap(app)
    
    from . import freqspec_builder
    app.register_blueprint(freqspec_builder.bp)
    
    return app