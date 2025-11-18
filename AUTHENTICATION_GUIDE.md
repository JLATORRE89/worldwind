# WorldWind Authentication & Cloud Sync Guide 🔐☁️

Complete guide to user accounts, authentication, and cloud synchronization for WorldWind.

---

## 🎯 What You Get with User Accounts

### ✨ Features

- **Multiple Login Options:**
  - ✅ Email & Password
  - ✅ Google Account
  - ✅ Discord Account
  - ✅ Microsoft Account

- **Cloud Sync:**
  - ✅ Save your travels to the cloud
  - ✅ Save your friends list
  - ✅ Access from any device
  - ✅ Auto-sync across Unity and Python clients

- **User Profile:**
  - ✅ Username and display name
  - ✅ Avatar/profile picture
  - ✅ Account statistics
  - ✅ Privacy controls

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Setup Backend Server](#setup-backend-server)
3. [Using Authentication (Python)](#python-authentication)
4. [Using Authentication (Unity)](#unity-authentication)
5. [OAuth Setup](#oauth-setup)
6. [Cloud Sync Usage](#cloud-sync-usage)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Users (No Server Setup)

If you just want to use WorldWind with cloud sync, you can use a hosted server (if available).

**Python:**
```bash
python worldwind_auth.py
# Follow prompts to register or login
```

**Unity:**
1. Add `WorldWindAuthClient` component to a GameObject
2. Use the login UI or call login methods from code

### For Developers (Run Your Own Server)

1. **Setup Backend:**
   ```bash
   cd backend-server
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   python app.py
   ```

2. **Use Clients:**
   - Python: `python worldwind_auth.py`
   - Unity: Add `WorldWindAuthClient` component

---

## Setup Backend Server

### Step 1: Install Dependencies

```bash
cd backend-server
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Minimal configuration (for testing):
```env
SECRET_KEY=change-this-to-random-string
DATABASE_URL=sqlite:///worldwind.db
```

### Step 3: Run Server

```bash
python app.py
```

Output:
```
✓ Database tables created
====================================
WorldWind Authentication Server
====================================

Endpoints available:
  POST   /api/register
  POST   /api/login
  GET    /auth/google
  ...

Server running on http://localhost:5000
====================================
```

### Step 4: Test Server

```bash
curl http://localhost:5000/health
```

Response:
```json
{"status": "ok", "service": "WorldWind Auth Server"}
```

---

## Python Authentication

### Installation

```bash
# Dependencies already in requirements.txt
pip install requests
```

### Basic Usage

```python
from worldwind_auth import WorldWindAuth

# Connect to server
auth = WorldWindAuth('http://localhost:5000')

# Register new user
auth.register(
    email='your@email.com',
    username='yourusername',
    password='securepassword'
)

# Or login
auth.login('your@email.com', 'securepassword')

# Check if authenticated
if auth.is_authenticated():
    print(f"Logged in as: {auth.user['username']}")
```

### OAuth Login

```python
# Google login
auth.login_google()
# Opens browser, complete login there

# After OAuth callback, manually set token:
token = input("Paste token from browser: ")
auth.set_token(token)
```

### Using with WorldWind

```python
from worldwind_with_photos import WorldWindWithPhotos
from worldwind_auth import WorldWindAuth

# Authenticate
auth = WorldWindAuth()
auth.login('your@email.com', 'password')

# Load travels from cloud
travels = auth.get_travels()

# Create globe
globe = WorldWindWithPhotos()

# Add travels to globe
for travel in travels:
    globe.add_travel_photo(
        photo_path=travel['photo_url'],  # Download from URL
        latitude=travel['latitude'],
        longitude=travel['longitude'],
        title=travel['title']
    )

# Add new travel and sync to cloud
auth.create_travel(
    latitude=48.8566,
    longitude=2.3522,
    photo_url='https://example.com/paris.jpg',
    title='Paris Trip',
    description='Amazing vacation!',
    date='2024-06-15'
)

app.run()
```

### Command-Line Authentication

Run the auth client directly:

```bash
python worldwind_auth.py
```

Interactive menu:
```
1) Register  2) Login  3) Google  4) Discord  5) Microsoft
Choice: 2

Email: your@email.com
Password: ********

✓ Logged in as yourusername

Profile:
  Username: yourusername
  Email: your@email.com
  Travels: 5
  Friends: 10
```

---

## Unity Authentication

### Setup

1. **Add Component:**
   - Create empty GameObject: "Authentication"
   - Add Component → `WorldWindAuthClient`
   - Set Server URL: `http://localhost:5000`

2. **Create Login UI** (optional):
   Create a simple UI with InputFields and Buttons

### Basic Usage (Code)

