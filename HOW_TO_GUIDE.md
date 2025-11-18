# WorldWind VR - Complete How-To Guide 🌍

**Your personal 3D globe with photos, friends, and VR exploration!**

---

## 📋 Table of Contents

1. [Quick Start - Unity C# VR](#unity-csharp-vr-version)
2. [Quick Start - Python VR](#python-vr-version)
3. [Adding Your Travel Photos](#adding-travel-photos-)
4. [Adding Friends](#adding-friends-)
5. [Cool Features You Can Add](#cool-features-available)
6. [Troubleshooting](#troubleshooting)

---

# Unity C# VR Version

## 🎮 Setup in 5 Steps (10 minutes)

### Step 1: Get Unity
```
1. Download Unity Hub → https://unity.com/download
2. Install Unity 2021.3 LTS (or newer)
3. Include: "XR Plugin Management" module
```

### Step 2: Create Project
```
1. Open Unity Hub
2. Click "New Project"
3. Choose "3D Core" template
4. Name: "My-WorldWind-VR"
5. Click "Create"
```

### Step 3: Enable VR
```
1. Edit → Project Settings
2. Click "XR Plugin Management"
3. Install it if prompted
4. Check ✅ "OpenXR" (for PC VR)
5. Check ✅ "Oculus" (for Quest)
```

### Step 4: Install Packages
```
1. Window → Package Manager
2. Click "+" → "Add package by name"
3. Add: com.unity.xr.interaction.toolkit
4. Add: com.unity.textmeshpro
5. Click "Import TMP Essentials" when prompted
```

### Step 5: Add WorldWind Scripts
```
1. Copy all .cs files from unity-csharp-vr/Assets/Scripts/
   to your Unity project's Assets/Scripts/ folder

2. In Unity Hierarchy:
   - Right-click → Create Empty
   - Name it "VR Setup"
   - Add Component → VRSetupManager

3. Create XR Rig:
   - GameObject → XR → Room-Scale XR Rig

4. Press Play! 🎮
```

## 🎯 Using Unity WorldWind VR

### Basic Controls
| What You Want | How To Do It |
|---------------|--------------|
| **Rotate Globe** | Grab with ONE hand (Grip button) → Move hand |
| **Scale Globe** | Grab with BOTH hands (Both Grips) → Move hands apart/together |
| **Select Location** | Point controller → Pull Trigger |
| **Reset View** | Press A (Oculus) or X (Index) button |

### Adding Your Travel Photos (Unity)

See the photo manager script below for automatic integration!

---

# Python VR Version

## 🐍 Setup in 3 Steps (5 minutes)

### Step 1: Install Python & Dependencies
```bash
# Make sure you have Python 3.7+ installed
python --version

# Navigate to the python-vispy folder
cd python-vispy

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Install VR Support (Optional)
```bash
# For VR support with SteamVR
pip install openvr

# Make sure SteamVR is installed and running
```

### Step 3: Run It!
```bash
# Desktop mode (no VR)
python worldwind.py

# VR mode (requires SteamVR)
python worldwind_vr.py
```

## 🎯 Using Python WorldWind

### Desktop Controls
| Action | Control |
|--------|---------|
| Rotate Globe | Left Click + Drag |
| Zoom | Mouse Wheel OR Right Click + Drag |
| Reset View | Press R |
| Quit | Press ESC |

### VR Controls
| Action | Control |
|--------|---------|
| Rotate Globe | Grip Button |
| Select | Trigger Button |
| Check VR Status | Press V |

---

# Adding Travel Photos 📸

## What You Can Do

- ✅ Upload photos from your travels
- ✅ Pin them to locations on the globe
- ✅ See photo thumbnails in 3D space
- ✅ Click photos to view full size (in VR or desktop)
- ✅ Add captions and dates
- ✅ Create photo routes (connect your journey)

## How To Add Photos

### Method 1: Using Python Script

```bash
# Use the photo manager (created below)
python add_travel_photo.py --photo "paris.jpg" --lat 48.8566 --lon 2.3522 --title "Eiffel Tower"
```

### Method 2: Using JSON Config

Create `my_travels.json`:
```json
{
  "travels": [
    {
      "photo": "photos/paris_eiffel.jpg",
      "latitude": 48.8566,
      "longitude": 2.3522,
      "title": "Eiffel Tower Visit",
      "date": "2023-06-15",
      "description": "Amazing sunset view!"
    },
    {
      "photo": "photos/tokyo_tower.jpg",
      "latitude": 35.6586,
      "longitude": 139.7454,
      "title": "Tokyo Tower",
      "date": "2023-09-20",
      "description": "Night lights were incredible"
    }
  ]
}
```

Then load it:
```bash
python worldwind_with_photos.py --config my_travels.json
```

### Method 3: In Unity (C#)

```csharp
// Add this to your script
PhotoPlacemarkManager photoManager = gameObject.AddComponent<PhotoPlacemarkManager>();

// Load a photo
photoManager.AddPhotoPlacemark(
    photoPath: "C:/Photos/paris.jpg",
    latitude: 48.8566f,
    longitude: 2.3522f,
    title: "Eiffel Tower",
    description: "Summer 2023"
);
```

---

# Adding Friends 👥

## What You Can Do

- ✅ Add friends as placemarks on their home cities
- ✅ See where all your friends are around the world
- ✅ Add profile pictures (if you have them)
- ✅ Click to see friend info
- ✅ Create friend groups with different colors

## How To Add Friends

### Using JSON Config

Create `my_friends.json`:
```json
{
  "friends": [
    {
      "name": "Sarah Johnson",
      "city": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "photo": "photos/friends/sarah.jpg",
      "color": "yellow",
      "group": "college"
    },
    {
      "name": "Mike Chen",
      "city": "San Francisco",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "photo": "photos/friends/mike.jpg",
      "color": "blue",
      "group": "work"
    },
    {
      "name": "Emma Schmidt",
      "city": "Berlin",
      "latitude": 52.5200,
      "longitude": 13.4050,
      "photo": "photos/friends/emma.jpg",
      "color": "green",
      "group": "college"
    }
  ]
}
```

Load it:
```bash
python worldwind_with_friends.py --friends my_friends.json
```

### Quick Add (Python)

```python
# In your Python script
from worldwind_extensions import FriendManager

friends = FriendManager(globe)

# Add friends
friends.add("Sarah", "New York", 40.7128, -74.0060, color="yellow")
friends.add("Mike", "San Francisco", 37.7749, -122.4194, color="blue")
friends.add("Emma", "Berlin", 52.5200, 13.4050, color="green")

# Show all friends
friends.show_all()
```

---

# Cool Features Available ✨

## 🌟 Already Built-In

- ✅ **3D Interactive Globe** - Smooth rotation and zoom
- ✅ **VR Support** - Full VR with Oculus/Index/Vive
- ✅ **Placemarks** - Pin locations on the globe
- ✅ **3D Polygons** - Show areas/regions with height
- ✅ **Coordinate Display** - See lat/lon in real-time
- ✅ **Desktop Mode** - Works without VR

## 🚀 Features We Can Add (Easy to Implement)

### 1. **Travel Routes** 🛫
Connect your travel photos with lines showing your journey
```python
globe.create_route([
    (48.8566, 2.3522),   # Paris
    (41.9028, 12.4964),  # Rome
    (35.6586, 139.7454)  # Tokyo
], color="cyan", animated=True)
```

### 2. **Time-Based Visualization** ⏰
Show placemarks based on dates - animate your journey over time
```python
globe.play_timeline(start_date="2023-01-01", end_date="2023-12-31")
```

### 3. **Photo Gallery Mode** 🖼️
Click a photo to see a VR slideshow of all photos from that location

### 4. **Weather Overlays** 🌤️
Show real-time weather data from APIs
```python
globe.add_weather_layer(api_key="your_key")
```

### 5. **Distance Measurements** 📏
Measure distances between two points
```python
distance = globe.measure_distance(
    from_lat=48.8566, from_lon=2.3522,  # Paris
    to_lat=40.7128, to_lon=-74.0060     # New York
)
print(f"Distance: {distance} km")
```

### 6. **Animated Flights** ✈️
Animate a flight path between cities
```python
globe.animate_flight(
    from_city="Paris",
    to_city="Tokyo",
    duration=5.0  # seconds
)
```

### 7. **Country Highlighting** 🗺️
Highlight entire countries
```python
globe.highlight_country("France", color="blue", opacity=0.3)
```

### 8. **Heat Maps** 🌡️
Show data as heat maps (travel frequency, friend density, etc.)
```python
globe.create_heatmap(data_points, intensity="visited_count")
```

### 9. **Notes & Memories** 📝
Attach text notes to locations
```python
globe.add_note(
    lat=48.8566, lon=2.3522,
    note="Best croissant at Café de Flore!",
    voice_memo="paris_note.mp3"  # Optional voice note
)
```

### 10. **Multi-User VR** 👥
See friends in VR with you, looking at the same globe

### 11. **AR Mode** 📱
Place the globe on your table using AR (Quest 3, phone ARKit/ARCore)

### 12. **Day/Night Cycle** 🌓
Show Earth's day/night terminator in real-time

### 13. **Satellite Imagery** 🛰️
Load real NASA Blue Marble or Bing Maps imagery

### 14. **Custom Markers** 🎨
Use custom icons for different types of places
```python
globe.add_placemark(
    lat=48.8566, lon=2.3522,
    icon="icons/restaurant.png",
    type="food"
)
```

### 15. **Export & Share** 📤
Export your globe as a 3D model or video
```python
globe.export_video("my_travels.mp4", duration=30)
```

---

# Troubleshooting

## Unity Issues

### "Scripts won't compile"
```
1. Check Unity Console (bottom of screen)
2. Make sure all .cs files are in Assets/Scripts/
3. Try: Assets → Reimport All
4. Restart Unity
```

### "VR not working"
```
1. SteamVR or Oculus app running?
2. Headset connected and on?
3. Edit → Project Settings → XR Plugin Management
4. Verify OpenXR or Oculus is checked ✅
5. Restart Unity
```

### "Globe not visible in VR"
```
1. Check globe position: (0, 1.5, 2)
2. Make sure you're looking forward
3. Try moving closer in VR
4. Check VR Setup Manager component is active
```

## Python Issues

### "Module not found"
```bash
# Install missing modules
pip install -r requirements.txt

# Or individually:
pip install vispy numpy pillow pyqt5
```

### "VR not working (Python)"
```bash
# Install OpenVR
pip install openvr

# Make sure SteamVR is running
# Check: python worldwind_vr.py
```

### "Photos not loading"
```python
# Check file paths are correct
# Use absolute paths:
photo_path = "C:/Users/YourName/Photos/paris.jpg"  # Windows
photo_path = "/home/user/Photos/paris.jpg"         # Linux
```

---

# Quick Reference Card

## 📌 File Locations

```
worldwind/
├── python-vispy/
│   ├── worldwind.py              ← Desktop version
│   ├── worldwind_vr.py           ← VR version
│   ├── worldwind_with_photos.py  ← With photo support
│   └── my_travels.json           ← Your photo config
│
└── unity-csharp-vr/
    ├── Assets/Scripts/
    │   ├── WorldWindGlobe.cs     ← Core globe
    │   ├── PhotoPlacemarkManager.cs  ← Photo support
    │   └── VRGlobeInteraction.cs ← VR controls
    └── README.md
```

## 🎮 Controls Summary

| Platform | Rotate | Zoom | Select | VR Grab |
|----------|--------|------|--------|---------|
| **Unity VR** | Grip | Both Grips | Trigger | Grip button |
| **Python VR** | Grip | - | Trigger | Grip button |
| **Python Desktop** | Left Drag | Wheel | Click | - |

---

# Next Steps

1. ✅ Set up your version (Unity OR Python)
2. ✅ Test it works with basic globe
3. ✅ Add your first travel photo
4. ✅ Add your friends
5. 🎨 Customize colors and styles
6. 🚀 Try advanced features (routes, animations)
7. 🎉 Show it off in VR!

---

**Need help? Check the full README files or create an issue!** 🙋‍♂️

**Have fun exploring your world! 🌍✨**
