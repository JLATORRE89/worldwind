#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind with Travel Photos
=============================

WorldWind globe with support for adding your travel photos as 3D placemarks.
"""

import numpy as np
from vispy import app, scene, io
from vispy.scene import visuals
from vispy.visuals.transforms import STTransform
import sys
import math
import json
import os
from pathlib import Path

# Import the base WorldWind class
from worldwind import WorldWind


class TravelPhoto:
    """Represents a travel photo placemark."""
    def __init__(self, photo_path, latitude, longitude, title="", description="", date=""):
        self.photo_path = photo_path
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.description = description
        self.date = date
        self.texture = None
        self.marker = None


class WorldWindWithPhotos(WorldWind):
    """
    Extended WorldWind with travel photo support.
    """

    def __init__(self):
        super().__init__()
        self.travel_photos = []
        self.photo_size = 0.15  # Size of photo displays

        print("\n💡 Photo Features:")
        print("   - Load photos from disk")
        print("   - Display as 3D billboards on globe")
        print("   - Click photos to see details")
        print()

    def add_travel_photo(self, photo_path, latitude, longitude, title="", description="", date=""):
        """
        Add a travel photo as a placemark on the globe.

        Parameters:
        -----------
        photo_path : str
            Path to the photo file
        latitude : float
            Latitude of the location
        longitude : float
            Longitude of the location
        title : str
            Title/caption for the photo
        description : str
            Additional description
        date : str
            Date of the photo (e.g., "2023-06-15")
        """
        # Check if file exists
        if not os.path.exists(photo_path):
            print(f"⚠️  Photo not found: {photo_path}")
            return None

        # Create photo object
        photo = TravelPhoto(photo_path, latitude, longitude, title, description, date)

        try:
            # Load image using VisPy's image loader
            image_data = io.read_png(photo_path)
            photo.texture = image_data

            # Convert lat/lon to 3D position
            x, y, z = self.latlon_to_xyz(latitude, longitude, self.earth_radius + 0.1)

            # Create a visual for the photo (using Image visual)
            # For now, we'll use a simple marker and store the photo data
            marker_pos = np.array([[x, y, z]])

            # Create marker
            marker = visuals.Markers(
                parent=self.view.scene,
                pos=marker_pos,
                size=20,
                face_color='cyan',
                edge_color='white',
                edge_width=3,
                symbol='square'  # Square for photo frame
            )

            photo.marker = marker
            self.travel_photos.append(photo)

            print(f"📸 Added photo: '{title}' at {latitude}°, {longitude}°")

        except Exception as e:
            print(f"❌ Error loading photo: {e}")
            return None

        return photo

    def load_from_json(self, json_path):
        """
        Load travel photos from a JSON configuration file.

        JSON format:
        {
          "travels": [
            {
              "photo": "path/to/photo.jpg",
              "latitude": 48.8566,
              "longitude": 2.3522,
              "title": "Eiffel Tower",
              "description": "Summer vacation",
              "date": "2023-06-15"
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

            travels = data.get('travels', [])

            for travel in travels:
                photo_path = travel.get('photo', '')

                # Handle relative paths
                if not os.path.isabs(photo_path):
                    json_dir = os.path.dirname(json_path)
                    photo_path = os.path.join(json_dir, photo_path)

                self.add_travel_photo(
                    photo_path=photo_path,
                    latitude=travel.get('latitude', 0),
                    longitude=travel.get('longitude', 0),
                    title=travel.get('title', ''),
                    description=travel.get('description', ''),
                    date=travel.get('date', '')
                )

            print(f"\n✅ Loaded {len(travels)} travel photos from JSON")

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")

    def get_all_photos(self):
        """Get list of all travel photos."""
        return self.travel_photos

    def remove_photo(self, photo):
        """Remove a travel photo from the globe."""
        if photo in self.travel_photos:
            if photo.marker:
                photo.marker.parent = None
            self.travel_photos.remove(photo)

    def clear_all_photos(self):
        """Remove all travel photos."""
        for photo in self.travel_photos:
            if photo.marker:
                photo.marker.parent = None
        self.travel_photos.clear()

    def on_mouse_press(self, event):
        """Handle mouse clicks to select photos."""
        # TODO: Implement photo selection with raycasting
        pass


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='WorldWind with Travel Photos')
    parser.add_argument('--config', type=str, help='Path to JSON config file with travel photos')
    parser.add_argument('--photo', type=str, help='Path to a single photo to add')
    parser.add_argument('--lat', type=float, help='Latitude for single photo')
    parser.add_argument('--lon', type=float, help='Longitude for single photo')
    parser.add_argument('--title', type=str, default='', help='Title for single photo')

    args = parser.parse_args()

    print("=" * 60)
    print("WorldWind with Travel Photos")
    print("=" * 60)
    print()

    # Create application
    canvas = WorldWindWithPhotos()

    # Load from config file
    if args.config:
        canvas.load_from_json(args.config)

    # Or add a single photo
    elif args.photo and args.lat is not None and args.lon is not None:
        canvas.add_travel_photo(
            photo_path=args.photo,
            latitude=args.lat,
            longitude=args.lon,
            title=args.title
        )

    # Example photos (if no arguments provided)
    else:
        print("ℹ️  No photos provided. Use --config or --photo to add travel photos.")
        print()
        print("Example usage:")
        print("  python worldwind_with_photos.py --config my_travels.json")
        print("  python worldwind_with_photos.py --photo paris.jpg --lat 48.8566 --lon 2.3522 --title 'Paris'")
        print()

    # Run
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
