#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind Extensions
====================

Additional features for WorldWind: routes, animations, distance measurements, etc.
"""

import numpy as np
from vispy.scene import visuals
import math


class TravelRoute:
    """
    Create and manage travel routes on the globe.
    """

    def __init__(self, globe_instance):
        """
        Initialize the TravelRoute manager.

        Parameters:
        -----------
        globe_instance : WorldWind
            The WorldWind globe instance
        """
        self.globe = globe_instance
        self.routes = []

    def create_route(self, locations, color='cyan', width=3, name="Route"):
        """
        Create a route connecting multiple locations.

        Parameters:
        -----------
        locations : list of tuples
            List of (latitude, longitude) tuples
        color : str or tuple
            Color of the route line
        width : float
            Width of the route line
        name : str
            Name of the route

        Returns:
        --------
        Line visual object
        """
        if len(locations) < 2:
            print("Need at least 2 locations to create a route")
            return None

        # Convert lat/lon to 3D coordinates
        vertices = []
        for lat, lon in locations:
            x, y, z = self.globe.latlon_to_xyz(lat, lon, self.globe.earth_radius + 0.02)
            vertices.append([x, y, z])

        vertices = np.array(vertices)

        # Create curved path (arc along sphere surface)
        # For now, use straight lines, but could interpolate along great circle
        line = visuals.Line(
            pos=vertices,
            color=color,
            width=width,
            parent=self.globe.view.scene
        )

        route_data = {
            'name': name,
            'locations': locations,
            'line': line,
            'color': color
        }

        self.routes.append(route_data)

        print(f"✈️  Created route '{name}' with {len(locations)} waypoints")

        return line

    def create_great_circle_route(self, start, end, color='cyan', width=3, num_points=50):
        """
        Create a route following the great circle path between two points.

        Parameters:
        -----------
        start : tuple
            (latitude, longitude) start point
        end : tuple
            (latitude, longitude) end point
        color : str or tuple
            Color of the route
        width : float
            Width of the line
        num_points : int
            Number of points to interpolate along the path

        Returns:
        --------
        Line visual object
        """
        start_lat, start_lon = start
        end_lat, end_lon = end

        # Generate intermediate points along great circle
        vertices = []

        for i in range(num_points):
            # Interpolation parameter
            t = i / (num_points - 1)

            # Spherical linear interpolation (slerp)
            lat, lon = self._slerp(start_lat, start_lon, end_lat, end_lon, t)

            x, y, z = self.globe.latlon_to_xyz(lat, lon, self.globe.earth_radius + 0.02)
            vertices.append([x, y, z])

        vertices = np.array(vertices)

        line = visuals.Line(
            pos=vertices,
            color=color,
            width=width,
            parent=self.globe.view.scene
        )

        return line

    def _slerp(self, lat1, lon1, lat2, lon2, t):
        """
        Spherical linear interpolation between two lat/lon points.

        Parameters:
        -----------
        lat1, lon1 : float
            Start point
        lat2, lon2 : float
            End point
        t : float
            Interpolation parameter (0 to 1)

        Returns:
        --------
        tuple : (lat, lon) interpolated point
        """
        # Convert to radians
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        # Convert to Cartesian
        x1 = math.cos(lat1_rad) * math.cos(lon1_rad)
        y1 = math.cos(lat1_rad) * math.sin(lon1_rad)
        z1 = math.sin(lat1_rad)

        x2 = math.cos(lat2_rad) * math.cos(lon2_rad)
        y2 = math.cos(lat2_rad) * math.sin(lon2_rad)
        z2 = math.sin(lat2_rad)

        # Dot product
        dot = x1*x2 + y1*y2 + z1*z2

        # Clamp dot product
        dot = max(-1.0, min(1.0, dot))

        # Angle between vectors
        theta = math.acos(dot)

        # Avoid division by zero
        if abs(theta) < 0.001:
            # Points are very close, use linear interpolation
            x = (1 - t) * x1 + t * x2
            y = (1 - t) * y1 + t * y2
            z = (1 - t) * z1 + t * z2
        else:
            # Spherical interpolation
            sin_theta = math.sin(theta)
            a = math.sin((1 - t) * theta) / sin_theta
            b = math.sin(t * theta) / sin_theta

            x = a * x1 + b * x2
            y = a * y1 + b * y2
            z = a * z1 + b * z2

        # Convert back to lat/lon
        lat = math.degrees(math.asin(z))
        lon = math.degrees(math.atan2(y, x))

        return lat, lon

    def measure_distance(self, point1, point2, unit='km'):
        """
        Measure distance between two points using haversine formula.

        Parameters:
        -----------
        point1 : tuple
            (latitude, longitude) first point
        point2 : tuple
            (latitude, longitude) second point
        unit : str
            'km' for kilometers, 'mi' for miles, 'nm' for nautical miles

        Returns:
        --------
        float : distance in specified unit
        """
        lat1, lon1 = point1
        lat2, lon2 = point2

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius
        r = 6371  # km

        distance = r * c

        # Convert to requested unit
        if unit == 'mi':
            distance *= 0.621371  # km to miles
        elif unit == 'nm':
            distance *= 0.539957  # km to nautical miles

        return distance

    def clear_all_routes(self):
        """Remove all routes from the globe."""
        for route in self.routes:
            if route['line']:
                route['line'].parent = None
        self.routes.clear()


class DistanceMeasurement:
    """
    Measure and display distances on the globe.
    """

    def __init__(self, globe_instance):
        self.globe = globe_instance
        self.measurements = []

    def measure_and_display(self, point1, point2, color='yellow', unit='km'):
        """
        Measure distance and draw a line with distance label.

        Parameters:
        -----------
        point1 : tuple
            (latitude, longitude)
        point2 : tuple
            (latitude, longitude)
        color : str
            Color of the measurement line
        unit : str
            Distance unit ('km', 'mi', 'nm')

        Returns:
        --------
        dict : measurement data
        """
        # Calculate distance
        route_manager = TravelRoute(self.globe)
        distance = route_manager.measure_distance(point1, point2, unit)

        # Draw line
        x1, y1, z1 = self.globe.latlon_to_xyz(point1[0], point1[1], self.globe.earth_radius + 0.02)
        x2, y2, z2 = self.globe.latlon_to_xyz(point2[0], point2[1], self.globe.earth_radius + 0.02)

        vertices = np.array([[x1, y1, z1], [x2, y2, z2]])

        line = visuals.Line(
            pos=vertices,
            color=color,
            width=4,
            parent=self.globe.view.scene
        )

        measurement = {
            'point1': point1,
            'point2': point2,
            'distance': distance,
            'unit': unit,
            'line': line
        }

        self.measurements.append(measurement)

        print(f"📏 Distance: {distance:.2f} {unit}")

        return measurement


class AnimatedFlight:
    """
    Animate a flight path between two locations.
    """

    def __init__(self, globe_instance):
        self.globe = globe_instance
        self.animations = []

    def animate_flight(self, start, end, duration=5.0, color='red'):
        """
        Animate a flight from start to end location.

        Parameters:
        -----------
        start : tuple
            (latitude, longitude) start point
        end : tuple
            (latitude, longitude) end point
        duration : float
            Duration of animation in seconds
        color : str
            Color of the flight path

        Returns:
        --------
        Animation data
        """
        print(f"✈️  Animating flight from {start} to {end} over {duration}s")

        # TODO: Implement animation using VisPy Timer
        # For now, just draw the route

        route_manager = TravelRoute(self.globe)
        line = route_manager.create_great_circle_route(start, end, color=color, width=5)

        animation = {
            'start': start,
            'end': end,
            'duration': duration,
            'line': line
        }

        self.animations.append(animation)

        return animation
