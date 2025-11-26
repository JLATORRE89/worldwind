"""
WorldWind Authentication Server
================================

Flask backend server providing:
- User registration and login (email/password)
- OAuth authentication (Google, Discord, Microsoft)
- User profile management
- Cloud sync for travels, photos, friends
- API for WorldWind clients (Unity, Python)
"""

from flask import Flask, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
import jwt
import datetime
import os
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///worldwind.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for Unity/Python clients
CORS(app)

# Initialize database
db = SQLAlchemy(app)

# Initialize OAuth
oauth = OAuth(app)

# Configure OAuth providers
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

discord = oauth.register(
    name='discord',
    client_id=os.environ.get('DISCORD_CLIENT_ID'),
    client_secret=os.environ.get('DISCORD_CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify email'}
)

microsoft = oauth.register(
    name='microsoft',
    client_id=os.environ.get('MICROSOFT_CLIENT_ID'),
    client_secret=os.environ.get('MICROSOFT_CLIENT_SECRET'),
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# Database Models
class User(db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)  # Null for OAuth users

    # OAuth fields
    oauth_provider = db.Column(db.String(20), nullable=True)  # google, discord, microsoft
    oauth_id = db.Column(db.String(200), nullable=True)

    # Profile
    display_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    travels = db.relationship('Travel', backref='user', lazy=True, cascade='all, delete-orphan')
    friends = db.relationship('Friend', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Travel(db.Model):
    """User travel/photo model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    photo_url = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'photo_url': self.photo_url,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'title': self.title,
            'description': self.description,
            'date': self.date
        }


class Friend(db.Model):
    """User friend model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    photo_url = db.Column(db.String(500), nullable=True)
    color = db.Column(db.String(20), default='yellow')
    group = db.Column(db.String(50), default='friends')

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'photo_url': self.photo_url,
            'color': self.color,
            'group': self.group
        }


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])

            if not current_user:
                return jsonify({'message': 'User not found'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Helper function to generate JWT token
def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user with email/password"""
    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    # Create new user
    user = User(email=email, username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = generate_token(user.id)

    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username
        }
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Login with email/password"""
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Update last login
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    # Generate token
    token = generate_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name
        }
    })


