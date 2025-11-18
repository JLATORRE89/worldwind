#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind with Friends
======================

WorldWind globe with support for adding friends as placemarks around the world.
"""

import numpy as np
from vispy import app, scene, io
from vispy.scene import visuals
import sys
import json
import os

# Import the base WorldWind class
from worldwind import WorldWind


class Friend:
    """Represents a friend placemark."""
    def __init__(self, name, city, latitude, longitude, photo_path="", color="yellow", group="friends"):
        self.name = name
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.photo_path = photo_path
        self.color = color
        self.group = group
        self.marker = None


class WorldWindWithFriends(WorldWind):
    """
    Extended WorldWind with friend placemark support.
    """

    def __init__(self):
        super().__init__()
        self.friends = []

        # Group color mapping
        self.group_colors = {
            'family': 'red',
            'friends': 'yellow',
            'work': 'blue',
            'college': 'green',
            'high_school': 'orange'
        }

        # Color name to RGB mapping
        self.color_map = {
            'red': (1, 0, 0),
            'yellow': (1, 1, 0),
            'blue': (0, 0, 1),
            'green': (0, 1, 0),
            'cyan': (0, 1, 1),
            'magenta': (1, 0, 1),
            'orange': (1, 0.5, 0),
            'purple': (0.5, 0, 1),
            'white': (1, 1, 1),
            'pink': (1, 0.5, 0.8)
        }

        print("\n👥 Friend Features:")
        print("   - Add friends at their locations")
        print("   - Organize by groups (family, work, college, etc.)")
        print("   - Color-code by group")
        print("   - Add profile photos")
        print()

    def add_friend(self, name, city, latitude, longitude, photo_path="", color="yellow", group="friends"):
        """
        Add a friend as a placemark on the globe.

        Parameters:
        -----------
        name : str
            Friend's name
        city : str
            City where friend lives
        latitude : float
            Latitude of the city
        longitude : float
            Longitude of the city
        photo_path : str
            Path to friend's photo (optional)
        color : str
            Color of the marker
        group : str
            Group category (family, friends, work, college, etc.)
        """
        # Create friend object
        friend = Friend(name, city, latitude, longitude, photo_path, color, group)

        # Get marker color
        marker_color = self._get_color(color, group)

        # Convert lat/lon to 3D position
        x, y, z = self.latlon_to_xyz(latitude, longitude, self.earth_radius + 0.05)
        marker_pos = np.array([[x, y, z]])

        # Create marker
        marker = visuals.Markers(
            parent=self.view.scene,
            pos=marker_pos,
            size=18,
            face_color=marker_color,
            edge_color='white',
            edge_width=2,
            symbol='disc'
        )

        friend.marker = marker
        self.friends.append(friend)

        print(f"👤 Added friend: {name} in {city} ({latitude}°, {longitude}°) - Group: {group}")

        return friend

    def _get_color(self, color_name, group):
        """Get color RGB tuple from name or group."""
        # Try color name first
        if color_name.lower() in self.color_map:
            return self.color_map[color_name.lower()]

        # Fall back to group color
        if group.lower() in self.group_colors:
            group_color_name = self.group_colors[group.lower()]
            return self.color_map.get(group_color_name, (1, 1, 0))  # Default yellow

        # Default yellow
        return (1, 1, 0)

    def load_from_json(self, json_path):
        """
        Load friends from a JSON configuration file.

        JSON format:
        {
          "friends": [
            {
              "name": "Sarah Johnson",
              "city": "New York",
              "latitude": 40.7128,
              "longitude": -74.0060,
              "photo": "photos/sarah.jpg",
              "color": "yellow",
              "group": "college"
            }
          ]
        }
        """
        if not os.path.exists(json_path):
            print(f"❌ JSON file not found: {json_path}")
            return

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            friends_data = data.get('friends', [])

            for friend_data in friends_data:
                self.add_friend(
                    name=friend_data.get('name', 'Unknown'),
                    city=friend_data.get('city', 'Unknown'),
                    latitude=friend_data.get('latitude', 0),
                    longitude=friend_data.get('longitude', 0),
                    photo_path=friend_data.get('photo', ''),
                    color=friend_data.get('color', 'yellow'),
                    group=friend_data.get('group', 'friends')
                )

            print(f"\n✅ Loaded {len(friends_data)} friends from JSON")

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")

    def get_all_friends(self):
        """Get list of all friends."""
        return self.friends

    def get_friends_by_group(self, group):
        """Get friends in a specific group."""
        return [f for f in self.friends if f.group.lower() == group.lower()]

    def show_group(self, group, show=True):
        """Show or hide friends in a specific group."""
        for friend in self.friends:
            if friend.group.lower() == group.lower() and friend.marker:
                friend.marker.visible = show

    def remove_friend(self, friend):
        """Remove a friend from the globe."""
        if friend in self.friends:
            if friend.marker:
                friend.marker.parent = None
            self.friends.remove(friend)

    def clear_all_friends(self):
        """Remove all friends."""
        for friend in self.friends:
            if friend.marker:
                friend.marker.parent = None
        self.friends.clear()

    def list_friends(self):
        """Print a list of all friends."""
        if not self.friends:
            print("No friends added yet.")
            return

        print("\n📋 Friends List:")
        print("=" * 60)

        # Group friends by group
        groups = {}
        for friend in self.friends:
            group_name = friend.group
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(friend)

        # Print by group
        for group_name, group_friends in groups.items():
            print(f"\n{group_name.upper()} ({len(group_friends)}):")
            for friend in group_friends:
                print(f"  • {friend.name:20s} - {friend.city:20s} ({friend.latitude:.2f}°, {friend.longitude:.2f}°)")

        print("=" * 60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='WorldWind with Friends')
    parser.add_argument('--friends', type=str, help='Path to JSON file with friends data')
    parser.add_argument('--name', type=str, help='Friend name')
    parser.add_argument('--city', type=str, help='Friend city')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--color', type=str, default='yellow', help='Marker color')
    parser.add_argument('--group', type=str, default='friends', help='Friend group')

    args = parser.parse_args()

    print("=" * 60)
    print("WorldWind with Friends")
    print("=" * 60)
    print()

    # Create application
    canvas = WorldWindWithFriends()

    # Load from JSON file
    if args.friends:
        canvas.load_from_json(args.friends)

    # Or add a single friend
    elif args.name and args.city and args.lat is not None and args.lon is not None:
        canvas.add_friend(
            name=args.name,
            city=args.city,
            latitude=args.lat,
            longitude=args.lon,
            color=args.color,
            group=args.group
        )

    # Example friends (if no arguments provided)
    else:
        print("ℹ️  No friends provided. Use --friends or individual args to add friends.")
        print()
        print("Example usage:")
        print("  python worldwind_with_friends.py --friends my_friends.json")
        print("  python worldwind_with_friends.py --name 'Sarah' --city 'New York' --lat 40.7128 --lon -74.0060")
        print()
        print("Adding example friends...")

        # Add some example friends
        canvas.add_friend("Sarah Johnson", "New York", 40.7128, -74.0060, color="yellow", group="college")
        canvas.add_friend("Mike Chen", "San Francisco", 37.7749, -122.4194, color="blue", group="work")
        canvas.add_friend("Emma Schmidt", "Berlin", 52.5200, 13.4050, color="green", group="college")
        canvas.add_friend("Carlos Rodriguez", "Madrid", 40.4168, -3.7038, color="red", group="family")

    # List friends
    canvas.list_friends()

    # Run
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
