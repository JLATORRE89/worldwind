# HTTPS Setup for WorldWind Backend Server

This server supports HTTPS natively through `app.py` using `.env` settings.

## 1) Enable HTTPS quickly (adhoc cert)

Use this for local development where you just need encrypted transport.

1. Copy environment file if needed:

```bash
cp .env.example .env
```

2. Set:

```env
HTTPS_ENABLED=True
SSL_CERT_FILE=
SSL_KEY_FILE=
```

3. Start server:

```bash
python app.py
```

4. Open:

- `https://localhost:5000/health`

Note: browser will warn because the cert is self-signed and regenerated each run.

## 2) Enable HTTPS with persistent cert/key

Use this when you want stable cert files.

1. Create cert directory:

```bash
mkdir -p certs
```

2. Generate a self-signed certificate (OpenSSL):

```bash
openssl req -x509 -newkey rsa:2048 -nodes -sha256 -days 365 \
  -keyout certs/server.key \
  -out certs/server.crt \
  -subj "/CN=localhost"
```

3. Set `.env`:

```env
HTTPS_ENABLED=True
SSL_CERT_FILE=certs/server.crt
SSL_KEY_FILE=certs/server.key
```

4. Start server:

```bash
python app.py
```

## 3) Verify HTTPS

```bash
curl -k https://localhost:5000/health
```

Expected response:

```json
{"status":"ok","service":"WorldWind Auth Server"}
```

## 4) Update dependent URLs

When HTTPS is enabled, switch client/server URLs from `http://` to `https://`.

- Python client base URL
- Unity auth client `serverUrl`
- OAuth provider redirect URIs:
  - `https://localhost:5000/auth/google/callback`
  - `https://localhost:5000/auth/discord/callback`
  - `https://localhost:5000/auth/microsoft/callback`

## 5) Production recommendation

For externally reachable deployments, terminate TLS at a reverse proxy
(nginx/Apache/Caddy) with managed certificates (for example, Let's Encrypt),
and run Flask behind it.
