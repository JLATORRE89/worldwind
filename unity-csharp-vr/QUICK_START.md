# WorldWind VR - Quick Start Guide

Get up and running with WorldWind VR in 10 minutes!

## Prerequisites

- [ ] Unity Hub installed
- [ ] Unity 2021.3 LTS or newer
- [ ] VR Headset (Oculus Quest, Rift, Index, Vive, etc.)
- [ ] VR Software running (Oculus app or SteamVR)

## Fast Setup (5 Steps)

### Step 1: Create Unity Project (2 min)

1. Open Unity Hub
2. Click "New Project"
3. Select "3D Core" template
4. Name: `WorldWind-VR`
5. Click "Create"

### Step 2: Enable VR (2 min)

1. Edit → Project Settings → XR Plugin Management
2. Click "Install XR Plugin Management"
3. Under **PC, Mac & Linux Standalone** tab:
   - ✅ Check "OpenXR"
4. Under **Android** tab (for Quest):
   - ✅ Check "Oculus"

### Step 3: Install Packages (2 min)

1. Window → Package Manager
2. Click "+" → "Add package by name"
3. Install these packages:
   - `com.unity.xr.interaction.toolkit`
   - `com.unity.textmeshpro`
   - `com.unity.inputsystem`
4. Import TMP Essential Resources if prompted

### Step 4: Add Scripts (2 min)

1. Copy these files to `Assets/Scripts/`:
   - `WorldWindGlobe.cs`
   - `VRGlobeInteraction.cs`
   - `VRCoordinateDisplay.cs`
   - `VRSetupManager.cs`

### Step 5: Setup Scene (2 min)

#### Automatic (Easiest):

1. GameObject → Create Empty
2. Name: "VR Setup Manager"
3. Add Component → `VRSetupManager`
4. GameObject → XR → Room-Scale XR Rig
5. **Press Play!** 🎮

#### Manual:

1. GameObject → XR → Room-Scale XR Rig
2. GameObject → Create Empty → Name: "WorldWind Globe"
   - Position: (0, 1.5, 2)
   - Add Component → `WorldWindGlobe`
   - Add Component → `VRGlobeInteraction`
3. **Press Play!** 🎮

## Controls

| Action | Button |
|--------|--------|
| Rotate Globe | Grip (one hand) |
| Scale Globe | Grip (two hands) |
| Select | Trigger |
| Reset | A/X Button |

## Troubleshooting

### "No VR Device Detected"

1. Check headset is on and connected
2. SteamVR or Oculus app running?
3. Try: Edit → Project Settings → XR Plugin Management → Restart Unity

### "Scripts won't compile"

1. Check Console for errors
2. Verify all packages installed
3. Try: Assets → Reimport All

### "Globe not visible"

1. Position: (0, 1.5, 2) - in front of camera
2. Check XR Rig is at (0, 0, 0)
3. Try moving closer in VR

## Next Steps

✨ **Add Earth Texture**: See README.md "Add Earth Texture" section
🎨 **Customize**: Modify globe size, colors, positions
📍 **Add Placemarks**: Use `globe.CreatePlacemark(lat, lon, color)`
🏗️ **Build for Quest**: See README.md "Build for Oculus Quest"

## Example Code

Add this to a new script to customize:

```csharp
using UnityEngine;

public class CustomSetup : MonoBehaviour
{
    void Start()
    {
        WorldWindGlobe globe = FindObjectOfType<WorldWindGlobe>();

        // Add your hometown
        globe.CreatePlacemark(40.7128f, -74.0060f, Color.yellow, "New York");

        // Add a region
        List<Vector2> coords = new List<Vector2>
        {
            new Vector2(45, -100),
            new Vector2(45, -95),
            new Vector2(40, -95),
            new Vector2(40, -100)
        };
        globe.CreateExtrudedPolygon(coords, 0.2f, Color.cyan);
    }
}
```

## Need Help?

- 📖 Read full README.md
- 🔍 Check Unity Console for errors
- 🎥 Unity XR Tutorials: [docs.unity3d.com](https://docs.unity3d.com/Manual/XR.html)

---

**Ready for VR? Put on your headset and press Play!** 🚀
