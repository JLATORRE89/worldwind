using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.Management;

/// <summary>
/// VR Setup Manager
/// Handles VR initialization and configuration for WorldWind
/// </summary>
public class VRSetupManager : MonoBehaviour
{
    [Header("VR Settings")]
    [SerializeField] private bool autoStartVR = true;
    [SerializeField] private bool allowDesktopFallback = true;

    [Header("Globe Settings")]
    [SerializeField] private GameObject globePrefab;
    [SerializeField] private Vector3 globePosition = new Vector3(0, 1.5f, 2.0f);
    [SerializeField] private float globeScale = 1.0f;

    [Header("VR Rig")]
    [SerializeField] private Transform vrRigTransform;
    [SerializeField] private Transform leftController;
    [SerializeField] private Transform rightController;
    [SerializeField] private Transform headTransform;

    private GameObject globeInstance;
    private bool vrEnabled = false;

    void Start()
    {
        // Check if VR is supported
        if (XRSettings.isDeviceActive)
        {
            Debug.Log($"VR Device Active: {XRSettings.loadedDeviceName}");
            vrEnabled = true;
        }
        else
        {
            Debug.Log("No VR device detected");

            if (autoStartVR)
            {
                StartCoroutine(InitializeXR());
            }
            else if (!allowDesktopFallback)
            {
                Debug.LogWarning("VR required but not available. Set allowDesktopFallback to true for desktop mode.");
                return;
            }
        }

        // Create the globe
        CreateGlobe();

        // Setup VR rig if in VR mode
        if (vrEnabled)
        {
            SetupVRRig();
        }

        // Display instructions
        ShowInstructions();
    }

    /// <summary>
    /// Initialize XR subsystem
    /// </summary>
    System.Collections.IEnumerator InitializeXR()
    {
        Debug.Log("Initializing XR...");

        if (XRGeneralSettings.Instance != null && XRGeneralSettings.Instance.Manager != null)
        {
            yield return XRGeneralSettings.Instance.Manager.InitializeLoader();

            if (XRGeneralSettings.Instance.Manager.activeLoader != null)
            {
                Debug.Log("XR initialized successfully");
                XRGeneralSettings.Instance.Manager.StartSubsystems();
                vrEnabled = true;
            }
            else
            {
                Debug.LogWarning("XR initialization failed");

                if (!allowDesktopFallback)
                {
                    Debug.LogError("VR required but initialization failed");
                }
            }
        }
        else
        {
            Debug.LogWarning("XRGeneralSettings not configured. Please configure XR Plugin Management in Project Settings.");
        }
    }

    /// <summary>
    /// Create the WorldWind globe instance
    /// </summary>
    void CreateGlobe()
    {
        GameObject globe;

        if (globePrefab != null)
        {
            globe = Instantiate(globePrefab, globePosition, Quaternion.identity);
        }
        else
        {
            // Create globe programmatically
            globe = new GameObject("WorldWind Globe");
            globe.transform.position = globePosition;
            globe.AddComponent<WorldWindGlobe>();
            globe.AddComponent<VRGlobeInteraction>();
        }

        globe.transform.localScale = Vector3.one * globeScale;
        globeInstance = globe;

        Debug.Log($"Globe created at {globePosition}");
    }

    /// <summary>
    /// Setup VR rig components
    /// </summary>
    void SetupVRRig()
    {
        if (vrRigTransform == null)
        {
            // Try to find VR rig
            GameObject xrRig = GameObject.Find("XR Rig") ?? GameObject.Find("VR Rig");

            if (xrRig != null)
            {
                vrRigTransform = xrRig.transform;
            }
        }

        // Find controllers if not assigned
        if (leftController == null || rightController == null)
        {
            FindControllers();
        }

        // Find head/camera
        if (headTransform == null)
        {
            Camera mainCamera = Camera.main;
            if (mainCamera != null)
            {
                headTransform = mainCamera.transform;
            }
        }

        Debug.Log($"VR Rig setup - Controllers: {leftController != null && rightController != null}, Head: {headTransform != null}");
    }

    /// <summary>
    /// Find VR controllers in the scene
    /// </summary>
    void FindControllers()
    {
        // Common controller names in Unity XR
        string[] leftControllerNames = { "LeftHand Controller", "Left Controller", "LeftHandAnchor" };
        string[] rightControllerNames = { "RightHand Controller", "Right Controller", "RightHandAnchor" };

        foreach (string name in leftControllerNames)
        {
            GameObject controller = GameObject.Find(name);
            if (controller != null)
            {
                leftController = controller.transform;
                break;
            }
        }

        foreach (string name in rightControllerNames)
        {
            GameObject controller = GameObject.Find(name);
            if (controller != null)
            {
                rightController = controller.transform;
                break;
            }
        }

        if (leftController != null) Debug.Log($"Left controller found: {leftController.name}");
        if (rightController != null) Debug.Log($"Right controller found: {rightController.name}");
    }

    /// <summary>
    /// Display usage instructions
    /// </summary>
    void ShowInstructions()
    {
        Debug.Log("=== WorldWind VR Controls ===");
        Debug.Log("GRIP BUTTON (one hand): Rotate globe");
        Debug.Log("GRIP BUTTON (two hands): Scale and rotate globe");
        Debug.Log("TRIGGER: Point and select placemarks");
        Debug.Log("Point controllers at globe to see coordinates");
        Debug.Log("============================");
    }

    /// <summary>
    /// Get the globe instance
    /// </summary>
    public GameObject GetGlobe()
    {
        return globeInstance;
    }

    /// <summary>
    /// Check if VR is enabled
    /// </summary>
    public bool IsVREnabled()
    {
        return vrEnabled;
    }

    /// <summary>
    /// Reset globe position to default
    /// </summary>
    public void ResetGlobePosition()
    {
        if (globeInstance != null)
        {
            globeInstance.transform.position = globePosition;
            globeInstance.transform.rotation = Quaternion.identity;
            globeInstance.transform.localScale = Vector3.one * globeScale;
        }
    }

    void OnApplicationQuit()
    {
        // Cleanup XR
        if (XRGeneralSettings.Instance != null && XRGeneralSettings.Instance.Manager != null)
        {
            XRGeneralSettings.Instance.Manager.StopSubsystems();
            XRGeneralSettings.Instance.Manager.DeinitializeLoader();
        }
    }
}