```csharp
// Get reference
WorldWindAuthClient auth = FindObjectOfType<WorldWindAuthClient>();

// Register
auth.Register("user@email.com", "username", "password", (success, message) => {
    if (success) {
        Debug.Log("Registered!");
    } else {
        Debug.LogError(message);
    }
});

// Login
auth.Login("user@email.com", "password", (success, message) => {
    if (success) {
        Debug.Log($"Logged in as {auth.username}!");
    }
});

// OAuth login
auth.LoginGoogle();  // Opens browser
// User completes login, gets token
// Call auth.SetToken("token") with the token
```

### Auto-Login on Start

```csharp
public class AutoLogin : MonoBehaviour
{
    private WorldWindAuthClient auth;

    void Start()
    {
        auth = FindObjectOfType<WorldWindAuthClient>();

        // Wait a frame for auto-login from saved token
        StartCoroutine(CheckLogin());
    }

    IEnumerator CheckLogin()
    {
        yield return new WaitForSeconds(1f);

        if (auth.isAuthenticated)
        {
            Debug.Log($"Auto-logged in as {auth.username}");
            LoadUserData();
        }
        else
        {
            ShowLoginUI();
        }
    }

    void LoadUserData()
    {
        // Load travels from cloud
        auth.GetTravels((travels) => {
            PhotoPlacemarkManager photoManager = FindObjectOfType<PhotoPlacemarkManager>();

            foreach (var travel in travels)
            {
                // Add to globe
                photoManager.AddPhotoPlacemark(
                    travel.photo_url,
                    travel.latitude,
                    travel.longitude,
                    travel.title,
                    travel.description,
                    travel.date
                );
            }
        });

        // Load friends
        auth.GetFriends((friends) => {
            FriendPlacemarkManager friendManager = FindObjectOfType<FriendPlacemarkManager>();

            foreach (var friend in friends)
            {
                friendManager.AddFriend(
                    friend.name,
                    friend.city,
                    friend.latitude,
                    friend.longitude,
                    friend.photo_url,
                    friend.color,
                    friend.group
                );
            }
        });
    }
}
```

### Sync to Cloud

```csharp
// When user adds a new travel photo
void OnPhotoAdded(TravelPhoto photo)
{
    // Create travel data
    var travelData = new WorldWindAuthClient.TravelData
    {
        latitude = photo.latitude,
        longitude = photo.longitude,
        title = photo.title,
        description = photo.description,
        date = photo.date,
        photo_url = UploadPhotoToCloud(photo.photoPath)  // Upload first
    };

    // Sync to cloud
    auth.CreateTravel(travelData, (createdTravel) => {
        if (createdTravel != null)
        {
            Debug.Log("✓ Synced to cloud!");
        }
    });
}
```

---

## OAuth Setup

### Why OAuth?

OAuth allows users to login with their existing accounts (Google, Discord, Microsoft) without creating a new password.

### Setting Up Google OAuth

1. **Go to Google Cloud Console:**
   https://console.cloud.google.com/

2. **Create Project:**
   - Click "Select a project" → "New Project"
   - Name: "WorldWind"
   - Click "Create"

3. **Enable Google+ API:**
   - Navigate to "APIs & Services" → "Library"
   - Search "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials:**
   - Go to "Credentials" → "Create Credentials"
   - Select "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "WorldWind Auth"

5. **Configure Redirect URIs:**
   - Authorized JavaScript origins: `http://localhost:5000`
   - Authorized redirect URIs: `http://localhost:5000/auth/google/callback`

6. **Copy Credentials:**
   - Copy Client ID
   - Copy Client Secret
   - Add to `.env` file

### Setting Up Discord OAuth

1. **Go to Discord Developer Portal:**
   https://discord.com/developers/applications

2. **Create Application:**
   - Click "New Application"
   - Name: "WorldWind"
   - Click "Create"

3. **Configure OAuth2:**
   - Go to "OAuth2" tab
   - Add Redirect: `http://localhost:5000/auth/discord/callback`
   - Scopes: Check "identify" and "email"

4. **Copy Credentials:**
   - Copy Client ID
   - Click "Reset Secret" → Copy Client Secret
   - Add to `.env` file

### Setting Up Microsoft OAuth

1. **Go to Azure Portal:**
   https://portal.azure.com/

2. **Register Application:**
   - Navigate to "Azure Active Directory"
   - Click "App registrations" → "New registration"
   - Name: "WorldWind"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:5000/auth/microsoft/callback`

3. **Create Client Secret:**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: "WorldWind Auth"
   - Copy the secret VALUE (not ID)

4. **Copy Credentials:**
   - Copy Application (client) ID
   - Copy client secret
   - Add to `.env` file

---

## Cloud Sync Usage

### Automatic Sync (Recommended)

```python
# Python
auth = WorldWindAuth()
auth.login('user@email.com', 'password')

