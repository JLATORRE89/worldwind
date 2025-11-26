# WorldWind Examples

Example configurations and usage patterns for WorldWind with photos, friends, and routes.

## 📁 Files in this Directory

- `my_travels.json` - Example travel photo configuration
- `my_friends.json` - Example friends configuration
- `combined_example.py` - Complete example with photos, friends, and routes

## 🖼️ Using Travel Photos

### Setup Your Photos

1. Create a `photos` directory:
   ```bash
   mkdir photos
   ```

2. Add your travel photos to the directory

3. Edit `my_travels.json` to match your photos:
   ```json
   {
     "travels": [
       {
         "photo": "photos/my_photo.jpg",
         "latitude": 48.8566,
         "longitude": 2.3522,
         "title": "My Trip",
         "description": "Amazing time!",
         "date": "2024-01-15"
       }
     ]
   }
   ```

### Run with Your Photos

```bash
# From the python-vispy directory
python worldwind_with_photos.py --config examples/my_travels.json
```

## 👥 Using Friends

### Setup Your Friends

Edit `my_friends.json`:
```json
{
  "friends": [
    {
      "name": "Your Friend",
      "city": "Their City",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "photo": "photos/friends/friend.jpg",
      "color": "yellow",
      "group": "college"
    }
  ]
}
```

### Run with Your Friends

```bash
python worldwind_with_friends.py --friends examples/my_friends.json
```

## 🗺️ Example: Complete Globe

Here's a complete example combining everything:

```python
#!/usr/bin/env python
from worldwind_with_photos import WorldWindWithPhotos
from worldwind_extensions import TravelRoute, DistanceMeasurement
from vispy import app

# Create globe
globe = WorldWindWithPhotos()

# Load your travels
globe.load_from_json('examples/my_travels.json')

# Add routes between your travels
routes = TravelRoute(globe)

# Create a route from Paris → Rome → Tokyo
routes.create_route([
    (48.8566, 2.3522),   # Paris
    (41.8902, 12.4964),  # Rome
    (35.6586, 139.7454)  # Tokyo
], color='cyan', name='Europe to Asia Trip')

# Measure distance from New York to London
distance_tool = DistanceMeasurement(globe)
nyc_to_london = distance_tool.measure_and_display(
    (40.7128, -74.0060),  # NYC
    (51.5074, -0.1278),   # London
    unit='mi'
)

print(f"Distance NYC to London: {nyc_to_london['distance']:.0f} miles")

# Run the application
app.run()
```

Save this as `my_globe.py` and run:
```bash
python my_globe.py
```

## 📸 Photo Requirements

- **Formats**: JPG, PNG
- **Recommended Size**: 1024x1024 or smaller (for performance)
- **Location**: Store in `photos/` directory
- **Paths**: Can be absolute or relative to JSON file

## 🎨 Color Options for Friends

Available colors:
- `red`, `yellow`, `blue`, `green`
- `cyan`, `magenta`, `orange`, `purple`
- `white`, `pink`

## 🏷️ Friend Groups

Default groups:
- `family` - Red markers
- `friends` - Yellow markers
- `work` - Blue markers
- `college` - Green markers
- `high_school` - Orange markers

You can add custom groups with custom colors!

## 🗺️ Getting Coordinates

### From Google Maps
1. Right-click on a location
2. Click the coordinates at the top
3. Copy latitude, longitude

### From Wikipedia
1. Find the location's Wikipedia page
2. Look for coordinates in the top-right
3. Use decimal format (e.g., 48.8566, not 48°51'24"N)

## 💡 Tips

### Performance
- Use compressed images (JPG with ~80% quality)
- Limit photos to <100 for smooth performance
- Use lower globe resolution if needed (edit `cols` and `rows` in `worldwind.py`)

### Organization
```
python-vispy/
├── photos/
│   ├── travels/
│   │   ├── 2023/
│   │   └── 2024/
│   └── friends/
│       ├── family/
│       ├── work/
│       └── college/
├── examples/
│   ├── my_travels_2023.json
│   ├── my_travels_2024.json
│   └── my_friends.json
└── worldwind_with_photos.py
```

### Batch Processing
Create multiple JSON files for different trips/years and load them separately!

## 🚀 Advanced Usage

### Combining Photos and Friends

```python
from worldwind_with_photos import WorldWindWithPhotos
from worldwind_with_friends import Friend

# Create globe with photos
globe = WorldWindWithPhotos()
globe.load_from_json('examples/my_travels.json')

# Manually add friends (since we inherit from WorldWind)
# ... add friend markers ...

app.run()
```

### Creating Routes from JSON

```json
{
  "routes": [
    {
      "name": "Summer 2023",
      "color": "cyan",
      "waypoints": [
        {"lat": 48.8566, "lon": 2.3522},
        {"lat": 41.8902, "lon": 12.4964},
        {"lat": 35.6586, "lon": 139.7454}
      ]
    }
  ]
}
```

## 📚 More Examples

Check the main `python-vispy/` directory for more scripts:

- `worldwind.py` - Basic globe
- `worldwind_vr.py` - VR version
- `worldwind_with_photos.py` - Travel photos
- `worldwind_with_friends.py` - Friend locations
- `worldwind_extensions.py` - Routes, distances, animations

## ❓ Need Help?

- Check `../README.md` for installation instructions
- Check `../HOW_TO_GUIDE.md` for detailed usage
- Look at the example JSON files in this directory

---

**Have fun creating your personal globe! 🌍✨**
