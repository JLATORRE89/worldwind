# WorldWind Python - VisPy 3D Globe Visualization

A Python port of NASA WorldWind using VisPy for high-performance 3D interactive globe visualization.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

This Python implementation provides the following features from the original WorldWind:

- ✨ **Interactive 3D Globe** - Smooth rotation, zoom, and pan controls
- 🌍 **Earth Visualization** - 3D sphere with Blue Marble imagery support
- 📍 **Placemarks** - Add markers at specific lat/lon coordinates
- 🔷 **3D Polygons** - Polygons with extrusion (3D elevation)
- 🎮 **Interactive Controls** - Mouse and keyboard controls
- 📊 **Coordinate Display** - Real-time coordinate tracking
- ⚡ **High Performance** - Powered by VisPy's OpenGL backend

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- OpenGL-capable graphics card

### Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd worldwind/python-vispy
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: You need to install one of the GUI backends (PyQt5, PyQt6, or PySide6):
   ```bash
   # Choose one:
   pip install PyQt5        # Recommended
   # OR
   pip install PyQt6
   # OR
   pip install PySide6
   ```

## Usage

### Running the Application

```bash
python worldwind.py
```

### Controls

#### Mouse Controls
- **Left Click + Drag**: Rotate the globe
- **Right Click + Drag**: Zoom in/out
- **Middle Click + Drag**: Pan the view
- **Mouse Wheel**: Zoom in/out

#### Keyboard Controls
- **R**: Reset camera to default view
- **H**: Display help in console
- **ESC**: Quit application

## Architecture

### Project Structure

```
python-vispy/
├── worldwind.py          # Main application file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Key Components

#### WorldWind Class
The main application class that extends `scene.SceneCanvas`:
- Manages the 3D scene and camera
- Handles user interactions
- Coordinates all visual elements

#### Globe Rendering
- Uses VisPy's `Sphere` visual for the Earth
- Supports texture mapping for realistic imagery
- Smooth shading for visual quality

#### Coordinate System
- **Latitude**: -90° (South Pole) to +90° (North Pole)
- **Longitude**: -180° (West) to +180° (East)
- Conversion functions: `latlon_to_xyz()` and `xyz_to_latlon()`

### Example: Adding Custom Placemarks

```python
# Convert lat/lon to 3D coordinates
lat, lon = 40.7128, -74.0060  # New York City
x, y, z = worldwind_instance.latlon_to_xyz(lat, lon, 1.0)

# Create marker
marker_pos = np.array([[x, y, z]])
marker = visuals.Markers(
    parent=view.scene,
    pos=marker_pos,
    size=15,
    face_color='red',
    edge_color='white',
    edge_width=2
)
```

## Comparison with JavaScript WorldWind

| Feature | JavaScript WorldWind | Python VisPy Port |
|---------|---------------------|-------------------|
| 3D Globe | ✅ WebGL | ✅ OpenGL |
| Placemarks | ✅ | ✅ |
| Polygons | ✅ | ✅ |
| 3D Extrusion | ✅ | ✅ |
| WMS Layers | ✅ | 🚧 Planned |
| 3D Models | ✅ COLLADA | 🚧 Planned |
| Textures | ✅ Blue Marble | ✅ Supported |
| Interactive | ✅ | ✅ |

## Advanced Features

### Adding Earth Textures

To add realistic Earth textures (Blue Marble):

1. Download a Blue Marble texture from NASA:
   - [Blue Marble Next Generation](https://visibleearth.nasa.gov/collection/1484/blue-marble)
   - Recommended: 2048x1024 or 4096x2048 resolution

2. Save the texture as `earth_texture.jpg` in the same directory

3. Modify the globe creation code:
   ```python
   from vispy import io

   # Load texture
   texture = io.read_png('earth_texture.jpg')

   # Apply to globe
   self.globe = visuals.Sphere(
       radius=self.earth_radius,
       method='latitude',
       parent=self.view.scene,
       cols=60,
       rows=60
   )
   # Apply texture (implementation varies based on VisPy version)
   ```

### Performance Optimization

For better performance with large datasets:

- Reduce sphere resolution (cols/rows) for faster rendering
- Use Level of Detail (LOD) techniques
- Implement frustum culling for off-screen objects
- Use instancing for multiple similar objects

## Troubleshooting

### Issue: Black screen or no display
**Solution**: Ensure you have a GUI backend installed (PyQt5, PyQt6, or PySide6)

### Issue: ImportError for VisPy
**Solution**:
```bash
pip install --upgrade vispy
```

### Issue: Slow performance
**Solution**:
- Update graphics drivers
- Reduce sphere resolution in `create_sphere()` parameters
- Close other GPU-intensive applications

### Issue: "Interactive mode requires a GUI backend"
**Solution**: Install PyQt5:
```bash
pip install PyQt5
```

## Development

### Adding New Features

To add new features, modify `worldwind.py`:

1. **New Visual Elements**: Add in the `__init__` method
2. **Event Handlers**: Add methods like `on_mouse_move()`, `on_key_press()`
3. **Helper Functions**: Add utility methods to the `WorldWind` class

### Contributing

Contributions are welcome! Please follow these guidelines:
- Use PEP 8 style guide
- Add docstrings to functions and classes
- Test with Python 3.7+
- Update README for new features

## References

- [NASA WorldWind](https://worldwind.arc.nasa.gov/)
- [VisPy Documentation](http://vispy.org/)
- [Blue Marble Imagery](https://visibleearth.nasa.gov/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Original WorldWind: NASA
- Python VisPy Port: Claude AI Assistant

## Acknowledgments

- NASA for the WorldWind concept and imagery
- VisPy team for the excellent visualization library
- OpenGL community for graphics standards
