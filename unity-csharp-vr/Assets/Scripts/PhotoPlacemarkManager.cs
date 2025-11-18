using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.IO;

/// <summary>
/// Photo Placemark Manager
/// Manages travel photos as 3D placemarks on the globe
/// </summary>
[RequireComponent(typeof(WorldWindGlobe))]
public class PhotoPlacemarkManager : MonoBehaviour
{
    [System.Serializable]
    public class TravelPhoto
    {
        public string photoPath;
        public float latitude;
        public float longitude;
        public string title;
        public string description;
        public string date;
        public Texture2D texture;
        public GameObject placemark;
    }

    [Header("Photo Settings")]
    [SerializeField] private float photoPlacemarkSize = 0.1f;
    [SerializeField] private float photoDisplaySize = 0.3f;
    [SerializeField] private Color photoFrameColor = Color.white;
    [SerializeField] private float altitudeOffset = 0.05f;

    [Header("UI Settings")]
    [SerializeField] private bool showPhotoOnClick = true;
    [SerializeField] private Canvas photoDisplayCanvas;

    private WorldWindGlobe globe;
    private List<TravelPhoto> travelPhotos = new List<TravelPhoto>();
    private TravelPhoto selectedPhoto;

    void Start()
    {
        globe = GetComponent<WorldWindGlobe>();

        if (photoDisplayCanvas == null)
        {
            CreatePhotoDisplayUI();
        }

        Debug.Log("Photo Placemark Manager initialized");
    }

    /// <summary>
    /// Add a travel photo placemark to the globe
    /// </summary>
    public TravelPhoto AddPhotoPlacemark(string photoPath, float latitude, float longitude,
                                         string title = "", string description = "", string date = "")
    {
        // Load the image
        Texture2D texture = LoadPhoto(photoPath);
        if (texture == null)
        {
            Debug.LogError($"Failed to load photo: {photoPath}");
            return null;
        }

        // Create travel photo object
        TravelPhoto photo = new TravelPhoto
        {
            photoPath = photoPath,
            latitude = latitude,
            longitude = longitude,
            title = title,
            description = description,
            date = date,
            texture = texture
        };

        // Create 3D placemark
        Vector3 position = globe.LatLonToXYZ(latitude, longitude, altitudeOffset);
        GameObject placemark = CreatePhotoPlacemark3D(position, texture, title);

        photo.placemark = placemark;
        travelPhotos.Add(photo);

        Debug.Log($"Added photo placemark: {title} at {latitude}°, {longitude}°");

        return photo;
    }

    /// <summary>
    /// Load a photo from file system
    /// </summary>
    Texture2D LoadPhoto(string path)
    {
        if (!File.Exists(path))
        {
            Debug.LogWarning($"Photo file not found: {path}");
            return null;
        }

        byte[] imageData = File.ReadAllBytes(path);
        Texture2D texture = new Texture2D(2, 2);

        if (texture.LoadImage(imageData))
        {
            return texture;
        }

        Debug.LogError($"Failed to load image data: {path}");
        return null;
    }

