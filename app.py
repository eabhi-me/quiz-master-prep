from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flasgger import Swagger
# seting the environment
from dotenv import load_dotenv
import os
load_dotenv()

# setting the application config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# setting the instances of different element
db = SQLAlchemy(app)
# an insatnace for encryption and hashing
bcrypt = Bcrypt(app)

api = Api(app)

migrate = Migrate(app, db)

# an instsnce to document the api docs
swagger = Swagger(app)
app.config['SWAGGER'] = {
    'title': 'Quiz API',
    'uiversion': 3,
    'specs_route': '/docs/'
}


# setting an login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# importing the components
from controllers.routes import *
from models.models import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# if __name__ == '__main__':
#     app.run(debug=True)

# deployment server
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
