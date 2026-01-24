# API Authentication

This document describes authentication mechanisms for the REST API.

## Overview

All API requests require authentication using an API key. The API key should be included in the `X-API-Key` header of every request.

## Getting an API Key

1. Log in to the dashboard at https://dashboard.example.com
2. Navigate to Settings → API Keys
3. Click "Generate New Key"
4. Copy and store the key securely (it won't be shown again)

## Authentication Headers

Include the following header in all requests:

```
X-API-Key: your-api-key-here
```

## Common Authentication Errors

### 401 Unauthorized

This error indicates authentication failure. Common causes:

- **Invalid API key**: The key doesn't exist or has been revoked
- **Missing header**: The X-API-Key header is not present
- **Expired key**: API key has exceeded its validity period (if applicable)

**Solution**: Verify your API key is correct and active in the dashboard.

### 403 Forbidden

This error indicates the API key is valid but lacks permission.

- **Role mismatch**: Key doesn't have required permissions
- **IP restriction**: Request from unauthorized IP address
- **Rate limited**: Too many requests (check X-RateLimit-* headers)

**Solution**: Check key permissions in dashboard or contact support.

## Rate Limiting

- Standard tier: 100 requests per minute
- Professional tier: 1000 requests per minute
- Enterprise tier: Custom limits

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Key Rotation

For security, rotate API keys regularly:

1. Generate a new key in the dashboard
2. Update your application configuration
3. Test with the new key
4. Revoke the old key

Keys cannot be recovered after revocation.

## Troubleshooting

### "Invalid API key" error after copy-paste

Ensure no extra whitespace or line breaks were included when copying the key.

### Requests work from curl but not from application

Check that your HTTP client properly sets the header. Some frameworks require explicit header configuration.

### Intermittent 401 errors

May indicate key rotation in progress or caching issues. Ensure you're using the latest key and clear any API key caches.
