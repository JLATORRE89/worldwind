using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.Interaction.Toolkit;

/// <summary>
/// VR Globe Interaction
/// Handles VR controller interactions with the WorldWind globe
/// </summary>
[RequireComponent(typeof(WorldWindGlobe))]
public class VRGlobeInteraction : MonoBehaviour
{
    [Header("VR Interaction Settings")]
    [SerializeField] private bool enableGrabRotation = true;
    [SerializeField] private float rotationSensitivity = 50.0f;
    [SerializeField] private bool enableTwoHandedScale = true;
    [SerializeField] private float scaleSensitivity = 1.0f;
    [SerializeField] private float minScale = 0.5f;
    [SerializeField] private float maxScale = 5.0f;

    [Header("VR Controller References")]
    [SerializeField] private XRNode leftControllerNode = XRNode.LeftHand;
    [SerializeField] private XRNode rightControllerNode = XRNode.RightHand;

    private WorldWindGlobe globe;
    private bool isGrabbing = false;
    private bool isTwoHandedGrab = false;

    private Vector3 lastLeftControllerPosition;
    private Vector3 lastRightControllerPosition;
    private Quaternion lastRotation;
    private float initialTwoHandedDistance;
    private Vector3 initialScale;

    // Input devices
    private InputDevice leftController;
    private InputDevice rightController;

    void Start()
    {
        globe = GetComponent<WorldWindGlobe>();
        lastRotation = transform.rotation;
        initialScale = transform.localScale;

        // Initialize VR controllers
        InitializeControllers();
    }

    void Update()
    {
        // Update controller references if needed
        if (!leftController.isValid || !rightController.isValid)
        {
            InitializeControllers();
        }

        HandleVRInput();
    }

    /// <summary>
    /// Initialize VR controller input devices
    /// </summary>
    void InitializeControllers()
    {
        leftController = InputDevices.GetDeviceAtXRNode(leftControllerNode);
        rightController = InputDevices.GetDeviceAtXRNode(rightControllerNode);

        Debug.Log($"VR Controllers initialized - Left: {leftController.isValid}, Right: {rightController.isValid}");
    }

    /// <summary>
    /// Handle VR controller input
    /// </summary>
    void HandleVRInput()
    {
        bool leftGripPressed = false;
        bool rightGripPressed = false;

        // Check grip buttons
        if (leftController.isValid)
        {
            leftController.TryGetFeatureValue(CommonUsages.gripButton, out leftGripPressed);
        }

        if (rightController.isValid)
        {
            rightController.TryGetFeatureValue(CommonUsages.gripButton, out rightGripPressed);
        }

        // Two-handed grab
        if (leftGripPressed && rightGripPressed)
        {
            if (!isTwoHandedGrab)
            {
                StartTwoHandedGrab();
            }
            else
            {
                UpdateTwoHandedGrab();
            }
        }
        // One-handed grab
        else if (leftGripPressed || rightGripPressed)
        {
            if (!isGrabbing && !isTwoHandedGrab)
            {
                StartOneHandedGrab(leftGripPressed);
            }
            else if (!isTwoHandedGrab)
            {
                UpdateOneHandedGrab(leftGripPressed);
            }
        }
        else
        {
            // Release grab
            if (isGrabbing || isTwoHandedGrab)
            {
                ReleaseGrab();
            }
        }

        // Handle trigger for selection/info
        HandleTriggerInput();
    }

    /// <summary>
    /// Start one-handed grab rotation
    /// </summary>
    void StartOneHandedGrab(bool useLeftHand)
    {
        isGrabbing = true;

        Vector3 controllerPosition;
        if (useLeftHand && leftController.TryGetFeatureValue(CommonUsages.devicePosition, out controllerPosition))
        {
            lastLeftControllerPosition = controllerPosition;
        }
        else if (rightController.TryGetFeatureValue(CommonUsages.devicePosition, out controllerPosition))
        {
            lastRightControllerPosition = controllerPosition;
        }

        lastRotation = transform.rotation;

        Debug.Log("Started one-handed grab");
    }

    /// <summary>
    /// Update one-handed grab rotation
    /// </summary>
    void UpdateOneHandedGrab(bool useLeftHand)
    {
        if (!enableGrabRotation) return;

        Vector3 currentPosition;
        Vector3 lastPosition = useLeftHand ? lastLeftControllerPosition : lastRightControllerPosition;

        bool gotPosition = false;
        if (useLeftHand && leftController.TryGetFeatureValue(CommonUsages.devicePosition, out currentPosition))
        {
            gotPosition = true;
            lastLeftControllerPosition = currentPosition;
        }
        else if (rightController.TryGetFeatureValue(CommonUsages.devicePosition, out currentPosition))
        {
            gotPosition = true;
            lastRightControllerPosition = currentPosition;
        }

        if (gotPosition)
        {
            // Calculate rotation based on controller movement
            Vector3 delta = currentPosition - lastPosition;

            if (delta.magnitude > 0.001f)
            {
                // Rotate globe based on horizontal and vertical movement
                float yaw = -delta.x * rotationSensitivity;
                float pitch = delta.y * rotationSensitivity;

                transform.Rotate(Vector3.up, yaw, Space.World);
                transform.Rotate(Vector3.right, pitch, Space.World);
            }
        }
    }

