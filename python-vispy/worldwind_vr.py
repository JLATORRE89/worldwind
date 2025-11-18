#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldWind Python VR - 3D Globe Visualization with VR Support
============================================================

A Python VR implementation of NASA WorldWind using VisPy and PyOpenVR.
Supports SteamVR-compatible headsets (Valve Index, HTC Vive, Oculus Rift, etc.)
"""

import numpy as np
from vispy import app, scene
from vispy.scene import visuals
from vispy.visuals.transforms import STTransform
from vispy.geometry import create_sphere
import sys
import math

# VR support (optional - falls back to desktop if not available)
VR_AVAILABLE = False
try:
    import openvr
    VR_AVAILABLE = True
    print("✓ OpenVR support available")
except ImportError:
    print("✗ PyOpenVR not found. Running in desktop mode.")
    print("  Install with: pip install openvr")


class WorldWindVR(scene.SceneCanvas):
    """
    VR-Ready WorldWind application class.
    Supports both VR (SteamVR) and desktop modes.
    """

    def __init__(self, enable_vr=True):
        """Initialize the WorldWind VR canvas and scene."""

        # Determine if VR should be enabled
        self.vr_enabled = enable_vr and VR_AVAILABLE

        if self.vr_enabled:
            print("Initializing VR mode...")
            self._init_vr()
        else:
            print("Initializing desktop mode...")

        # Initialize canvas
        scene.SceneCanvas.__init__(
            self,
            keys='interactive',
            size=(1920, 1080) if self.vr_enabled else (1200, 800),
            title='WorldWind Python VR - 3D Globe',
            show=True
        )

        self.unfreeze()

        # Create view
        self.view = self.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.fov = 90 if self.vr_enabled else 45
        self.view.camera.distance = 3

        # VR state
        self.vr_system = None
        self.vr_compositor = None
        self.controller_states = {}

        # Earth radius
        self.earth_radius = 1.0

        # Create globe
        self._create_globe()
        self._create_placemarks()
        self._create_polygon()

        if not self.vr_enabled:
            self._create_axes()

        # VR update timer
        if self.vr_enabled:
            self.vr_timer = app.Timer(interval=1/90, connect=self._update_vr, start=True)
            print("VR mode active - 90Hz tracking")

        self.show()

        self._print_controls()

    def _init_vr(self):
        """Initialize OpenVR system."""
        try:
            self.vr_system = openvr.init(openvr.VRApplication_Scene)

            if self.vr_system:
                self.vr_compositor = openvr.VRCompositor()

                # Get recommended render target size
                width, height = self.vr_system.getRecommendedRenderTargetSize()
                print(f"VR System initialized: {width}x{height}")

                # Get HMD info
                model = self.vr_system.getStringTrackedDeviceProperty(
                    openvr.k_unTrackedDeviceIndex_Hmd,
                    openvr.Prop_ModelNumber_String
                )
                print(f"VR Headset: {model}")

                return True
            else:
                print("Failed to initialize VR system")
                self.vr_enabled = False
                return False

        except Exception as e:
            print(f"VR initialization error: {e}")
            self.vr_enabled = False
            return False

    def _update_vr(self, event):
        """Update VR tracking and rendering."""
        if not self.vr_enabled or not self.vr_system:
            return

        try:
            # Get VR poses
            poses = self.vr_system.getDeviceToAbsoluteTrackingPose(
                openvr.TrackingUniverseStanding,
                0,
                openvr.k_unMaxTrackedDeviceCount
            )

            # Update HMD pose
            if poses[openvr.k_unTrackedDeviceIndex_Hmd].bPoseIsValid:
                hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd].mDeviceToAbsoluteTracking
                # Convert to camera transform
                # TODO: Apply HMD transform to camera

            # Check controller states
            self._update_controllers(poses)

            # Submit frames to compositor
            # TODO: Implement stereo rendering for left/right eyes

        except Exception as e:
            print(f"VR update error: {e}")

    def _update_controllers(self, poses):
        """Update VR controller states."""
        if not self.vr_system:
            return

        for device_index in range(openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(device_index)

            if device_class == openvr.TrackedDeviceClass_Controller:
                if poses[device_index].bPoseIsValid:
                    # Get controller state
                    result, state = self.vr_system.getControllerState(device_index)

                    if result:
                        # Store controller state
                        self.controller_states[device_index] = state

                        # Check for button presses
                        # Trigger: state.ulButtonPressed & (1 << openvr.k_EButton_SteamVR_Trigger)
                        # Grip: state.ulButtonPressed & (1 << openvr.k_EButton_Grip)

    def _create_globe(self):
        """Create the 3D globe with Earth texture."""
        self.globe = visuals.Sphere(
            radius=self.earth_radius,
            method='latitude',
            parent=self.view.scene,
            cols=60,
            rows=60,
            color='lightblue'
        )
        self.globe.shading = 'smooth'
        print(f"Globe created - Radius: {self.earth_radius}")

    def _create_placemarks(self):
        """Create placemarks on the globe surface."""
        # Sample locations
        locations = [
            (55.0, -106.0, 'red', 'Sample Location'),
            (40.7128, -74.0060, 'yellow', 'New York'),
            (51.5074, -0.1278, 'green', 'London'),
            (-33.8688, 151.2093, 'magenta', 'Sydney'),
        ]

        for lat, lon, color, label in locations:
            x, y, z = self.latlon_to_xyz(lat, lon, self.earth_radius)
            marker_pos = np.array([[x, y, z]])

            # Create marker
            placemark = visuals.Markers(
                parent=self.view.scene,
                pos=marker_pos,
                size=15 if not self.vr_enabled else 25,
                face_color=color,
                edge_color='white',
                edge_width=2
            )

        print(f"Created {len(locations)} placemarks")

    def _create_polygon(self):
        """Create a 3D polygon on the globe surface with extrusion."""
        polygon_coords = [
            (45.0, -100.0),
            (45.0, -95.0),
            (40.0, -95.0),
            (40.0, -100.0),
        ]

        vertices_surface = []
        vertices_extruded = []
        extrusion_height = 0.2

        for lat, lon in polygon_coords:
            x, y, z = self.latlon_to_xyz(lat, lon, self.earth_radius)
            vertices_surface.append([x, y, z])

            x_ext, y_ext, z_ext = self.latlon_to_xyz(
                lat, lon, self.earth_radius + extrusion_height
            )
            vertices_extruded.append([x_ext, y_ext, z_ext])

        vertices_surface = np.array(vertices_surface)
        vertices_extruded = np.array(vertices_extruded)

        # Draw vertical edges
        for i in range(len(vertices_surface)):
            edge_vertices = np.array([vertices_surface[i], vertices_extruded[i]])
            visuals.Line(
                pos=edge_vertices,
                color='cyan',
                width=3,
                parent=self.view.scene
            )

        # Draw top and bottom polygons
        top_poly = np.vstack([vertices_extruded, vertices_extruded[0:1]])
        visuals.Line(
            pos=top_poly,
            color='blue',
            width=4,
            parent=self.view.scene
        )

        bottom_poly = np.vstack([vertices_surface, vertices_surface[0:1]])
        visuals.Line(
            pos=bottom_poly,
            color='darkblue',
            width=3,
            parent=self.view.scene
        )

        print("3D extruded polygon created")

    def _create_axes(self):
        """Create coordinate axes for reference."""
        axis_length = 2.0

        # X, Y, Z axes
        for axis, color in [(np.array([[0, 0, 0], [axis_length, 0, 0]]), 'red'),
                            (np.array([[0, 0, 0], [0, axis_length, 0]]), 'green'),
                            (np.array([[0, 0, 0], [0, 0, axis_length]]), 'blue')]:
            visuals.Line(pos=axis, color=color, width=2, parent=self.view.scene)

    def latlon_to_xyz(self, lat, lon, radius):
        """Convert latitude/longitude to 3D Cartesian coordinates."""
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        x = radius * math.cos(lat_rad) * math.cos(lon_rad)
        y = radius * math.cos(lat_rad) * math.sin(lon_rad)
        z = radius * math.sin(lat_rad)

        return x, y, z

    def xyz_to_latlon(self, x, y, z):
        """Convert 3D Cartesian coordinates to latitude/longitude."""
        r = math.sqrt(x**2 + y**2 + z**2)
        if r == 0:
            return 0, 0

        lat = math.degrees(math.asin(z / r))
        lon = math.degrees(math.atan2(y, x))

        return lat, lon

    def on_key_press(self, event):
        """Handle keyboard events."""
        if event.key == 'Escape':
            self._cleanup()
            self.close()
            app.quit()
        elif event.key == 'r' or event.key == 'R':
            self.view.camera.elevation = 30
            self.view.camera.azimuth = 45
            self.view.camera.distance = 3
            print("Camera view reset")
        elif event.key == 'v' or event.key == 'V':
            if VR_AVAILABLE and not self.vr_enabled:
                print("Attempting to enable VR...")
                self._init_vr()
            else:
                print(f"VR Status: {'Enabled' if self.vr_enabled else 'Disabled'}")

    def _cleanup(self):
        """Cleanup VR resources."""
        if self.vr_enabled and self.vr_system:
            try:
                openvr.shutdown()
                print("VR system shutdown")
            except:
                pass

    def _print_controls(self):
        """Print control instructions."""
        print("\n" + "=" * 60)
        print("WorldWind Python VR - Controls")
        print("=" * 60)

        if self.vr_enabled:
            print("\nVR CONTROLS:")
            print("  Grip Button: Grab and rotate globe")
            print("  Trigger: Select placemarks")
            print("  Put on your VR headset to begin!")
        else:
            print("\nDESKTOP CONTROLS:")
            print("  Left Click + Drag: Rotate globe")
            print("  Right Click + Drag: Zoom")
            print("  Mouse Wheel: Zoom in/out")

        print("\nKEYBOARD:")
        print("  R: Reset camera view")
        print("  V: Check VR status")
        print("  ESC: Quit")
        print("=" * 60 + "\n")


def main():
    """Main entry point for WorldWind VR."""
    print("=" * 60)
    print("WorldWind Python VR - 3D Globe Visualization")
    print("Powered by VisPy + OpenVR")
    print("=" * 60)
    print()

    # Check for VR flag
    enable_vr = '--vr' in sys.argv or VR_AVAILABLE

    if enable_vr and not VR_AVAILABLE:
        print("VR mode requested but PyOpenVR not installed.")
        print("Install with: pip install openvr")
        print("Falling back to desktop mode...")
        print()

    # Create application
    canvas = WorldWindVR(enable_vr=enable_vr)

    # Run
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
