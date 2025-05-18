from flask import Flask
from backend import create_application

app = create_application()


with app.app_context():
    print(app.url_map)
    
if __name__ == '__main__' :
    app.run(debug=True)

