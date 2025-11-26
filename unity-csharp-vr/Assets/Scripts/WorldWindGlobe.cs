using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// WorldWind Globe - VR Ready
/// Generates and manages a 3D globe with Earth visualization for VR
/// </summary>
public class WorldWindGlobe : MonoBehaviour
{
    [Header("Globe Settings")]
    [SerializeField] private float globeRadius = 1.0f;
    [SerializeField] private int latitudeSegments = 60;
    [SerializeField] private int longitudeSegments = 120;

    [Header("Materials")]
    [SerializeField] private Material earthMaterial;
    [SerializeField] private Texture2D earthTexture;

    [Header("VR Interaction")]
    [SerializeField] private bool enableVRGrab = true;
    [SerializeField] private float rotationSpeed = 30.0f;

    private MeshFilter meshFilter;
    private MeshRenderer meshRenderer;
    private MeshCollider meshCollider;

    // Store placemarks and polygons
    private List<GameObject> placemarks = new List<GameObject>();
    private List<GameObject> polygons = new List<GameObject>();

    void Start()
    {
        InitializeGlobe();
        CreateSamplePlacemarks();
        CreateSamplePolygon();
    }

    /// <summary>
    /// Initialize the globe mesh and components
    /// </summary>
    void InitializeGlobe()
    {
        // Add required components
        meshFilter = gameObject.AddComponent<MeshFilter>();
        meshRenderer = gameObject.AddComponent<MeshRenderer>();
        meshCollider = gameObject.AddComponent<MeshCollider>();

        // Generate globe mesh
        Mesh globeMesh = GenerateSphereMesh(globeRadius, latitudeSegments, longitudeSegments);
        meshFilter.mesh = globeMesh;
        meshCollider.sharedMesh = globeMesh;

        // Setup material
        if (earthMaterial == null)
        {
            earthMaterial = new Material(Shader.Find("Standard"));
            earthMaterial.color = new Color(0.2f, 0.5f, 0.8f); // Ocean blue
        }

        if (earthTexture != null)
        {
            earthMaterial.mainTexture = earthTexture;
        }

        meshRenderer.material = earthMaterial;

        Debug.Log($"WorldWind Globe initialized - Radius: {globeRadius}, Segments: {latitudeSegments}x{longitudeSegments}");
    }

    /// <summary>
    /// Generate a UV sphere mesh for the globe
    /// </summary>
    Mesh GenerateSphereMesh(float radius, int latSegments, int lonSegments)
    {
        Mesh mesh = new Mesh();
        mesh.name = "WorldWind Globe";

        List<Vector3> vertices = new List<Vector3>();
        List<Vector3> normals = new List<Vector3>();
        List<Vector2> uvs = new List<Vector2>();
        List<int> triangles = new List<int>();

        // Generate vertices
        for (int lat = 0; lat <= latSegments; lat++)
        {
            float theta = lat * Mathf.PI / latSegments;
            float sinTheta = Mathf.Sin(theta);
            float cosTheta = Mathf.Cos(theta);

            for (int lon = 0; lon <= lonSegments; lon++)
            {
                float phi = lon * 2 * Mathf.PI / lonSegments;
                float sinPhi = Mathf.Sin(phi);
                float cosPhi = Mathf.Cos(phi);

                // Vertex position
                Vector3 vertex = new Vector3(
                    radius * sinTheta * cosPhi,
                    radius * cosTheta,
                    radius * sinTheta * sinPhi
                );

                vertices.Add(vertex);

                // Normal (points outward from sphere center)
                normals.Add(vertex.normalized);

                // UV coordinates
                Vector2 uv = new Vector2(
                    (float)lon / lonSegments,
                    1.0f - (float)lat / latSegments
                );
                uvs.Add(uv);
            }
        }

        // Generate triangles
        for (int lat = 0; lat < latSegments; lat++)
        {
            for (int lon = 0; lon < lonSegments; lon++)
            {
                int current = lat * (lonSegments + 1) + lon;
                int next = current + lonSegments + 1;

                // Two triangles per quad
                triangles.Add(current);
                triangles.Add(next);
                triangles.Add(current + 1);

                triangles.Add(current + 1);
                triangles.Add(next);
                triangles.Add(next + 1);
            }
        }

        mesh.vertices = vertices.ToArray();
        mesh.normals = normals.ToArray();
        mesh.uv = uvs.ToArray();
        mesh.triangles = triangles.ToArray();

        mesh.RecalculateBounds();

        return mesh;
    }

    /// <summary>
    /// Convert latitude/longitude to 3D position on sphere
    /// </summary>
    public Vector3 LatLonToXYZ(float latitude, float longitude, float altitude = 0)
    {
        float lat = latitude * Mathf.Deg2Rad;
        float lon = longitude * Mathf.Deg2Rad;
        float r = globeRadius + altitude;

        float x = r * Mathf.Cos(lat) * Mathf.Cos(lon);
        float y = r * Mathf.Sin(lat);
        float z = r * Mathf.Cos(lat) * Mathf.Sin(lon);

        return new Vector3(x, y, z);
    }