    /// <summary>
    /// Create a 3D photo placemark
    /// </summary>
    GameObject CreatePhotoPlacemark3D(Vector3 position, Texture2D texture, string title)
    {
        // Create container
        GameObject container = new GameObject($"Photo: {title}");
        container.transform.SetParent(transform);
        container.transform.localPosition = position;

        // Create frame (cube)
        GameObject frame = GameObject.CreatePrimitive(PrimitiveType.Cube);
        frame.name = "Frame";
        frame.transform.SetParent(container.transform);
        frame.transform.localPosition = Vector3.zero;
        frame.transform.localScale = new Vector3(photoPlacemarkSize, photoPlacemarkSize, 0.01f);

        // Set frame material
        Renderer frameRenderer = frame.GetComponent<Renderer>();
        Material frameMaterial = new Material(Shader.Find("Standard"));
        frameMaterial.color = photoFrameColor;
        frameRenderer.material = frameMaterial;

        // Create photo plane
        GameObject photoPlane = GameObject.CreatePrimitive(PrimitiveType.Quad);
        photoPlane.name = "Photo";
        photoPlane.transform.SetParent(container.transform);
        photoPlane.transform.localPosition = new Vector3(0, 0, -0.006f);
        photoPlane.transform.localScale = new Vector3(photoPlacemarkSize * 0.9f, photoPlacemarkSize * 0.9f, 1);

        // Apply photo texture
        Renderer photoRenderer = photoPlane.GetComponent<Renderer>();
        Material photoMaterial = new Material(Shader.Find("Standard"));
        photoMaterial.mainTexture = texture;
        photoRenderer.material = photoMaterial;

        // Make photo face outward from globe center
        container.transform.rotation = Quaternion.LookRotation(position.normalized);

        // Add click detection
        BoxCollider collider = container.AddComponent<BoxCollider>();
        collider.size = new Vector3(photoPlacemarkSize, photoPlacemarkSize, 0.02f);

        // Add marker sphere for visibility
        GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        marker.name = "Marker";
        marker.transform.SetParent(container.transform);
        marker.transform.localPosition = new Vector3(0, photoPlacemarkSize * 0.6f, 0);
        marker.transform.localScale = Vector3.one * 0.03f;

        Renderer markerRenderer = marker.GetComponent<Renderer>();
        Material markerMaterial = new Material(Shader.Find("Standard"));
        markerMaterial.color = Color.cyan;
        markerMaterial.SetFloat("_Metallic", 0.5f);
        markerMaterial.SetFloat("_Glossiness", 0.8f);
        markerRenderer.material = markerMaterial;

        return container;
    }

    /// <summary>
    /// Create UI for displaying selected photo
    /// </summary>
    void CreatePhotoDisplayUI()
    {
        // Create canvas
        GameObject canvasObj = new GameObject("Photo Display Canvas");
        canvasObj.transform.SetParent(transform);

        photoDisplayCanvas = canvasObj.AddComponent<Canvas>();
        photoDisplayCanvas.renderMode = RenderMode.WorldSpace;

        RectTransform canvasRect = photoDisplayCanvas.GetComponent<RectTransform>();
        canvasRect.sizeDelta = new Vector2(800, 600);
        canvasRect.localScale = new Vector3(0.001f, 0.001f, 0.001f);

        canvasObj.AddComponent<GraphicRaycaster>();
        canvasObj.SetActive(false);

        Debug.Log("Photo display UI created");
    }

    /// <summary>
    /// Load travel photos from JSON file
    /// </summary>
    public void LoadFromJSON(string jsonPath)
    {
        if (!File.Exists(jsonPath))
        {
            Debug.LogError($"JSON file not found: {jsonPath}");
            return;
        }

        string json = File.ReadAllText(jsonPath);
        TravelPhotosData data = JsonUtility.FromJson<TravelPhotosData>(json);

        foreach (var photoData in data.travels)
        {
            AddPhotoPlacemark(
                photoData.photo,
                photoData.latitude,
                photoData.longitude,
                photoData.title,
                photoData.description,
                photoData.date
            );
        }

        Debug.Log($"Loaded {data.travels.Length} travel photos from JSON");
    }

    /// <summary>
    /// Get all travel photos
    /// </summary>
    public List<TravelPhoto> GetAllPhotos()
    {
        return new List<TravelPhoto>(travelPhotos);
    }

    /// <summary>
    /// Remove a photo placemark
    /// </summary>
    public void RemovePhoto(TravelPhoto photo)
    {
        if (travelPhotos.Contains(photo))
        {
            if (photo.placemark != null)
            {
                Destroy(photo.placemark);
            }
            travelPhotos.Remove(photo);
        }
    }

    /// <summary>
    /// Clear all photo placemarks
    /// </summary>
    public void ClearAllPhotos()
    {
        foreach (var photo in travelPhotos)
        {
            if (photo.placemark != null)
            {
                Destroy(photo.placemark);
            }
        }
        travelPhotos.Clear();
    }

    [System.Serializable]
    public class PhotoData
    {
        public string photo;
        public float latitude;
        public float longitude;
        public string title;
        public string description;
        public string date;
    }

    [System.Serializable]
    public class TravelPhotosData
    {
        public PhotoData[] travels;
    }
}