# All travels/friends automatically sync
travels = auth.get_travels()  # Gets from cloud
auth.create_travel(...)  # Saves to cloud
```

```csharp
// Unity
auth.Login("email", "password", (success, msg) => {
    // On success, load from cloud
    auth.GetTravels(LoadTravelsToGlobe);
    auth.GetFriends(LoadFriendsToGlobe);
});
```

### Manual Sync

**Upload Local Data to Cloud:**

```python
# Read local JSON
with open('my_travels.json') as f:
    local_travels = json.load(f)['travels']

# Upload each
for travel in local_travels:
    auth.create_travel(
        latitude=travel['latitude'],
        longitude=travel['longitude'],
        title=travel['title'],
        # ...
    )
```

**Download Cloud Data to Local:**

```python
# Get from cloud
cloud_travels = auth.get_travels()

# Save to JSON
with open('my_travels.json', 'w') as f:
    json.dump({'travels': cloud_travels}, f, indent=2)
```

### Multi-Device Sync

1. **Device 1 (PC):**
   - Login with your account
   - Add travels/friends
   - Data automatically syncs to cloud

2. **Device 2 (VR Headset):**
   - Login with same account
   - Data automatically loads from cloud
   - All your travels/friends appear!

3. **Device 3 (Another PC):**
   - Login with same account
   - See all data from both devices

---

## Troubleshooting

### "Connection refused" Error

**Problem:** Can't connect to auth server

**Solution:**
```bash
# Make sure server is running
cd backend-server
python app.py

# Check health
curl http://localhost:5000/health
```

### "Token expired" Error

**Problem:** JWT token has expired (30 days)

**Solution:**
```python
# Just login again
auth.login('email', 'password')
```

### "Invalid credentials" Error

**Problem:** Wrong email/password

**Solution:**
- Double-check email and password
- Or register new account
- Or use "Forgot Password" (if implemented)

### OAuth Redirect Not Working

**Problem:** OAuth callback fails

**Solutions:**
1. **Check redirect URI** in OAuth provider settings
2. **Ensure server URL matches** - `http://localhost:5000` exactly
3. **Clear browser cookies**
4. **Try incognito mode**

### Data Not Syncing

**Problem:** Changes not appearing on other devices

**Solutions:**
1. **Check authentication:**
   ```python
   if auth.is_authenticated():
       print("✓ Authenticated")
   else:
       print("✗ Not authenticated - login first!")
   ```

2. **Manual sync:**
   ```python
   # Force refresh
   travels = auth.get_travels()
   ```

3. **Check server logs** for errors

### "Database locked" (SQLite)

**Problem:** SQLite can't handle concurrent writes

**Solution:**
- For production, use PostgreSQL
- For development, restart server

---

## Security Best Practices

### For Users

1. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
2. **Don't share your token** - it's like a password
3. **Logout on shared devices**
4. **Use OAuth when possible** (Google, Discord, Microsoft)

### For Developers

1. **Change SECRET_KEY** in production:
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use HTTPS** in production (not HTTP)

3. **Never commit `.env`** file to git:
   ```bash
   echo ".env" >> .gitignore
   ```

4. **Use PostgreSQL** for production (not SQLite)

5. **Rate limit** API endpoints in production

---

## Advanced Features

### Photo Upload to Cloud

Currently, `photo_url` expects a URL. To upload photos:

**Option 1: Use a separate file host** (Imgur, Cloudinary, AWS S3)

**Option 2: Add file upload endpoint** to backend server

```python
# Coming soon
auth.upload_photo('local_file.jpg')
# Returns: 'https://yourserver.com/uploads/photo123.jpg'
```

### Sharing Globes

Share your globe with friends:

```python
# Generate share link
share_link = auth.create_share_link()
print(f"Share with friends: {share_link}")

# View someone's shared globe
auth.load_shared_globe('share-code-here')
```

### Privacy Controls

```python
# Set travels to private
auth.update_profile(privacy='private')

# Allow specific friends to see your globe
auth.add_globe_viewer('friend_username')
```

---

## FAQ

**Q: Do I need to run my own server?**
A: For development, yes. For production, you could use a hosted server.

**Q: Is my data private?**
A: Yes, all user data is isolated. Only you can see your travels/friends (unless you share).

**Q: Can I use without authentication?**
A: Yes! The original WorldWind works without accounts. Authentication adds cloud sync.

**Q: What happens if I forget my password?**
A: Password reset feature coming soon. For now, use OAuth (Google/Discord/Microsoft).

**Q: Can I export my data?**
A: Yes, use `auth.get_travels()` and `auth.get_friends()` to download your data as JSON.

**Q: How much storage do I get?**
A: Unlimited travels and friends. Photos should be hosted externally (URLs).

**Q: Can I delete my account?**
A: Account deletion feature coming soon. For now, contact admin.

---

**Authentication makes WorldWind even more powerful - your globe, everywhere! 🌍☁️**
