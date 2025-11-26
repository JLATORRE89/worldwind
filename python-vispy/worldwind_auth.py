#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind Authentication Client
================================

Client library for authenticating with WorldWind backend server.
Supports email/password login and OAuth (Google, Discord, Microsoft).
"""

import requests
import json
import os
from pathlib import Path


class WorldWindAuth:
    """
    Authentication client for WorldWind.
    """

    def __init__(self, server_url='http://localhost:5000'):
        """
        Initialize authentication client.

        Parameters:
        -----------
        server_url : str
            URL of the WorldWind authentication server
        """
        self.server_url = server_url.rstrip('/')
        self.token = None
        self.user = None

        # Try to load saved token
        self._load_token()

    def register(self, email, username, password):
        """
        Register new user with email/password.

        Parameters:
        -----------
        email : str
            User email
        username : str
            Username
        password : str
            Password

        Returns:
        --------
        dict : User data and token
        """
        response = requests.post(
            f'{self.server_url}/api/register',
            json={
                'email': email,
                'username': username,
                'password': password
            }
        )

        if response.status_code == 201:
            data = response.json()
            self.token = data['token']
            self.user = data['user']
            self._save_token()
            print(f"✓ Registered successfully as {username}")
            return data
        else:
            error = response.json().get('error', 'Registration failed')
            print(f"✗ Registration failed: {error}")
            raise Exception(error)

    def login(self, email, password):
        """
        Login with email/password.

        Parameters:
        -----------
        email : str
            User email
        password : str
            Password

        Returns:
        --------
        dict : User data and token
        """
        response = requests.post(
            f'{self.server_url}/api/login',
            json={
                'email': email,
                'password': password
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.user = data['user']
            self._save_token()
            print(f"✓ Logged in as {self.user['username']}")
            return data
        else:
            error = response.json().get('error', 'Login failed')
            print(f"✗ Login failed: {error}")
            raise Exception(error)

    def login_google(self):
        """
        Login with Google OAuth.
        Opens browser for authentication.
        """
        import webbrowser
        auth_url = f'{self.server_url}/auth/google'
        print(f"Opening browser for Google login: {auth_url}")
        webbrowser.open(auth_url)
        print("Complete login in browser, then paste the token here:")

    def login_discord(self):
        """
        Login with Discord OAuth.
        Opens browser for authentication.
        """
        import webbrowser
        auth_url = f'{self.server_url}/auth/discord'
        print(f"Opening browser for Discord login: {auth_url}")
        webbrowser.open(auth_url)
        print("Complete login in browser, then paste the token here:")

    def login_microsoft(self):
        """
        Login with Microsoft OAuth.
        Opens browser for authentication.
        """
        import webbrowser
        auth_url = f'{self.server_url}/auth/microsoft'
        print(f"Opening browser for Microsoft login: {auth_url}")
        webbrowser.open(auth_url)
        print("Complete login in browser, then paste the token here:")

    def set_token(self, token):
        """
        Manually set authentication token (from OAuth flow).

        Parameters:
        -----------
        token : str
            JWT authentication token
        """
        self.token = token
        self._save_token()
        self.get_profile()  # Fetch user data

    def logout(self):
        """Logout and clear token."""
        self.token = None
        self.user = None
        self._clear_token()
        print("✓ Logged out")

    def is_authenticated(self):
        """Check if user is authenticated."""
        return self.token is not None

    def get_headers(self):
        """Get headers with authentication token."""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {'Authorization': f'Bearer {self.token}'}

    def get_profile(self):
        """
        Get user profile.

        Returns:
        --------
        dict : User profile data
        """
        response = requests.get(
            f'{self.server_url}/api/profile',
            headers=self.get_headers()
        )

        if response.status_code == 200:
            self.user = response.json()
            return self.user
        else:
            error = response.json().get('message', 'Failed to get profile')
            raise Exception(error)

    def update_profile(self, display_name=None, avatar_url=None):
        """
        Update user profile.

        Parameters:
        -----------
        display_name : str
            Display name
        avatar_url : str
            Avatar URL
        """
        data = {}
        if display_name:
            data['display_name'] = display_name
        if avatar_url:
            data['avatar_url'] = avatar_url

        response = requests.put(
            f'{self.server_url}/api/profile',
            headers=self.get_headers(),
            json=data
        )

        if response.status_code == 200:
            print("✓ Profile updated")
            return response.json()
        else:
            error = response.json().get('message', 'Failed to update profile')
            raise Exception(error)

    # ========================================================================
    # TRAVELS
    # ========================================================================

    def get_travels(self):
        """
        Get all travels for current user.

        Returns:
        --------
        list : List of travel dictionaries
        """
        response = requests.get(
            f'{self.server_url}/api/travels',
            headers=self.get_headers()
        )

        if response.status_code == 200:
            return response.json()['travels']
        else:
            raise Exception("Failed to get travels")

    def create_travel(self, latitude, longitude, photo_url=None, title=None,
                     description=None, date=None):
        """
        Create new travel/photo.

        Parameters:
        -----------
        latitude : float
            Latitude
        longitude : float
            Longitude
        photo_url : str
            Photo URL
        title : str
            Title
        description : str
            Description
        date : str
            Date

        Returns:
        --------
        dict : Created travel data
        """
        response = requests.post(
            f'{self.server_url}/api/travels',
            headers=self.get_headers(),
            json={
                'latitude': latitude,
                'longitude': longitude,
                'photo_url': photo_url,
                'title': title,
                'description': description,
                'date': date
            }
        )

        if response.status_code == 201:
            print(f"✓ Travel added: {title}")
            return response.json()['travel']
        else:
            raise Exception("Failed to create travel")

    def delete_travel(self, travel_id):
        """Delete a travel."""
        response = requests.delete(
            f'{self.server_url}/api/travels/{travel_id}',
            headers=self.get_headers()
        )

        if response.status_code == 200:
            print("✓ Travel deleted")
        else:
            raise Exception("Failed to delete travel")

    # ========================================================================
    # FRIENDS
    # ========================================================================

    def get_friends(self):
        """
        Get all friends for current user.

        Returns:
        --------
        list : List of friend dictionaries
        """
        response = requests.get(
            f'{self.server_url}/api/friends',
            headers=self.get_headers()
        )

        if response.status_code == 200:
            return response.json()['friends']
        else:
            raise Exception("Failed to get friends")

    def create_friend(self, name, city, latitude, longitude, photo_url=None,
                     color='yellow', group='friends'):
        """
        Create new friend.

        Parameters:
        -----------
        name : str
            Friend name
        city : str
            City
        latitude : float
            Latitude
        longitude : float
            Longitude
        photo_url : str
            Photo URL
        color : str
            Marker color
        group : str
            Friend group

        Returns:
        --------
        dict : Created friend data
        """
        response = requests.post(
            f'{self.server_url}/api/friends',
            headers=self.get_headers(),
            json={
                'name': name,
                'city': city,
                'latitude': latitude,
                'longitude': longitude,
                'photo_url': photo_url,
                'color': color,
                'group': group
            }
        )

        if response.status_code == 201:
            print(f"✓ Friend added: {name}")
            return response.json()['friend']
        else:
            raise Exception("Failed to create friend")

    def delete_friend(self, friend_id):
        """Delete a friend."""
        response = requests.delete(
            f'{self.server_url}/api/friends/{friend_id}',
            headers=self.get_headers()
        )

        if response.status_code == 200:
            print("✓ Friend deleted")
        else:
            raise Exception("Failed to delete friend")

    # ========================================================================
    # TOKEN MANAGEMENT
    # ========================================================================

    def _get_token_path(self):
        """Get path to token file."""
        home = Path.home()
        config_dir = home / '.worldwind'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'token.json'

    def _save_token(self):
        """Save token to file."""
        if self.token:
            token_path = self._get_token_path()
            with open(token_path, 'w') as f:
                json.dump({'token': self.token}, f)

    def _load_token(self):
        """Load token from file."""
        token_path = self._get_token_path()
        if token_path.exists():
            with open(token_path, 'r') as f:
                data = json.load(f)
                self.token = data.get('token')

                # Validate token by fetching profile
                if self.token:
                    try:
                        self.get_profile()
                        print(f"✓ Logged in as {self.user['username']}")
                    except:
                        # Token expired or invalid
                        self.token = None
                        self.user = None

    def _clear_token(self):
        """Clear saved token."""
        token_path = self._get_token_path()
        if token_path.exists():
            token_path.unlink()


# Example usage
if __name__ == '__main__':
    # Initialize client
    auth = WorldWindAuth('http://localhost:5000')

    # Check if already logged in
    if auth.is_authenticated():
        print(f"Already logged in as: {auth.user['username']}")
    else:
        print("Not logged in")

        # Example: Register or login
        choice = input("1) Register  2) Login  3) Google  4) Discord  5) Microsoft\nChoice: ")

        if choice == '1':
            email = input("Email: ")
            username = input("Username: ")
            password = input("Password: ")
            auth.register(email, username, password)

        elif choice == '2':
            email = input("Email: ")
            password = input("Password: ")
            auth.login(email, password)

        elif choice == '3':
            auth.login_google()

        elif choice == '4':
            auth.login_discord()

        elif choice == '5':
            auth.login_microsoft()

    # Show profile
    if auth.is_authenticated():
        profile = auth.get_profile()
        print(f"\nProfile:")
        print(f"  Username: {profile['username']}")
        print(f"  Email: {profile['email']}")
        print(f"  Travels: {profile['travels_count']}")
        print(f"  Friends: {profile['friends_count']}")
