from flask import Flask
import os
from flask_smorest import Api
from .publicBlueprint import publicBLP

def create_application():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TBSplat'
    app.config["API_TITLE"] = "TBS REST API"
    app.config["API_VERSION"] = "v1"
    

    #MySQL configuration
    app.config['MYSQL_HOST'] = 'localhost'  
    app.config['MYSQL_USER'] = 'root'  
    app.config['MYSQL_PASSWORD'] = 'asma'  
    app.config['MYSQL_DB'] = 'e_tbs' 

    # Connect to MySQL
    from flask_mysqldb import MySQL
    mysql = MySQL(app)
    # Attach mysql to the app
    app.mysql = mysql
    
    app.register_blueprint(publicBLP, url_prefix='/')
    
    return app
   
    
