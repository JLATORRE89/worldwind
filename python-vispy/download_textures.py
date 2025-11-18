#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Texture Downloader for WorldWind Python
========================================

Downloads Earth textures (Blue Marble) for use with the WorldWind application.
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found.")
    print("Please install it using: pip install requests")
    sys.exit(1)


def download_file(url, filename):
    """
    Download a file from a URL with progress indication.

    Parameters:
    -----------
    url : str
        URL to download from
    filename : str
        Local filename to save to
    """
    print(f"Downloading {filename}...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Show progress
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"Progress: {progress:.1f}%", end='\r')

        print(f"\n✓ Downloaded: {filename} ({downloaded / 1024 / 1024:.2f} MB)")
        return True

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error downloading {filename}: {e}")
        return False


def main():
    """Main function to download Earth textures."""
    print("=" * 70)
    print("WorldWind Python - Texture Downloader")
    print("=" * 70)
    print()

    # Create textures directory if it doesn't exist
    textures_dir = "textures"
    if not os.path.exists(textures_dir):
        os.makedirs(textures_dir)
        print(f"Created directory: {textures_dir}/")

    # Example texture URLs (these are public domain Earth textures)
    # Note: You may need to find current valid URLs for high-res textures
    textures = {
        "earth_daymap.jpg": "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/world.topo.bathy.200412.3x5400x2700.jpg",
    }

    print("\nAvailable textures:")
    print("1. Earth Day Map (Blue Marble)")
    print()

    # Note: The actual NASA imagery URLs may change
    # For production use, you should host these files or use a CDN
    print("NOTE: Due to NASA's file hosting structure, you may need to manually download textures.")
    print()
    print("Recommended sources:")
    print("1. NASA Visible Earth: https://visibleearth.nasa.gov/")
    print("2. Blue Marble Next Generation: https://visibleearth.nasa.gov/collection/1484/blue-marble")
    print()
    print("Manual download instructions:")
    print("1. Visit the NASA Visible Earth website")
    print("2. Download a Blue Marble image (2048x1024 or higher recommended)")
    print("3. Save it as 'earth_texture.jpg' in the python-vispy/textures/ directory")
    print()

    # For demonstration, we can try to download a smaller texture
    print("Attempting to download a sample texture...")
    print("(This may not work if URLs have changed)")
    print()

    # Alternative: Use a placeholder texture generator
    print("Creating a simple placeholder texture...")
    create_placeholder_texture(os.path.join(textures_dir, "earth_placeholder.jpg"))


def create_placeholder_texture(filename):
    """
    Create a simple placeholder Earth texture using Pillow.

    Parameters:
    -----------
    filename : str
        Output filename for the placeholder texture
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        print(f"Generating placeholder texture: {filename}")

        # Create a blue/green Earth-like texture
        width, height = 2048, 1024

        # Create base image
        img = Image.new('RGB', (width, height))
        pixels = img.load()

        # Simple gradient to simulate ocean/land
        for y in range(height):
            for x in range(width):
                # Create a simple blue-green pattern
                blue_value = int(100 + 50 * np.sin(x * 0.01))
                green_value = int(80 + 40 * np.sin(y * 0.01))
                pixels[x, y] = (20, green_value, blue_value)

        # Add some "land" areas (brighter regions)
        draw = ImageDraw.Draw(img)

        # Add some ellipses to simulate continents
        draw.ellipse([300, 200, 800, 600], fill=(100, 150, 50))
        draw.ellipse([1200, 300, 1800, 700], fill=(120, 160, 60))
        draw.ellipse([400, 600, 900, 900], fill=(110, 140, 55))

        # Save the image
        img.save(filename, 'JPEG', quality=85)
        print(f"✓ Created placeholder texture: {filename}")
        print(f"  Size: {width}x{height}")
        print()
        print("This is a simple placeholder. For realistic Earth visualization,")
        print("please download actual Blue Marble imagery from NASA.")

    except ImportError:
        print("✗ Pillow (PIL) not installed. Cannot create placeholder texture.")
        print("  Install with: pip install Pillow")


if __name__ == '__main__':
    main()
