#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind Python - 3D Globe Visualization using VisPy
======================================================

A Python port of NASA WorldWind using VisPy for high-performance 3D visualization.
This application demonstrates:
- 3D interactive globe with Earth texture
- Placemarks (markers on the globe)
- 3D polygons with extrusion
- Interactive controls (rotation, zoom, pan)
- Coordinate display
"""

import numpy as np
from vispy import app, scene, io
from vispy.scene import visuals
from vispy.visuals.transforms import MatrixTransform, STTransform
from vispy.geometry import create_sphere
import sys
import math


class WorldWind(scene.SceneCanvas):
    """
    Main WorldWind application class.
    Creates a 3D interactive globe visualization.
    """

    def __init__(self):
        """Initialize the WorldWind canvas and scene."""
        scene.SceneCanvas.__init__(self, keys='interactive', size=(1200, 800),
                                   title='WorldWind Python - VisPy 3D Globe')

        # Create a ViewBox for the 3D scene
        self.unfreeze()
        self.view = self.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.fov = 45
        self.view.camera.distance = 4

        # Camera initial position
        self.view.camera.elevation = 30
        self.view.camera.azimuth = 45

        # Store mouse interaction state
        self.last_pos = None
        self.rotation_x = 0
        self.rotation_y = 0

        # Earth radius constant (for scaling)
        self.earth_radius = 1.0

        # Create the globe
        self._create_globe()

        # Add placemarks
        self._create_placemarks()

        # Add 3D polygon
        self._create_polygon()

        # Add axes for reference (optional - can be disabled)
        self._create_axes()

        # Add coordinate display text
        self._create_coordinate_display()

        # Show the canvas
        self.show()

        print("WorldWind Python - Controls:")
        print("  - Left click + drag: Rotate globe")
        print("  - Right click + drag: Zoom in/out")
        print("  - Middle click + drag: Pan")
        print("  - Mouse wheel: Zoom")
        print("  - ESC: Quit application")

    def _create_globe(self):
        """Create the 3D globe with Earth texture."""
        # Create sphere mesh
        mesh_data = create_sphere(20, 40, radius=self.earth_radius)

        # Create the globe visual
        self.globe = visuals.Sphere(
            radius=self.earth_radius,
            method='latitude',
            parent=self.view.scene,
            cols=60,
            rows=60,
            color='lightblue'
        )

        # Try to load Earth texture (Blue Marble)
        # Note: For production, you would download actual Earth textures
        # For now, we'll use a solid color with a simple shader
        self.globe.shading = 'smooth'

        print("Globe created with radius:", self.earth_radius)

    def _create_placemarks(self):
        """Create placemarks (markers) on the globe surface."""
        # Example: Place a marker at coordinates (55°N, -106°W)
        # This matches the placemark in the original JavaScript version

        # Convert lat/lon to 3D coordinates
        lat, lon = 55.0, -106.0
        x, y, z = self.latlon_to_xyz(lat, lon, self.earth_radius)

        # Create a marker (sphere) at the location
        marker_pos = np.array([[x, y, z]])

        self.placemark = visuals.Markers(
            parent=self.view.scene,
            pos=marker_pos,
            size=15,
            face_color='red',
            edge_color='white',
            edge_width=2
        )

        # Create a small sphere as an alternative marker style
        self.marker_sphere = visuals.Sphere(
            radius=0.05,
            color='yellow',
            parent=self.view.scene
        )
        marker_transform = STTransform(translate=(x, y, z))
        self.marker_sphere.transform = marker_transform

        print(f"Placemark created at {lat}°N, {lon}°W")

    def _create_polygon(self):
        """Create a 3D polygon on the globe surface with extrusion."""
        # Create a polygon around a region (example: a square area)
        # Define vertices in lat/lon
        polygon_coords = [
            (45.0, -100.0),  # Northwest
            (45.0, -95.0),   # Northeast
            (40.0, -95.0),   # Southeast
            (40.0, -100.0),  # Southwest
        ]

        # Convert to 3D coordinates on sphere surface
        vertices_surface = []
        vertices_extruded = []

        extrusion_height = 0.2  # Height above surface

        for lat, lon in polygon_coords:
            x, y, z = self.latlon_to_xyz(lat, lon, self.earth_radius)
            vertices_surface.append([x, y, z])

            # Extruded vertices (higher altitude)
            x_ext, y_ext, z_ext = self.latlon_to_xyz(
                lat, lon, self.earth_radius + extrusion_height
            )
            vertices_extruded.append([x_ext, y_ext, z_ext])

        # Create the polygon faces
        vertices_surface = np.array(vertices_surface)
        vertices_extruded = np.array(vertices_extruded)

        # Draw the extruded polygon as lines connecting base to top
        all_vertices = []
        for i in range(len(vertices_surface)):
            all_vertices.append(vertices_surface[i])
            all_vertices.append(vertices_extruded[i])

        # Draw vertical edges
        for i in range(len(vertices_surface)):
            edge_vertices = np.array([vertices_surface[i], vertices_extruded[i]])
            line = visuals.Line(
                pos=edge_vertices,
                color='cyan',
                width=3,
                parent=self.view.scene
            )

        # Draw top polygon
        top_poly_vertices = np.vstack([vertices_extruded, vertices_extruded[0:1]])
        self.polygon_top = visuals.Line(
            pos=top_poly_vertices,
            color='blue',
            width=4,
            parent=self.view.scene
        )

        # Draw bottom polygon (on surface)
        bottom_poly_vertices = np.vstack([vertices_surface, vertices_surface[0:1]])
        self.polygon_bottom = visuals.Line(
            pos=bottom_poly_vertices,
            color='darkblue',
            width=3,
            parent=self.view.scene
        )

        print("3D extruded polygon created")

    def _create_axes(self):
        """Create coordinate axes for reference (X=Red, Y=Green, Z=Blue)."""
        # This is optional - helps with debugging and orientation
        axis_length = 2.0

        # X axis (red)
        x_axis = visuals.Line(
            pos=np.array([[0, 0, 0], [axis_length, 0, 0]]),
            color='red',
            width=2,
            parent=self.view.scene
        )

        # Y axis (green)
        y_axis = visuals.Line(
            pos=np.array([[0, 0, 0], [0, axis_length, 0]]),
            color='green',
            width=2,
            parent=self.view.scene
        )

        # Z axis (blue)
        z_axis = visuals.Line(
            pos=np.array([[0, 0, 0], [0, 0, axis_length]]),
            color='blue',
            width=2,
            parent=self.view.scene
        )

    def _create_coordinate_display(self):
        """Create text display for current coordinates."""
        self.coord_text = visuals.Text(
            'Coordinates: --',
            pos=(20, 20),
            color='white',
            font_size=12,
            parent=self.scene
        )

    def latlon_to_xyz(self, lat, lon, radius):
        """
        Convert latitude/longitude coordinates to 3D Cartesian coordinates.

        Parameters:
        -----------
        lat : float
            Latitude in degrees (-90 to 90)
        lon : float
            Longitude in degrees (-180 to 180)
        radius : float
            Radius of the sphere

        Returns:
        --------
        tuple : (x, y, z) coordinates
        """
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        # Spherical to Cartesian conversion
        # Note: Different coordinate systems may use different conventions
        # This uses: x = forward, y = right, z = up
        x = radius * math.cos(lat_rad) * math.cos(lon_rad)
        y = radius * math.cos(lat_rad) * math.sin(lon_rad)
        z = radius * math.sin(lat_rad)

        return x, y, z

    def xyz_to_latlon(self, x, y, z):
        """
        Convert 3D Cartesian coordinates to latitude/longitude.

        Parameters:
        -----------
        x, y, z : float
            Cartesian coordinates

        Returns:
        --------
        tuple : (lat, lon) in degrees
        """
        # Calculate radius
        r = math.sqrt(x**2 + y**2 + z**2)

        # Avoid division by zero
        if r == 0:
            return 0, 0

        # Calculate latitude
        lat = math.degrees(math.asin(z / r))

        # Calculate longitude
        lon = math.degrees(math.atan2(y, x))

        return lat, lon

    def on_mouse_move(self, event):
        """Handle mouse movement for coordinate display."""
        # Update coordinate display based on mouse position
        # Note: This is a simplified version; full implementation would
        # require ray-casting to find intersection with globe

        if event.pos is not None:
            x, y = event.pos
            # Simple coordinate display (screen coordinates for now)
            self.coord_text.text = f'Mouse: ({x:.0f}, {y:.0f})'

    def on_key_press(self, event):
        """Handle keyboard events."""
        if event.key == 'Escape':
            self.close()
            app.quit()
        elif event.key == 'r' or event.key == 'R':
            # Reset camera view
            self.view.camera.elevation = 30
            self.view.camera.azimuth = 45
            self.view.camera.distance = 4
            print("Camera view reset")
        elif event.key == 'h' or event.key == 'H':
            # Show help
            print("\nWorldWind Python - Keyboard Controls:")
            print("  R: Reset camera view")
            print("  H: Show this help")
            print("  ESC: Quit application")


def main():
    """Main entry point for the WorldWind application."""
    print("=" * 60)
    print("WorldWind Python - 3D Globe Visualization")
    print("Powered by VisPy")
    print("=" * 60)

    # Create and run the application
    canvas = WorldWind()

    # Start the application event loop
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
