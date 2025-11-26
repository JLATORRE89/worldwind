using UnityEngine;
using System.Collections.Generic;
using System.IO;

/// <summary>
/// Friend Placemark Manager
/// Manages friend locations as 3D placemarks on the globe
/// </summary>
[RequireComponent(typeof(WorldWindGlobe))]
public class FriendPlacemarkManager : MonoBehaviour
{
    [System.Serializable]
    public class Friend
    {
        public string name;
        public string city;
        public float latitude;
        public float longitude;
        public string photoPath;
        public string color;
        public string group;
        public Texture2D photo;
        public GameObject placemark;
    }

    [Header("Friend Settings")]
    [SerializeField] private float friendMarkerSize = 0.05f;
    [SerializeField] private float altitudeOffset = 0.05f;
    [SerializeField] private bool showLabels = true;

    [Header("Group Colors")]
    [SerializeField] private Color familyColor = Color.red;
    [SerializeField] private Color friendsColor = Color.yellow;
    [SerializeField] private Color workColor = Color.blue;
    [SerializeField] private Color collegeColor = Color.green;

    private WorldWindGlobe globe;
    private List<Friend> friends = new List<Friend>();

    void Start()
    {
        globe = GetComponent<WorldWindGlobe>();
        Debug.Log("Friend Placemark Manager initialized");
    }

    /// <summary>
    /// Add a friend placemark to the globe
    /// </summary>
    public Friend AddFriend(string name, string city, float latitude, float longitude,
                           string photoPath = "", string colorName = "yellow", string group = "friends")
    {
        // Create friend object
        Friend friend = new Friend
        {
            name = name,
            city = city,
            latitude = latitude,
            longitude = longitude,
            photoPath = photoPath,
            color = colorName,
            group = group
        };

        // Load photo if provided
        if (!string.IsNullOrEmpty(photoPath) && File.Exists(photoPath))
        {
            friend.photo = LoadPhoto(photoPath);
        }

        // Create 3D placemark
        Vector3 position = globe.LatLonToXYZ(latitude, longitude, altitudeOffset);
        Color markerColor = GetGroupColor(colorName, group);
        GameObject placemark = CreateFriendPlacemark(position, name, markerColor, friend.photo);

        friend.placemark = placemark;
        friends.Add(friend);

        Debug.Log($"Added friend: {name} in {city} ({latitude}°, {longitude}°)");

        return friend;
    }

    /// <summary>
    /// Load a photo from file
    /// </summary>
    Texture2D LoadPhoto(string path)
    {
        if (!File.Exists(path))
        {
            return null;
        }

        byte[] imageData = File.ReadAllBytes(path);
        Texture2D texture = new Texture2D(2, 2);

        if (texture.LoadImage(imageData))
        {
            return texture;
        }

        return null;
    }

    /// <summary>
    /// Create a friend placemark in 3D
    /// </summary>
    GameObject CreateFriendPlacemark(Vector3 position, string name, Color color, Texture2D photo)
    {
        // Create container
        GameObject container = new GameObject($"Friend: {name}");
        container.transform.SetParent(transform);
        container.transform.localPosition = position;

        // Create marker sphere
        GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        marker.name = "Marker";
        marker.transform.SetParent(container.transform);
        marker.transform.localPosition = Vector3.zero;
        marker.transform.localScale = Vector3.one * friendMarkerSize;

        // Set marker material
        Renderer markerRenderer = marker.GetComponent<Renderer>();
        Material markerMaterial = new Material(Shader.Find("Standard"));
        markerMaterial.color = color;
        markerMaterial.SetFloat("_Metallic", 0.3f);
        markerMaterial.SetFloat("_Glossiness", 0.7f);
        markerRenderer.material = markerMaterial;

        // If photo provided, create photo display above marker
        if (photo != null)
        {
            GameObject photoPlane = GameObject.CreatePrimitive(PrimitiveType.Quad);
            photoPlane.name = "Photo";
            photoPlane.transform.SetParent(container.transform);
            photoPlane.transform.localPosition = new Vector3(0, friendMarkerSize * 1.5f, 0);
            photoPlane.transform.localScale = Vector3.one * friendMarkerSize * 1.5f;

            // Apply photo texture
            Renderer photoRenderer = photoPlane.GetComponent<Renderer>();
            Material photoMaterial = new Material(Shader.Find("Standard"));
            photoMaterial.mainTexture = photo;
            photoRenderer.material = photoMaterial;

            // Make photo face outward
            photoPlane.transform.rotation = Quaternion.LookRotation(position.normalized);
        }

        // Create pin/stick connecting marker to globe surface
        GameObject pin = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        pin.name = "Pin";
        pin.transform.SetParent(container.transform);
        pin.transform.localPosition = new Vector3(0, -friendMarkerSize * 0.5f, 0);
        pin.transform.localScale = new Vector3(0.005f, friendMarkerSize * 0.5f, 0.005f);

        Renderer pinRenderer = pin.GetComponent<Renderer>();
        Material pinMaterial = new Material(Shader.Find("Standard"));
        pinMaterial.color = color * 0.7f;
        pinRenderer.material = pinMaterial;

        // Add label if enabled
        if (showLabels)
        {
            AddLabel(container, name, position, color);
        }

        // Make container face outward from globe
        container.transform.rotation = Quaternion.LookRotation(position.normalized);

        return container;
    }

