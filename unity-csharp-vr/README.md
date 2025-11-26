# WorldWind VR - Unity C# Edition

A fully VR-ready 3D globe visualization application built with Unity and C#, supporting Oculus, SteamVR, and OpenXR.

![Unity Version](https://img.shields.io/badge/Unity-2021.3%2B-blue)
![VR Ready](https://img.shields.io/badge/VR-Ready-green)
![C#](https://img.shields.io/badge/C%23-10.0-purple)

## Features

### ✨ VR Capabilities

- **🎮 Full VR Controller Support**
  - One-handed grab and rotate
  - Two-handed pinch to scale and rotate
  - Trigger-based selection and interaction
  - Haptic feedback (when supported)

- **👁️ Stereoscopic 3D Rendering**
  - Native VR rendering for Oculus Quest, Rift, Index, Vive, etc.
  - OpenXR support for cross-platform compatibility
  - 90+ FPS for smooth VR experience

- **🌐 Interactive Globe**
  - Procedurally generated UV sphere mesh
  - Real-time coordinate conversion (lat/lon ↔ XYZ)
  - Texture mapping for Earth imagery
  - Smooth rotation and scaling

- **📍 Placemarks & Annotations**
  - 3D markers at geographic locations
  - Interactive selection with VR controllers
  - Information display in VR space

- **🔷 3D Polygons**
  - Extruded polygons with custom height
  - Multiple visualization styles
  - Geographic boundary representation

- **📊 VR UI System**
  - World-space UI panels
  - Real-time coordinate display
  - Controller-attached or camera-relative positioning
  - TextMeshPro for crisp text rendering

## System Requirements

### Minimum Requirements
- Unity 2021.3 LTS or newer
- VR Headset: Oculus Quest/Rift, HTC Vive, Valve Index, or OpenXR-compatible device
- GPU: NVIDIA GTX 1060 / AMD RX 580 or better
- RAM: 8 GB
- OS: Windows 10/11, macOS, or Linux

### Recommended
- Unity 2022.3 LTS
- GPU: NVIDIA RTX 2060 / AMD RX 5700 or better
- RAM: 16 GB
- SSD for faster loading

## Installation

### 1. Unity Setup

1. **Install Unity Hub**: Download from [unity.com](https://unity.com/download)

2. **Install Unity 2021.3 LTS or newer**:
   ```bash
   # Include these modules:
   - Windows/Mac/Linux Build Support
   - Android Build Support (for Quest)
   - XR Plugin Management
   ```

3. **Create New Unity Project**:
   - Open Unity Hub
   - Click "New Project"
   - Select "3D Core" template
   - Name: "WorldWind-VR"
   - Click "Create"

### 2. Configure XR Plugin Management

1. **Open Project Settings**:
   - Edit → Project Settings → XR Plugin Management

2. **Install XR Plugin Management** (if not installed):
   - Click "Install XR Plugin Management"

3. **Enable VR Support**:

   **For PC VR (Oculus Rift, Valve Index, Vive):**
   - Select "PC, Mac & Linux Standalone" tab
   - Check "OpenXR" or "Oculus" (for Oculus devices)
   - Check "Windows Mixed Reality" (if using WMR headsets)

   **For Oculus Quest:**
   - Select "Android" tab
   - Check "Oculus"

4. **Configure OpenXR** (recommended for cross-platform):
   - Edit → Project Settings → XR Plug-in Management → OpenXR
   - Add Interaction Profiles:
     - Oculus Touch Controller Profile
     - Valve Index Controller Profile
     - HTC Vive Controller Profile

### 3. Install Required Packages

Open **Package Manager** (Window → Package Manager) and install:

1. **XR Interaction Toolkit**:
   - Click "+" → "Add package by name"
   - Enter: `com.unity.xr.interaction.toolkit`
   - Click "Add"

2. **TextMeshPro**:
   - Search for "TextMeshPro" in Package Manager
   - Click "Install"
   - Import "TMP Essential Resources" when prompted

3. **Input System** (if prompted):
   - Install new Input System
   - Allow Unity to restart

### 4. Import WorldWind Scripts

1. **Copy Scripts**:
   - Copy all files from `Assets/Scripts/` to your Unity project's `Assets/Scripts/` folder:
     - `WorldWindGlobe.cs`
     - `VRGlobeInteraction.cs`
     - `VRCoordinateDisplay.cs`
     - `VRSetupManager.cs`

2. **Verify Import**:
   - Check Unity Console for any errors
   - Scripts should appear in Project window

### 5. Scene Setup

#### Option A: Automated Setup (Recommended)

1. **Create Setup GameObject**:
   - In Hierarchy: Right-click → Create Empty
   - Name: "VR Setup Manager"

2. **Add Script**:
   - Select "VR Setup Manager"
   - In Inspector: Add Component → VRSetupManager

3. **Configure**:
   - Auto Start VR: ✓
   - Allow Desktop Fallback: ✓
   - Globe Position: (0, 1.5, 2)
   - Globe Scale: 1.0

4. **Press Play** - The globe will be created automatically!

#### Option B: Manual Setup

1. **Create XR Rig**:
   - GameObject → XR → Room-Scale XR Rig
   - This creates camera and controller tracking

2. **Create Globe**:
   - GameObject → 3D Object → Create Empty
   - Name: "WorldWind Globe"
   - Position: (0, 1.5, 2)

3. **Add Scripts to Globe**:
   - Select "WorldWind Globe"
   - Add Component → WorldWindGlobe
   - Add Component → VRGlobeInteraction

4. **Create Coordinate Display**:
   - GameObject → Create Empty
   - Name: "VR Coordinate Display"
   - Add Component → VRCoordinateDisplay

5. **Configure References**:
   - In VRCoordinateDisplay Inspector:
     - Left Controller Transform: Drag "LeftHand Controller" from XR Rig
     - Right Controller Transform: Drag "RightHand Controller" from XR Rig

### 6. Add Earth Texture (Optional)

1. **Download Earth Texture**:
   - Visit [NASA Visible Earth](https://visibleearth.nasa.gov/)
   - Download Blue Marble image (2048x1024 or 4096x2048)

2. **Import to Unity**:
   - Drag texture into `Assets/Materials/` folder
   - Select texture in Project window
   - In Inspector:
     - Texture Type: Default
     - Wrap Mode: Clamp
     - Filter Mode: Trilinear
     - Click "Apply"

3. **Create Material**:
   - Right-click in Project → Create → Material
   - Name: "Earth Material"
   - Shader: Standard
   - Albedo: Drag Earth texture here

4. **Apply to Globe**:
   - Select "WorldWind Globe" in Hierarchy
   - In WorldWindGlobe component:
     - Earth Material: Drag "Earth Material"
     - Earth Texture: Drag Earth texture

## Usage

### Running in VR

1. **Connect VR Headset**:
   - Turn on your VR headset
   - Ensure SteamVR or Oculus software is running

2. **Start Application**:
   - Press Play in Unity Editor
   - Or build and run (File → Build and Run)

3. **Put on Headset**:
   - You should see the 3D globe floating in front of you

### VR Controls

#### Basic Controls

| Action | Control | Description |
|--------|---------|-------------|
| **Grab & Rotate** | Grip Button (one hand) | Hold grip and move hand to rotate globe |
| **Scale & Rotate** | Grip Button (both hands) | Pinch to scale, rotate both hands to spin |
| **Select/Info** | Trigger Button | Point at placemark and pull trigger for info |
| **Reset Globe** | A/X Button | Reset globe to default position and size |

#### Advanced Controls

- **Precision Rotation**: Use one hand grip and make small movements
- **Globe Scaling**: Use two-hand grip and move hands apart/together
- **Coordinate Display**: Point controller at globe to see lat/lon
- **Placemark Selection**: Aim controller ray at marker and pull trigger

### Desktop Mode (Non-VR)

If no VR headset is detected:

1. **Mouse Controls**:
   - Left Click + Drag: Rotate globe
   - Right Click + Drag: Zoom
   - Middle Click + Drag: Pan

2. **Keyboard**:
   - R: Reset globe
   - ESC: Quit application

## Scripts Reference

### WorldWindGlobe.cs

Core globe rendering and geographic utilities.

```csharp
public class WorldWindGlobe : MonoBehaviour
{
    // Convert lat/lon to 3D position
    public Vector3 LatLonToXYZ(float latitude, float longitude, float altitude = 0)

    // Convert 3D position to lat/lon
    public Vector2 XYZToLatLon(Vector3 position)

    // Create a placemark
    public GameObject CreatePlacemark(float latitude, float longitude, Color color, string label = "")

    // Create extruded polygon
    public GameObject CreateExtrudedPolygon(List<Vector2> latLonCoordinates, float extrusionHeight, Color color)
}
```

### VRGlobeInteraction.cs

VR controller interaction handling.

```csharp
public class VRGlobeInteraction : MonoBehaviour
{
    // Enable/disable grab rotation
    [SerializeField] private bool enableGrabRotation = true;

    // Enable/disable two-handed scaling
    [SerializeField] private bool enableTwoHandedScale = true;

    // Reset globe to default state
    public void ResetGlobe()
}
```

### VRCoordinateDisplay.cs

VR UI for coordinate and information display.

```csharp
public class VRCoordinateDisplay : MonoBehaviour
{
    // Show custom message
    public void ShowMessage(string message, float duration = 3.0f)

    // Show placemark info
    public void ShowPlacemarkInfo(string name, float latitude, float longitude)

    // Toggle display visibility
    public void ToggleDisplay(bool visible)
}
```

### VRSetupManager.cs

Manages VR initialization and scene setup.

```csharp
public class VRSetupManager : MonoBehaviour
{
    // Get globe instance
    public GameObject GetGlobe()

    // Check if VR is enabled
    public bool IsVREnabled()

    // Reset globe position
    public void ResetGlobePosition()
}
```

## Building for Different Platforms

### Build for PC VR (Windows)

1. **File → Build Settings**
2. **Platform**: PC, Mac & Linux Standalone
3. **Target Platform**: Windows
4. **Click "Build"**
5. **Run the .exe** with VR headset connected

### Build for Oculus Quest

1. **File → Build Settings**
2. **Platform**: Android
3. **Switch Platform**
4. **Player Settings**:
   - Company Name: Your name
   - Product Name: WorldWind VR
   - Minimum API Level: Android 10.0 (API 29)
5. **XR Settings**:
   - Enable "Oculus"
6. **Build and Run** (Quest connected via USB)

### Build for SteamVR

1. Same as PC VR build
2. **Ensure SteamVR is installed**
3. **In Project Settings → XR Plugin Management**:
   - Enable "OpenXR" or "SteamVR"
4. **Build and distribute via Steam**

## Customization

### Adding Custom Placemarks

```csharp
// In your script:
WorldWindGlobe globe = FindObjectOfType<WorldWindGlobe>();

// Add placemark at New York City
globe.CreatePlacemark(40.7128f, -74.0060f, Color.yellow, "NYC");

// Add placemark at Tokyo
globe.CreatePlacemark(35.6762f, 139.6503f, Color.red, "Tokyo");
```

### Creating Custom Polygons

```csharp
// Define coordinates
List<Vector2> coords = new List<Vector2>
{
    new Vector2(45.0f, -100.0f),  // NW
    new Vector2(45.0f, -95.0f),   // NE
    new Vector2(40.0f, -95.0f),   // SE
    new Vector2(40.0f, -100.0f)   // SW
};

// Create extruded polygon
globe.CreateExtrudedPolygon(coords, 0.3f, Color.cyan);
```

### Changing Globe Appearance

```csharp
// In WorldWindGlobe Inspector:
- Latitude Segments: 60 (more = smoother)
- Longitude Segments: 120 (more = smoother)
- Globe Radius: 1.0 (larger = bigger globe)
```

## Troubleshooting

### VR Headset Not Detected

1. **Check XR Plugin Management**:
   - Edit → Project Settings → XR Plugin Management
   - Verify correct plugin is enabled for your platform

2. **Restart Unity**: Sometimes XR plugins need a restart

3. **Check Headset Software**:
   - Oculus: Oculus app running?
   - SteamVR: SteamVR running?

### Globe Not Appearing

1. **Check Console**: Look for errors in Unity Console
2. **Verify Position**: Globe default position is (0, 1.5, 2)
3. **Check Camera**: Make sure XR Rig camera can see the globe

### Controllers Not Working

1. **Check Controller Binding**:
   - Edit → Project Settings → XR Plug-in Management → OpenXR
   - Verify interaction profiles are added

2. **Test in VR Preview**: Use XR Device Simulator for testing

3. **Check Input System**: Ensure new Input System is enabled

### Performance Issues

1. **Reduce Globe Resolution**:
   - Lower Latitude/Longitude Segments to 30/60

2. **Optimize Textures**:
   - Use compressed texture formats
   - Reduce resolution to 2048x1024

3. **Lower Graphics Quality**:
   - Edit → Project Settings → Quality
   - Select "Medium" or "Low" preset

### Build Errors

1. **Missing Dependencies**:
   - Verify all packages are installed
   - Reimport scripts

2. **Platform Settings**:
   - Check minimum API level for Android
   - Verify XR backend is enabled

## Performance Optimization

### For Quest/Mobile VR

- Use simplified shaders (Mobile/Diffuse)
- Reduce polygon count (30 lat x 60 lon segments)
- Use texture compression (ASTC)
- Limit placemarks to < 100

### For PC VR

- Can use higher quality (60 lat x 120 lon segments)
- Use Standard shader with full lighting
- Support more placemarks and polygons
- Enable anti-aliasing

## Future Enhancements

- [ ] WMS layer integration
- [ ] Animated weather overlays
- [ ] Time-based visualization
- [ ] Multi-user VR collaboration
- [ ] Hand tracking support (Quest 2/3)
- [ ] Passthrough AR mode (Quest 3)
- [ ] Voice commands
- [ ] Custom Earth data import

## Resources

- [Unity XR Documentation](https://docs.unity3d.com/Manual/XR.html)
- [XR Interaction Toolkit](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest)
- [OpenXR](https://www.khronos.org/openxr/)
- [NASA Visible Earth](https://visibleearth.nasa.gov/)

## License

MIT License - see LICENSE file

## Credits

- Original WorldWind: NASA
- Unity VR Port: Claude AI Assistant
- Blue Marble Imagery: NASA

## Support

For issues or questions:
1. Check Unity Console for errors
2. Review this README troubleshooting section
3. Check Unity XR documentation
4. Test with XR Device Simulator