    /// <summary>
    /// Convert 3D position to latitude/longitude
    /// </summary>
    public Vector2 XYZToLatLon(Vector3 position)
    {
        float r = position.magnitude;
        float latitude = Mathf.Asin(position.y / r) * Mathf.Rad2Deg;
        float longitude = Mathf.Atan2(position.z, position.x) * Mathf.Rad2Deg;

        return new Vector2(latitude, longitude);
    }

    /// <summary>
    /// Create a placemark at the specified lat/lon
    /// </summary>
    public GameObject CreatePlacemark(float latitude, float longitude, Color color, string label = "")
    {
        Vector3 position = LatLonToXYZ(latitude, longitude, 0.05f);

        GameObject placemark = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        placemark.transform.SetParent(transform);
        placemark.transform.localPosition = position;
        placemark.transform.localScale = Vector3.one * 0.03f;

        // Set color
        Renderer renderer = placemark.GetComponent<Renderer>();
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = color;
        mat.SetFloat("_Metallic", 0.5f);
        mat.SetFloat("_Glossiness", 0.8f);
        renderer.material = mat;

        placemark.name = $"Placemark_{latitude}_{longitude}";

        // Add label if specified
        if (!string.IsNullOrEmpty(label))
        {
            // TODO: Add 3D text label for VR
        }

        placemarks.Add(placemark);

        Debug.Log($"Created placemark at {latitude}°, {longitude}°");

        return placemark;
    }

    /// <summary>
    /// Create sample placemarks (matching JavaScript version)
    /// </summary>
    void CreateSamplePlacemarks()
    {
        // Sample: 55°N, -106°W (same as JavaScript version)
        CreatePlacemark(55.0f, -106.0f, Color.red, "Sample Location");

        // Add a few more for VR visualization
        CreatePlacemark(40.7128f, -74.0060f, Color.yellow, "New York");
        CreatePlacemark(51.5074f, -0.1278f, Color.green, "London");
        CreatePlacemark(-33.8688f, 151.2093f, Color.magenta, "Sydney");
    }

    /// <summary>
    /// Create a 3D extruded polygon
    /// </summary>
    public GameObject CreateExtrudedPolygon(List<Vector2> latLonCoordinates, float extrusionHeight, Color color)
    {
        GameObject polygon = new GameObject("Extruded Polygon");
        polygon.transform.SetParent(transform);

        // Create base vertices
        List<Vector3> baseVertices = new List<Vector3>();
        List<Vector3> topVertices = new List<Vector3>();

        foreach (Vector2 latLon in latLonCoordinates)
        {
            Vector3 basePos = LatLonToXYZ(latLon.x, latLon.y, 0);
            Vector3 topPos = LatLonToXYZ(latLon.x, latLon.y, extrusionHeight);

            baseVertices.Add(basePos);
            topVertices.Add(topPos);
        }

        // Draw edges
        for (int i = 0; i < baseVertices.Count; i++)
        {
            int nextIndex = (i + 1) % baseVertices.Count;

            // Vertical edge
            GameObject verticalEdge = CreateLine(baseVertices[i], topVertices[i], color, 0.005f);
            verticalEdge.transform.SetParent(polygon.transform);

            // Top edge
            GameObject topEdge = CreateLine(topVertices[i], topVertices[nextIndex], color, 0.007f);
            topEdge.transform.SetParent(polygon.transform);

            // Base edge
            GameObject baseEdge = CreateLine(baseVertices[i], baseVertices[nextIndex], color * 0.7f, 0.005f);
            baseEdge.transform.SetParent(polygon.transform);
        }

        polygons.Add(polygon);

        return polygon;
    }

    /// <summary>
    /// Create a line between two points (helper for polygon edges)
    /// </summary>
    GameObject CreateLine(Vector3 start, Vector3 end, Color color, float width)
    {
        GameObject lineObj = new GameObject("Line");
        LineRenderer line = lineObj.AddComponent<LineRenderer>();

        line.positionCount = 2;
        line.SetPosition(0, start);
        line.SetPosition(1, end);

        line.startWidth = width;
        line.endWidth = width;

        Material lineMat = new Material(Shader.Find("Sprites/Default"));
        lineMat.color = color;
        line.material = lineMat;

        return lineObj;
    }

    /// <summary>
    /// Create sample polygon (matching JavaScript version)
    /// </summary>
    void CreateSamplePolygon()
    {
        List<Vector2> coordinates = new List<Vector2>
        {
            new Vector2(45.0f, -100.0f),  // Northwest
            new Vector2(45.0f, -95.0f),   // Northeast
            new Vector2(40.0f, -95.0f),   // Southeast
            new Vector2(40.0f, -100.0f)   // Southwest
        };

        CreateExtrudedPolygon(coordinates, 0.2f, new Color(0, 1, 1, 0.8f)); // Cyan
    }

    /// <summary>
    /// Get the globe radius (useful for other scripts)
    /// </summary>
    public float GetRadius()
    {
        return globeRadius;
    }
}