    /// <summary>
    /// Add a text label to the friend marker
    /// </summary>
    void AddLabel(GameObject parent, string text, Vector3 position, Color color)
    {
        // Note: For proper 3D text, use TextMeshPro
        // This creates a simple placeholder
        GameObject labelObj = new GameObject("Label");
        labelObj.transform.SetParent(parent.transform);
        labelObj.transform.localPosition = new Vector3(0, friendMarkerSize * 2.5f, 0);
        labelObj.transform.localScale = Vector3.one * 0.01f;

        // In a real implementation, add TextMeshPro component here
        // For now, just mark it with a name
        labelObj.name = $"Label: {text}";
    }

    /// <summary>
    /// Get group color based on name or group
    /// </summary>
    Color GetGroupColor(string colorName, string group)
    {
        // Try to parse color name first
        if (!string.IsNullOrEmpty(colorName))
        {
            switch (colorName.ToLower())
            {
                case "red": return Color.red;
                case "yellow": return Color.yellow;
                case "blue": return Color.blue;
                case "green": return Color.green;
                case "cyan": return Color.cyan;
                case "magenta": return Color.magenta;
                case "white": return Color.white;
                case "orange": return new Color(1f, 0.5f, 0f);
                case "purple": return new Color(0.5f, 0f, 1f);
            }
        }

        // Fall back to group colors
        switch (group.ToLower())
        {
            case "family": return familyColor;
            case "friends": return friendsColor;
            case "work": return workColor;
            case "college": return collegeColor;
            default: return Color.yellow;
        }
    }

    /// <summary>
    /// Load friends from JSON file
    /// </summary>
    public void LoadFromJSON(string jsonPath)
    {
        if (!File.Exists(jsonPath))
        {
            Debug.LogError($"JSON file not found: {jsonPath}");
            return;
        }

        string json = File.ReadAllText(jsonPath);
        FriendsData data = JsonUtility.FromJson<FriendsData>(json);

        foreach (var friendData in data.friends)
        {
            AddFriend(
                friendData.name,
                friendData.city,
                friendData.latitude,
                friendData.longitude,
                friendData.photo,
                friendData.color,
                friendData.group
            );
        }

        Debug.Log($"Loaded {data.friends.Length} friends from JSON");
    }

    /// <summary>
    /// Get all friends
    /// </summary>
    public List<Friend> GetAllFriends()
    {
        return new List<Friend>(friends);
    }

    /// <summary>
    /// Remove a friend placemark
    /// </summary>
    public void RemoveFriend(Friend friend)
    {
        if (friends.Contains(friend))
        {
            if (friend.placemark != null)
            {
                Destroy(friend.placemark);
            }
            friends.Remove(friend);
        }
    }

    /// <summary>
    /// Clear all friend placemarks
    /// </summary>
    public void ClearAllFriends()
    {
        foreach (var friend in friends)
        {
            if (friend.placemark != null)
            {
                Destroy(friend.placemark);
            }
        }
        friends.Clear();
    }

    /// <summary>
    /// Show/hide friends by group
    /// </summary>
    public void ShowGroup(string group, bool show)
    {
        foreach (var friend in friends)
        {
            if (friend.group.ToLower() == group.ToLower())
            {
                if (friend.placemark != null)
                {
                    friend.placemark.SetActive(show);
                }
            }
        }
    }

    [System.Serializable]
    public class FriendData
    {
        public string name;
        public string city;
        public float latitude;
        public float longitude;
        public string photo;
        public string color;
        public string group;
    }

    [System.Serializable]
    public class FriendsData
    {
        public FriendData[] friends;
    }
}
