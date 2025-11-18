using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR;
using TMPro;

/// <summary>
/// VR Coordinate Display
/// Shows latitude/longitude coordinates and other info in VR space
/// </summary>
public class VRCoordinateDisplay : MonoBehaviour
{
    [Header("Display Settings")]
    [SerializeField] private Canvas vrCanvas;
    [SerializeField] private TextMeshProUGUI coordinateText;
    [SerializeField] private TextMeshProUGUI infoText;
    [SerializeField] private float displayDistance = 0.5f;
    [SerializeField] private Vector3 displayOffset = new Vector3(0, -0.2f, 0);

    [Header("Controller References")]
    [SerializeField] private Transform leftControllerTransform;
    [SerializeField] private Transform rightControllerTransform;
    [SerializeField] private bool attachToController = true;
    [SerializeField] private bool useLeftController = false;

    [Header("Update Settings")]
    [SerializeField] private bool showRaycastCoordinates = true;
    [SerializeField] private float updateInterval = 0.1f;

    private WorldWindGlobe globe;
    private Camera vrCamera;
    private float lastUpdateTime;

    private InputDevice leftController;
    private InputDevice rightController;

    void Start()
    {
        // Find the globe
        globe = FindObjectOfType<WorldWindGlobe>();

        // Find VR camera (usually tagged as MainCamera)
        vrCamera = Camera.main;

        // Initialize controllers
        leftController = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
        rightController = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);

        // Create UI if not assigned
        if (vrCanvas == null)
        {
            CreateVRUI();
        }

