from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ads_user:ads_password@localhost:5431/ads_db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    owner = db.relationship('User', backref=db.backref('ads', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Ads API!'}), 200

@app.route('/ads', methods=['POST'])
@login_required
def create_ad():
    data = request.get_json()
    new_ad = Ad(
        title=data['title'],
        description=data['description'],
        owner_id=current_user.id
    )
    db.session.add(new_ad)
    db.session.commit()
    return jsonify({'message': 'Ad created successfully!'}), 201

@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return jsonify({
        'title': ad.title,
        'description': ad.description,
        'created_at': ad.created_at,
        'owner': ad.owner.email
    })

@app.route('/ads/<int:ad_id>', methods=['DELETE'])
@login_required
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if ad.owner_id != current_user.id:
        abort(403)
    db.session.delete(ad)
    db.session.commit()
    return jsonify({'message': 'Ad deleted successfully!'})

@app.route('/ads/<int:ad_id>', methods=['PUT'])
@login_required
def update_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if ad.owner_id != current_user.id:
        abort(403)
    data = request.get_json()
    ad.title = data.get('title', ad.title)
    ad.description = data.get('description', ad.description)
    db.session.commit()
    return jsonify({'message': 'Ad updated successfully!'})

# User registration and login
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists!'}), 400
    new_user = User(email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    login_user(user)
    return jsonify({'message': 'Logged in successfully!'})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