# OAuth Routes - Google
@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth"""
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def auth_google_callback():
    """Google OAuth callback"""
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)

    # Find or create user
    user = User.query.filter_by(oauth_provider='google', oauth_id=user_info['sub']).first()

    if not user:
        # Create new OAuth user
        user = User(
            email=user_info['email'],
            username=user_info['email'].split('@')[0],
            oauth_provider='google',
            oauth_id=user_info['sub'],
            display_name=user_info.get('name'),
            avatar_url=user_info.get('picture')
        )
        db.session.add(user)
        db.session.commit()

    # Update last login
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    # Generate token
    token = generate_token(user.id)

    # Return token (in production, redirect to app with token)
    return jsonify({
        'message': 'Google login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name
        }
    })


# OAuth Routes - Discord
@app.route('/auth/discord')
def auth_discord():
    """Initiate Discord OAuth"""
    redirect_uri = url_for('auth_discord_callback', _external=True)
    return discord.authorize_redirect(redirect_uri)


@app.route('/auth/discord/callback')
def auth_discord_callback():
    """Discord OAuth callback"""
    token = discord.authorize_access_token()
    resp = discord.get('users/@me')
    user_info = resp.json()

    # Find or create user
    user = User.query.filter_by(oauth_provider='discord', oauth_id=user_info['id']).first()

    if not user:
        email = user_info.get('email', f"{user_info['id']}@discord.user")
        user = User(
            email=email,
            username=user_info['username'],
            oauth_provider='discord',
            oauth_id=user_info['id'],
            display_name=user_info.get('global_name', user_info['username']),
            avatar_url=f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png" if user_info.get('avatar') else None
        )
        db.session.add(user)
        db.session.commit()

    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    token = generate_token(user.id)

    return jsonify({
        'message': 'Discord login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name
        }
    })


# OAuth Routes - Microsoft
@app.route('/auth/microsoft')
def auth_microsoft():
    """Initiate Microsoft OAuth"""
    redirect_uri = url_for('auth_microsoft_callback', _external=True)
    return microsoft.authorize_redirect(redirect_uri)


@app.route('/auth/microsoft/callback')
def auth_microsoft_callback():
    """Microsoft OAuth callback"""
    token = microsoft.authorize_access_token()
    user_info = microsoft.parse_id_token(token)

    # Find or create user
    user = User.query.filter_by(oauth_provider='microsoft', oauth_id=user_info['oid']).first()

    if not user:
        user = User(
            email=user_info['email'],
            username=user_info['email'].split('@')[0],
            oauth_provider='microsoft',
            oauth_id=user_info['oid'],
            display_name=user_info.get('name'),
            avatar_url=None
        )
        db.session.add(user)
        db.session.commit()

    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    token = generate_token(user.id)

    return jsonify({
        'message': 'Microsoft login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name
        }
    })


# ============================================================================
# USER PROFILE ROUTES
# ============================================================================

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'username': current_user.username,
        'display_name': current_user.display_name,
        'avatar_url': current_user.avatar_url,
        'oauth_provider': current_user.oauth_provider,
        'created_at': current_user.created_at.isoformat(),
        'travels_count': len(current_user.travels),
        'friends_count': len(current_user.friends)
    })


@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    data = request.get_json()

    if 'display_name' in data:
        current_user.display_name = data['display_name']

    if 'avatar_url' in data:
        current_user.avatar_url = data['avatar_url']

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'})


# ============================================================================
# TRAVEL/PHOTO ROUTES
# ============================================================================

@app.route('/api/travels', methods=['GET'])
@token_required
def get_travels(current_user):
    """Get all travels for current user"""
    travels = [travel.to_dict() for travel in current_user.travels]
    return jsonify({'travels': travels})


@app.route('/api/travels', methods=['POST'])
@token_required
def create_travel(current_user):
    """Create new travel/photo"""
    data = request.get_json()

    travel = Travel(
        user_id=current_user.id,
        photo_url=data.get('photo_url'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        title=data.get('title'),
        description=data.get('description'),
        date=data.get('date')
    )

    db.session.add(travel)
    db.session.commit()

    return jsonify({
        'message': 'Travel created successfully',
        'travel': travel.to_dict()
    }), 201


@app.route('/api/travels/<int:travel_id>', methods=['DELETE'])
@token_required
def delete_travel(current_user, travel_id):
    """Delete a travel"""
    travel = Travel.query.get(travel_id)

    if not travel or travel.user_id != current_user.id:
        return jsonify({'error': 'Travel not found'}), 404

    db.session.delete(travel)
    db.session.commit()

    return jsonify({'message': 'Travel deleted successfully'})


# ============================================================================
# FRIEND ROUTES
# ============================================================================

@app.route('/api/friends', methods=['GET'])
@token_required
def get_friends(current_user):
    """Get all friends for current user"""
    friends = [friend.to_dict() for friend in current_user.friends]
    return jsonify({'friends': friends})


@app.route('/api/friends', methods=['POST'])
@token_required
def create_friend(current_user):
    """Create new friend"""
    data = request.get_json()

    friend = Friend(
        user_id=current_user.id,
        name=data.get('name'),
        city=data.get('city'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        photo_url=data.get('photo_url'),
        color=data.get('color', 'yellow'),
        group=data.get('group', 'friends')
    )

    db.session.add(friend)
    db.session.commit()

    return jsonify({
        'message': 'Friend created successfully',
        'friend': friend.to_dict()
    }), 201


@app.route('/api/friends/<int:friend_id>', methods=['DELETE'])
@token_required
def delete_friend(current_user, friend_id):
    """Delete a friend"""
    friend = Friend.query.get(friend_id)

    if not friend or friend.user_id != current_user.id:
        return jsonify({'error': 'Friend not found'}), 404

    db.session.delete(friend)
    db.session.commit()

    return jsonify({'message': 'Friend deleted successfully'})


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'WorldWind Auth Server'})


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")

    print("=" * 60)
    print("WorldWind Authentication Server")
    print("=" * 60)
    print("\nEndpoints available:")
    print("  POST   /api/register          - Register with email/password")
    print("  POST   /api/login             - Login with email/password")
    print("  GET    /auth/google           - Login with Google")
    print("  GET    /auth/discord          - Login with Discord")
    print("  GET    /auth/microsoft        - Login with Microsoft")
    print("  GET    /api/profile           - Get user profile")
    print("  GET/POST /api/travels         - Manage travels")
    print("  GET/POST /api/friends         - Manage friends")
    print("\nServer running on http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