        Debug.Log("VR Coordinate Display initialized");
    }

    void Update()
    {
        // Update controller references if needed
        if (!leftController.isValid || !rightController.isValid)
        {
            leftController = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
            rightController = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
        }

        // Update position
        UpdateDisplayPosition();

        // Update coordinates
        if (Time.time - lastUpdateTime > updateInterval)
        {
            UpdateCoordinateDisplay();
            lastUpdateTime = Time.time;
        }
    }

    /// <summary>
    /// Create VR UI canvas and text elements
    /// </summary>
    void CreateVRUI()
    {
        // Create canvas
        GameObject canvasObj = new GameObject("VR Coordinate Display");
        canvasObj.transform.SetParent(transform);

        vrCanvas = canvasObj.AddComponent<Canvas>();
        vrCanvas.renderMode = RenderMode.WorldSpace;

        // Set canvas size
        RectTransform canvasRect = vrCanvas.GetComponent<RectTransform>();
        canvasRect.sizeDelta = new Vector2(400, 200);
        canvasRect.localScale = new Vector3(0.001f, 0.001f, 0.001f);

        // Add CanvasScaler
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.dynamicPixelsPerUnit = 10;

        // Add GraphicRaycaster for UI interaction
        canvasObj.AddComponent<GraphicRaycaster>();

        // Create background panel
        GameObject panelObj = new GameObject("Panel");
        panelObj.transform.SetParent(canvasObj.transform, false);

        Image panel = panelObj.AddComponent<Image>();
        panel.color = new Color(0, 0, 0, 0.7f);

        RectTransform panelRect = panelObj.GetComponent<RectTransform>();
        panelRect.anchorMin = Vector2.zero;
        panelRect.anchorMax = Vector2.one;
        panelRect.sizeDelta = Vector2.zero;

        // Create coordinate text
        GameObject coordTextObj = new GameObject("Coordinate Text");
        coordTextObj.transform.SetParent(panelObj.transform, false);

        coordinateText = coordTextObj.AddComponent<TextMeshProUGUI>();
        coordinateText.text = "Coordinates: --";
        coordinateText.fontSize = 24;
        coordinateText.color = Color.white;
        coordinateText.alignment = TextAlignmentOptions.Center;

        RectTransform coordRect = coordTextObj.GetComponent<RectTransform>();
        coordRect.anchorMin = new Vector2(0, 0.5f);
        coordRect.anchorMax = new Vector2(1, 1);
        coordRect.sizeDelta = Vector2.zero;

        // Create info text
        GameObject infoTextObj = new GameObject("Info Text");
        infoTextObj.transform.SetParent(panelObj.transform, false);

        infoText = infoTextObj.AddComponent<TextMeshProUGUI>();
        infoText.text = "WorldWind VR\nPoint at globe for coordinates";
        infoText.fontSize = 18;
        infoText.color = new Color(0.8f, 0.8f, 0.8f);
        infoText.alignment = TextAlignmentOptions.Center;

        RectTransform infoRect = infoTextObj.GetComponent<RectTransform>();
        infoRect.anchorMin = new Vector2(0, 0);
        infoRect.anchorMax = new Vector2(1, 0.5f);
        infoRect.sizeDelta = Vector2.zero;

        Debug.Log("VR UI created");
    }

    /// <summary>
    /// Update the display position (attach to controller or camera)
    /// </summary>
    void UpdateDisplayPosition()
    {
        if (attachToController)
        {
            Transform controllerTransform = useLeftController ? leftControllerTransform : rightControllerTransform;

            if (controllerTransform != null)
            {
                // Attach to controller
                vrCanvas.transform.position = controllerTransform.position + controllerTransform.TransformDirection(displayOffset);
                vrCanvas.transform.rotation = controllerTransform.rotation;
            }
            else
            {
                // Fallback to camera if controller not found
                PositionRelativeToCamera();
            }
        }
        else
        {
            // Position relative to camera
            PositionRelativeToCamera();
        }
    }

    /// <summary>
    /// Position the display relative to the VR camera
    /// </summary>
    void PositionRelativeToCamera()
    {
        if (vrCamera != null)
        {
            Vector3 position = vrCamera.transform.position + vrCamera.transform.forward * displayDistance;
            position += displayOffset;

            vrCanvas.transform.position = position;
            vrCanvas.transform.rotation = Quaternion.LookRotation(vrCanvas.transform.position - vrCamera.transform.position);
        }
    }

    /// <summary>
    /// Update coordinate display based on controller raycast
    /// </summary>
    void UpdateCoordinateDisplay()
    {
        if (!showRaycastCoordinates || globe == null) return;

        // Get the active controller
        Transform activeController = useLeftController ? leftControllerTransform : rightControllerTransform;

        if (activeController != null)
        {
            // Perform raycast from controller
            Ray ray = new Ray(activeController.position, activeController.forward);
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit, 100.0f))
            {
                if (hit.collider.gameObject.GetComponent<WorldWindGlobe>() != null)
                {
                    // Convert hit point to lat/lon
                    Vector2 latLon = globe.XYZToLatLon(hit.point);

                    // Update display
                    coordinateText.text = $"Lat: {latLon.x:F2}°\nLon: {latLon.y:F2}°";

                    // Calculate distance from camera
                    float distance = Vector3.Distance(vrCamera.transform.position, hit.point);
                    infoText.text = $"Distance: {distance:F2}m\nAltitude: 0m";
                }
            }
            else
            {
                coordinateText.text = "Coordinates: --";
                infoText.text = "Point at globe";
            }
        }
    }

    /// <summary>
    /// Show custom message on the display
    /// </summary>
    public void ShowMessage(string message, float duration = 3.0f)
    {
        if (infoText != null)
        {
            infoText.text = message;
            Invoke(nameof(ClearMessage), duration);
        }
    }

    /// <summary>
    /// Clear the info message
    /// </summary>
    void ClearMessage()
    {
        if (infoText != null)
        {
            infoText.text = "Point at globe for coordinates";
        }
    }

    /// <summary>
    /// Show placemark information
    /// </summary>
    public void ShowPlacemarkInfo(string name, float latitude, float longitude)
    {
        if (coordinateText != null)
        {
            coordinateText.text = $"{name}\nLat: {latitude:F2}°\nLon: {longitude:F2}°";
        }
    }

    /// <summary>
    /// Toggle display visibility
    /// </summary>
    public void ToggleDisplay(bool visible)
    {
        if (vrCanvas != null)
        {
            vrCanvas.gameObject.SetActive(visible);
        }
    }
}