    /// <summary>
    /// Start two-handed grab (for scaling and rotation)
    /// </summary>
    void StartTwoHandedGrab()
    {
        isTwoHandedGrab = true;
        isGrabbing = false;

        Vector3 leftPos, rightPos;
        if (leftController.TryGetFeatureValue(CommonUsages.devicePosition, out leftPos) &&
            rightController.TryGetFeatureValue(CommonUsages.devicePosition, out rightPos))
        {
            lastLeftControllerPosition = leftPos;
            lastRightControllerPosition = rightPos;
            initialTwoHandedDistance = Vector3.Distance(leftPos, rightPos);
        }

        Debug.Log("Started two-handed grab");
    }

    /// <summary>
    /// Update two-handed grab (scaling and rotation)
    /// </summary>
    void UpdateTwoHandedGrab()
    {
        if (!enableTwoHandedScale) return;

        Vector3 leftPos, rightPos;
        if (leftController.TryGetFeatureValue(CommonUsages.devicePosition, out leftPos) &&
            rightController.TryGetFeatureValue(CommonUsages.devicePosition, out rightPos))
        {
            // Calculate scale based on distance between controllers
            float currentDistance = Vector3.Distance(leftPos, rightPos);
            float scaleMultiplier = currentDistance / initialTwoHandedDistance;

            Vector3 newScale = initialScale * scaleMultiplier;
            newScale = Vector3.ClampMagnitude(newScale, maxScale);
            if (newScale.magnitude < minScale)
            {
                newScale = newScale.normalized * minScale;
            }

            transform.localScale = newScale;

            // Optional: Rotate based on controller orientation
            Vector3 controllerVector = (rightPos - leftPos).normalized;
            Vector3 lastControllerVector = (lastRightControllerPosition - lastLeftControllerPosition).normalized;

            if (controllerVector.magnitude > 0.1f && lastControllerVector.magnitude > 0.1f)
            {
                Quaternion deltaRotation = Quaternion.FromToRotation(lastControllerVector, controllerVector);
                transform.rotation = deltaRotation * transform.rotation;
            }

            lastLeftControllerPosition = leftPos;
            lastRightControllerPosition = rightPos;
        }
    }

    /// <summary>
    /// Release grab
    /// </summary>
    void ReleaseGrab()
    {
        isGrabbing = false;
        isTwoHandedGrab = false;
        initialScale = transform.localScale;

        Debug.Log("Released grab");
    }

    /// <summary>
    /// Handle trigger input for selection and information display
    /// </summary>
    void HandleTriggerInput()
    {
        bool leftTriggerPressed = false;
        bool rightTriggerPressed = false;

        if (leftController.isValid)
        {
            leftController.TryGetFeatureValue(CommonUsages.triggerButton, out leftTriggerPressed);
        }

        if (rightController.isValid)
        {
            rightController.TryGetFeatureValue(CommonUsages.triggerButton, out rightTriggerPressed);
        }

        if (leftTriggerPressed || rightTriggerPressed)
        {
            // TODO: Implement raycast selection for placemarks
            // This would allow users to point and click on placemarks to get info
        }
    }

    /// <summary>
    /// Handle raycast selection (called from trigger input)
    /// </summary>
    void PerformRaycastSelection(bool useLeftController)
    {
        Vector3 controllerPosition;
        Quaternion controllerRotation;

        InputDevice controller = useLeftController ? leftController : rightController;

        if (controller.TryGetFeatureValue(CommonUsages.devicePosition, out controllerPosition) &&
            controller.TryGetFeatureValue(CommonUsages.deviceRotation, out controllerRotation))
        {
            Ray ray = new Ray(controllerPosition, controllerRotation * Vector3.forward);
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit, 100.0f))
            {
                // Check if we hit a placemark or the globe
                if (hit.collider.gameObject.name.StartsWith("Placemark"))
                {
                    Debug.Log($"Selected placemark: {hit.collider.gameObject.name}");
                    // TODO: Show info panel
                }
                else if (hit.collider.gameObject == gameObject)
                {
                    // Hit the globe - convert to lat/lon
                    Vector2 latLon = globe.XYZToLatLon(hit.point);
                    Debug.Log($"Selected globe location: {latLon.x}°, {latLon.y}°");
                }
            }
        }
    }

    /// <summary>
    /// Reset globe to original position and scale
    /// </summary>
    public void ResetGlobe()
    {
        transform.rotation = Quaternion.identity;
        transform.localScale = Vector3.one;
        initialScale = Vector3.one;

        Debug.Log("Globe reset to default");
    }
}
