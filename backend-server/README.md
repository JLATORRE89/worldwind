# WorldWind Authentication Server 🔐

Backend server providing user authentication, cloud sync, and API for WorldWind clients.

## Features

✅ **Multiple Authentication Methods:**
- Email/Password registration and login
- Google OAuth
- Discord OAuth
- Microsoft OAuth

✅ **User Management:**
- User profiles with avatars
- Secure password hashing
- JWT token-based authentication
- Session management

✅ **Cloud Sync:**
- Sync travels/photos across devices
- Sync friends across devices
- Auto-save to cloud
- Multi-device support

✅ **API for Clients:**
- RESTful API
- CORS enabled for web/Unity clients
- JSON responses
- Secure token authentication

## Quick Start

### 1. Install Dependencies

```bash
cd backend-server
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your OAuth credentials (see below for setup).

### 3. Run Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

## OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs: `http://localhost:5000/auth/google/callback`
7. Copy Client ID and Client Secret to `.env`

### Discord OAuth

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "OAuth2" tab
4. Add redirect: `http://localhost:5000/auth/discord/callback`
5. Copy Client ID and Client Secret to `.env`

### Microsoft OAuth

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Add redirect URI: `http://localhost:5000/auth/microsoft/callback`
5. Go to "Certificates & secrets" → Create new client secret
6. Copy Application (client) ID and secret to `.env`

## API Endpoints

### Authentication

```
POST   /api/register          - Register with email/password
POST   /api/login             - Login with email/password
GET    /auth/google           - Login with Google
GET    /auth/discord          - Login with Discord
GET    /auth/microsoft        - Login with Microsoft
```

### User Profile

```
GET    /api/profile           - Get user profile
PUT    /api/profile           - Update user profile
```

### Travels

```
GET    /api/travels           - Get all travels
POST   /api/travels           - Create new travel
DELETE /api/travels/:id       - Delete travel
```

### Friends

```
GET    /api/friends           - Get all friends
POST   /api/friends           - Create new friend
DELETE /api/friends/:id       - Delete friend
```

## API Usage Examples

### Register

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myusername",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "myusername"
  }
}
```

### Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Get Profile (with token)

```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create Travel

```bash
curl -X POST http://localhost:5000/api/travels \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 48.8566,
    "longitude": 2.3522,
    "title": "Paris Trip",
    "description": "Amazing vacation!",
    "date": "2024-06-15",
    "photo_url": "https://example.com/photo.jpg"
  }'
```

## Database Schema

### User Table
- `id` - Primary key
- `email` - Unique email
- `username` - Unique username
- `password_hash` - Hashed password (null for OAuth users)
- `oauth_provider` - google/discord/microsoft (null for email users)
- `oauth_id` - OAuth user ID
- `display_name` - Display name
- `avatar_url` - Avatar URL
- `created_at` - Registration date
- `last_login` - Last login date

### Travel Table
- `id` - Primary key
- `user_id` - Foreign key to User
- `photo_url` - Photo URL
- `latitude` - Latitude
- `longitude` - Longitude
- `title` - Title
- `description` - Description
- `date` - Date
- `created_at` - Creation date

### Friend Table
- `id` - Primary key
- `user_id` - Foreign key to User
- `name` - Friend name
- `city` - City
- `latitude` - Latitude
- `longitude` - Longitude
- `photo_url` - Photo URL
- `color` - Marker color
- `group` - Friend group
- `created_at` - Creation date

## Security

### Password Security
- Passwords hashed using Werkzeug's `generate_password_hash`
- Uses PBKDF2-SHA256 algorithm
- Salted hashes

### Token Security
- JWT tokens with HS256 algorithm
- 30-day expiration
- Tokens required for all protected endpoints

### OAuth Security
- Uses Authlib for secure OAuth flows
- Validates OAuth tokens
- Stores OAuth IDs securely

## Production Deployment

### Database

For production, use PostgreSQL:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:pass@localhost/worldwind
```

### Security

1. **Change SECRET_KEY**:
   ```bash
   # Generate secure key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use HTTPS**:
   - Deploy behind nginx/Apache with SSL
   - Update OAuth redirect URIs to https://

3. **Environment Variables**:
   - Never commit `.env` file
   - Use environment variables in production

### Deployment Options

**Option 1: Heroku**
```bash
heroku create worldwind-auth
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**Option 2: Docker**
```bash
docker build -t worldwind-auth .
docker run -p 5000:5000 worldwind-auth
```

**Option 3: VPS (DigitalOcean, AWS, etc.)**
- Use gunicorn: `gunicorn -w 4 app:app`
- Configure nginx reverse proxy
- Set up SSL with Let's Encrypt

## Client Integration

### Python Client

```python
from worldwind_auth import WorldWindAuth

# Initialize
auth = WorldWindAuth('http://localhost:5000')

# Login
auth.login('user@example.com', 'password')

# Get travels
travels = auth.get_travels()

# Create travel
auth.create_travel(
    latitude=48.8566,
    longitude=2.3522,
    title="Paris",
    photo_url="http://example.com/photo.jpg"
)
```

### Unity Client

```csharp
// Get component
WorldWindAuthClient auth = GetComponent<WorldWindAuthClient>();

// Login
auth.Login("user@example.com", "password", (success, message) => {
    if (success) {
        Debug.Log("Logged in!");
    }
});

// Get travels
auth.GetTravels((travels) => {
    foreach (var travel in travels) {
        // Add to globe
        globe.CreatePhotoPlacemark(
            travel.latitude,
            travel.longitude,
            travel.title
        );
    }
});
```

## Development

### Run in Development Mode

```bash
python app.py
```

Server runs with debug mode enabled.

### Database Migrations

```bash
# Create all tables
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

### Testing

```bash
# Test registration
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# Test health
curl http://localhost:5000/health
```

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "OAuth not configured"
Check `.env` file has OAuth credentials set.

### "Database locked" (SQLite)
SQLite doesn't handle concurrent writes well. Use PostgreSQL for production.

### "CORS error"
Add your client origin to CORS configuration in `app.py`.

## License

MIT License

## Support

For issues or questions, check the main WorldWind repository.
