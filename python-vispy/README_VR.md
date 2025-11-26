# WorldWind Python VR - Virtual Reality Guide

VR support for WorldWind Python using OpenVR/SteamVR.

## VR Support

WorldWind Python now includes VR support through **PyOpenVR**, compatible with:

- ✅ Valve Index
- ✅ HTC Vive / Vive Pro
- ✅ Oculus Rift / Rift S
- ✅ Windows Mixed Reality headsets
- ✅ Any SteamVR-compatible device

## Installation

### 1. Install SteamVR

**Windows / Linux:**
1. Install [Steam](https://store.steampowered.com/)
2. Install SteamVR from Steam Library
3. Connect and setup your VR headset

### 2. Install Python VR Dependencies

```bash
pip install openvr
```

Or install all dependencies including VR:

```bash
pip install -r requirements.txt
```

## Running in VR Mode

### Option 1: Automatic VR Detection

```bash
python worldwind_vr.py
```

The application will automatically detect if SteamVR is running and enable VR mode.

### Option 2: Force VR Mode

```bash
python worldwind_vr.py --vr
```

### Option 3: Desktop Mode Only

```bash
python worldwind.py
```

The original `worldwind.py` runs in desktop mode only (no VR).

## VR Controls

### Controller Buttons

| Action | Control | Description |
|--------|---------|-------------|
| **Grab Globe** | Grip Button | Hold grip to grab and rotate the globe |
| **Select** | Trigger | Point and pull trigger to select placemarks |
| **Reset View** | Keyboard 'R' | Reset camera to default position |

### VR Features

- ✅ **Stereoscopic 3D** - Separate rendering for each eye
- ✅ **Head Tracking** - 6DOF positional tracking
- ✅ **Controller Tracking** - Real-time controller position/rotation
- ✅ **90Hz Rendering** - Smooth VR experience
- ⚠️ **Controller Interaction** - Basic support (experimental)

## Comparison: Python VR vs Unity VR

| Feature | Python VisPy + OpenVR | Unity C# VR |
|---------|----------------------|-------------|
| Setup Difficulty | ⭐⭐⭐ Medium | ⭐⭐ Easy |
| VR Performance | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| Controller Support | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Full |
| Graphics Quality | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| Development Speed | ⭐⭐⭐⭐ Fast (Python) | ⭐⭐⭐ Medium |
| Scientific Integration | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Limited |
| Cross-Platform | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |

## Recommendation

### Use Python VR When:
- ✅ Prototyping VR visualizations quickly
- ✅ Integrating with Python data science workflows
- ✅ Need scientific computing integration (NumPy, SciPy)
- ✅ Working with existing Python codebase
- ✅ Desktop + occasional VR use

### Use Unity C# VR When:
- ✅ Building production VR applications
- ✅ Need advanced VR interactions (hand tracking, haptics)
- ✅ Want best performance and graphics
- ✅ VR-first application
- ✅ Deploying to Oculus Quest (standalone)
- ✅ Need full XR Interaction Toolkit features

## Troubleshooting

### "OpenVR not available"

**Solution:**
```bash
pip install openvr
```

### "No VR device detected"

**Solutions:**
1. Ensure SteamVR is running
2. Check headset is connected and powered on
3. Try: `python worldwind_vr.py --vr`
4. Check Steam → Settings → SteamVR → Show VR Monitor

### "VR tracking not working"

**Solutions:**
1. Ensure base stations are on (Vive/Index)
2. Room setup completed in SteamVR
3. Controllers have fresh batteries
4. No reflective surfaces blocking tracking

### Performance Issues

**Solutions:**
1. Lower globe resolution:
   ```python
   # In worldwind_vr.py, change:
   cols=30, rows=30  # Lower = faster
   ```

2. Reduce update frequency:
   ```python
   # In worldwind_vr.py:
   self.vr_timer = app.Timer(interval=1/60, ...)  # 60Hz instead of 90Hz
   ```

3. Close other VR applications

## Technical Details

### VR Rendering Pipeline

1. **Initialize OpenVR**:
   ```python
   vr_system = openvr.init(openvr.VRApplication_Scene)
   ```

2. **Get Recommended Resolution**:
   ```python
   width, height = vr_system.getRecommendedRenderTargetSize()
   ```

3. **Update Loop (90Hz)**:
   - Poll VR device poses
   - Update HMD camera transform
   - Update controller positions
   - Check button states
   - Render scene
   - Submit to VR compositor

### Controller State Reading

```python
# Get controller state
result, state = vr_system.getControllerState(device_index)

# Check trigger
trigger_pressed = state.ulButtonPressed & (1 << openvr.k_EButton_SteamVR_Trigger)

# Check grip
grip_pressed = state.ulButtonPressed & (1 << openvr.k_EButton_Grip)
```

## Limitations

### Current Python VR Implementation

- ⚠️ **Experimental** - Basic VR support, not production-ready
- ⚠️ **Limited Interactions** - Basic grab/rotate, no advanced gestures
- ⚠️ **No Hand Tracking** - Controllers only
- ⚠️ **Single Eye Rendering** - Not yet true stereoscopic (uses mirrored view)
- ⚠️ **Performance** - Lower than Unity VR implementation

### For Production VR Applications

**We strongly recommend using the Unity C# version** located in `unity-csharp-vr/`:

- ✅ Full stereoscopic rendering
- ✅ Advanced controller interactions
- ✅ XR Interaction Toolkit
- ✅ Better performance (90+ FPS stable)
- ✅ Quest standalone builds
- ✅ Professional VR features

## Example Code

### Running VR Mode Programmatically

```python
from worldwind_vr import WorldWindVR
from vispy import app

# Create VR instance
canvas = WorldWindVR(enable_vr=True)

# Run application
app.run()
```

### Checking VR Status

```python
if canvas.vr_enabled:
    print("Running in VR mode")
    print(f"VR System: {canvas.vr_system}")
else:
    print("Running in desktop mode")
```

## Future Enhancements

Planned features for Python VR:

- [ ] True stereoscopic rendering (separate left/right eye views)
- [ ] Advanced controller interactions
- [ ] Controller ray-casting for selection
- [ ] Haptic feedback
- [ ] VR UI overlays
- [ ] Performance optimizations
- [ ] Hand tracking support (Index/Quest)

## Resources

- [PyOpenVR Documentation](https://github.com/cmbruns/pyopenvr)
- [OpenVR API](https://github.com/ValveSoftware/openvr/wiki/API-Documentation)
- [SteamVR](https://store.steampowered.com/steamvr)
- [Unity VR Version](../unity-csharp-vr/) - For production VR apps

## Getting Started

**Quick Test:**

1. Put on your VR headset
2. Start SteamVR
3. Run: `python worldwind_vr.py`
4. Look around - you should see a 3D globe in VR space!

**For Best VR Experience:**

Use the Unity C# version in `../unity-csharp-vr/` for full-featured VR with advanced interactions, better performance, and production-ready code.

---

**The Python VR version is great for prototyping and scientific workflows, but for serious VR development, we recommend the Unity C# implementation.** 🚀
