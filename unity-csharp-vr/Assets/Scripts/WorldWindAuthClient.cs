using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

/// <summary>
/// WorldWind Authentication Client for Unity
/// Supports email/password login and OAuth (Google, Discord, Microsoft)
/// </summary>
public class WorldWindAuthClient : MonoBehaviour
{
    [Header("Server Configuration")]
    [SerializeField] private string serverUrl = "http://localhost:5000";

    [Header("Authentication State")]
    public bool isAuthenticated = false;
    public string username;
    public string email;
    public int userId;

    private string authToken;

    // Events
    public event Action<UserData> OnLoginSuccess;
    public event Action<string> OnLoginFailed;
    public event Action OnLogout;

    void Start()
    {
        // Try to load saved token
        LoadToken();
    }

    // ========================================================================
    // REGISTRATION & LOGIN
    // ========================================================================

    /// <summary>
    /// Register new user with email/password
    /// </summary>
    public void Register(string email, string username, string password, Action<bool, string> callback)
    {
        StartCoroutine(RegisterCoroutine(email, username, password, callback));
    }

    private IEnumerator RegisterCoroutine(string email, string username, string password, Action<bool, string> callback)
    {
        string url = $"{serverUrl}/api/register";

        RegisterRequest requestData = new RegisterRequest
        {
            email = email,
            username = username,
            password = password
        };

        string jsonData = JsonUtility.ToJson(requestData);

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                AuthResponse response = JsonUtility.FromJson<AuthResponse>(request.downloadHandler.text);

                authToken = response.token;
                SetUserData(response.user);
                SaveToken();

                callback?.Invoke(true, "Registration successful");
                OnLoginSuccess?.Invoke(response.user);

                Debug.Log($"✓ Registered as {username}");
            }
            else
            {
                string error = GetErrorMessage(request);
                callback?.Invoke(false, error);
                OnLoginFailed?.Invoke(error);

                Debug.LogError($"✗ Registration failed: {error}");
            }
        }
    }

    /// <summary>
    /// Login with email/password
    /// </summary>
    public void Login(string email, string password, Action<bool, string> callback)
    {
        StartCoroutine(LoginCoroutine(email, password, callback));
    }

    private IEnumerator LoginCoroutine(string email, string password, Action<bool, string> callback)
    {
        string url = $"{serverUrl}/api/login";

        LoginRequest requestData = new LoginRequest
        {
            email = email,
            password = password
        };

        string jsonData = JsonUtility.ToJson(requestData);

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                AuthResponse response = JsonUtility.FromJson<AuthResponse>(request.downloadHandler.text);

                authToken = response.token;
                SetUserData(response.user);
                SaveToken();

                callback?.Invoke(true, "Login successful");
                OnLoginSuccess?.Invoke(response.user);

                Debug.Log($"✓ Logged in as {username}");
            }
            else
            {
                string error = GetErrorMessage(request);
                callback?.Invoke(false, error);
                OnLoginFailed?.Invoke(error);

                Debug.LogError($"✗ Login failed: {error}");
            }
        }
    }

    /// <summary>
    /// Login with Google OAuth
    /// Opens browser for authentication
    /// </summary>
    public void LoginGoogle()
    {
        string authUrl = $"{serverUrl}/auth/google";
        Application.OpenURL(authUrl);
        Debug.Log("Opening browser for Google login");
    }

    /// <summary>
    /// Login with Discord OAuth
    /// Opens browser for authentication
    /// </summary>
    public void LoginDiscord()
    {
        string authUrl = $"{serverUrl}/auth/discord";
        Application.OpenURL(authUrl);
        Debug.Log("Opening browser for Discord login");
    }

    /// <summary>
    /// Login with Microsoft OAuth
    /// Opens browser for authentication
    /// </summary>
    public void LoginMicrosoft()
    {
        string authUrl = $"{serverUrl}/auth/microsoft";
        Application.OpenURL(authUrl);
        Debug.Log("Opening browser for Microsoft login");
    }

    /// <summary>
    /// Manually set token (from OAuth callback)
    /// </summary>
    public void SetToken(string token)
    {
        authToken = token;
        SaveToken();
        GetProfile(null);  // Fetch user data
    }

    /// <summary>
    /// Logout
    /// </summary>
    public void Logout()
    {
        authToken = null;
        isAuthenticated = false;
        username = null;
        email = null;
        userId = 0;

        ClearToken();
        OnLogout?.Invoke();

        Debug.Log("✓ Logged out");
    }

    // ========================================================================
    // PROFILE
    // ========================================================================

    /// <summary>
    /// Get user profile
    /// </summary>
    public void GetProfile(Action<UserProfile> callback)
    {
        StartCoroutine(GetProfileCoroutine(callback));
    }

    private IEnumerator GetProfileCoroutine(Action<UserProfile> callback)
    {
        string url = $"{serverUrl}/api/profile";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                UserProfile profile = JsonUtility.FromJson<UserProfile>(request.downloadHandler.text);

                SetUserData(new UserData
                {
                    id = profile.id,
                    username = profile.username,
                    email = profile.email,
                    display_name = profile.display_name
                });

                callback?.Invoke(profile);

                Debug.Log($"✓ Profile loaded: {profile.username}");
            }
            else
            {
                Debug.LogError("✗ Failed to get profile");
                // Token might be expired
                Logout();
            }
        }
    }

    // ========================================================================
    // TRAVELS
    // ========================================================================

    /// <summary>
    /// Get all travels for current user
    /// </summary>
    public void GetTravels(Action<List<TravelData>> callback)
    {
        StartCoroutine(GetTravelsCoroutine(callback));
    }

    private IEnumerator GetTravelsCoroutine(Action<List<TravelData>> callback)
    {
        string url = $"{serverUrl}/api/travels";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                TravelsResponse response = JsonUtility.FromJson<TravelsResponse>(request.downloadHandler.text);
                callback?.Invoke(response.travels);

                Debug.Log($"✓ Loaded {response.travels.Count} travels");
            }
            else
            {
                Debug.LogError("✗ Failed to get travels");
                callback?.Invoke(new List<TravelData>());
            }
        }
    }

    /// <summary>
    /// Create new travel
    /// </summary>
    public void CreateTravel(TravelData travel, Action<TravelData> callback)
    {
        StartCoroutine(CreateTravelCoroutine(travel, callback));
    }

    private IEnumerator CreateTravelCoroutine(TravelData travel, Action<TravelData> callback)
    {
        string url = $"{serverUrl}/api/travels";
        string jsonData = JsonUtility.ToJson(travel);

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                CreateTravelResponse response = JsonUtility.FromJson<CreateTravelResponse>(request.downloadHandler.text);
                callback?.Invoke(response.travel);

                Debug.Log($"✓ Travel created: {travel.title}");
            }
            else
            {
                Debug.LogError("✗ Failed to create travel");
                callback?.Invoke(null);
            }
        }
    }

    // ========================================================================
    // FRIENDS
    // ========================================================================

    /// <summary>
    /// Get all friends for current user
    /// </summary>
    public void GetFriends(Action<List<FriendData>> callback)
    {
        StartCoroutine(GetFriendsCoroutine(callback));
    }

    private IEnumerator GetFriendsCoroutine(Action<List<FriendData>> callback)
    {
        string url = $"{serverUrl}/api/friends";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                FriendsResponse response = JsonUtility.FromJson<FriendsResponse>(request.downloadHandler.text);
                callback?.Invoke(response.friends);

                Debug.Log($"✓ Loaded {response.friends.Count} friends");
            }
            else
            {
                Debug.LogError("✗ Failed to get friends");
                callback?.Invoke(new List<FriendData>());
            }
        }
    }

    /// <summary>
    /// Create new friend
    /// </summary>
    public void CreateFriend(FriendData friend, Action<FriendData> callback)
    {
        StartCoroutine(CreateFriendCoroutine(friend, callback));
    }

    private IEnumerator CreateFriendCoroutine(FriendData friend, Action<FriendData> callback)
    {
        string url = $"{serverUrl}/api/friends";
        string jsonData = JsonUtility.ToJson(friend);

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                CreateFriendResponse response = JsonUtility.FromJson<CreateFriendResponse>(request.downloadHandler.text);
                callback?.Invoke(response.friend);

                Debug.Log($"✓ Friend created: {friend.name}");
            }
            else
            {
                Debug.LogError("✗ Failed to create friend");
                callback?.Invoke(null);
            }
        }
    }

    // ========================================================================
    // TOKEN MANAGEMENT
    // ========================================================================

    private void SaveToken()
    {
        if (!string.IsNullOrEmpty(authToken))
        {
            PlayerPrefs.SetString("WorldWindAuthToken", authToken);
            PlayerPrefs.Save();
        }
    }

    private void LoadToken()
    {
        if (PlayerPrefs.HasKey("WorldWindAuthToken"))
        {
            authToken = PlayerPrefs.GetString("WorldWindAuthToken");

            // Validate token by getting profile
            GetProfile((profile) =>
            {
                if (profile != null)
                {
                    Debug.Log($"✓ Auto-logged in as {profile.username}");
                }
            });
        }
    }

    private void ClearToken()
    {
        PlayerPrefs.DeleteKey("WorldWindAuthToken");
        PlayerPrefs.Save();
    }

    // ========================================================================
    // HELPERS
    // ========================================================================

    private void SetUserData(UserData user)
    {
        isAuthenticated = true;
        userId = user.id;
        username = user.username;
        email = user.email;
    }

    private string GetErrorMessage(UnityWebRequest request)
    {
        try
        {
            ErrorResponse error = JsonUtility.FromJson<ErrorResponse>(request.downloadHandler.text);
            return error.error;
        }
        catch
        {
            return request.error;
        }
    }

    // ========================================================================
    // DATA MODELS
    // ========================================================================

    [Serializable]
    public class RegisterRequest
    {
        public string email;
        public string username;
        public string password;
    }

    [Serializable]
    public class LoginRequest
    {
        public string email;
        public string password;
    }

    [Serializable]
    public class AuthResponse
    {
        public string message;
        public string token;
        public UserData user;
    }

    [Serializable]
    public class UserData
    {
        public int id;
        public string email;
        public string username;
        public string display_name;
    }

    [Serializable]
    public class UserProfile
    {
        public int id;
        public string email;
        public string username;
        public string display_name;
        public string avatar_url;
        public string oauth_provider;
        public int travels_count;
        public int friends_count;
    }

    [Serializable]
    public class TravelData
    {
        public int id;
        public string photo_url;
        public float latitude;
        public float longitude;
        public string title;
        public string description;
        public string date;
    }

    [Serializable]
    public class TravelsResponse
    {
        public List<TravelData> travels;
    }

    [Serializable]
    public class CreateTravelResponse
    {
        public string message;
        public TravelData travel;
    }

    [Serializable]
    public class FriendData
    {
        public int id;
        public string name;
        public string city;
        public float latitude;
        public float longitude;
        public string photo_url;
        public string color;
        public string group;
    }

    [Serializable]
    public class FriendsResponse
    {
        public List<FriendData> friends;
    }

    [Serializable]
    public class CreateFriendResponse
    {
        public string message;
        public FriendData friend;
    }

    [Serializable]
    public class ErrorResponse
    {
        public string error;
        public string message;
    }
}
