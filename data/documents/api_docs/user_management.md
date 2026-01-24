# User Management API

This document describes the User Management endpoints.

## Base URL

```
https://api.example.com/v1/users
```

## Endpoints

### List Users

```
GET /users
```

Query parameters:
- `limit` (int, default 20): Maximum users to return
- `offset` (int, default 0): Pagination offset
- `status` (string): Filter by status (active, suspended, pending)

Response:
```json
{
  "users": [...],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### Get User

```
GET /users/{user_id}
```

Returns a single user by ID. Returns 404 if user not found.

### Create User

```
POST /users
```

Request body:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "member"
}
```

Returns 201 with created user. Returns 400 for validation errors.

### Update User

```
PUT /users/{user_id}
```

Updates user properties. Only included fields are updated.

### Delete User

```
DELETE /users/{user_id}
```

Soft-deletes a user. Returns 204 on success.

## Common Errors

### 400 Bad Request

Validation failed. Check the `errors` array in response:
```json
{
  "error": "validation_error",
  "errors": [
    {"field": "email", "message": "Invalid email format"}
  ]
}
```

### 404 Not Found

User with specified ID doesn't exist. Verify the user_id is correct.

### 409 Conflict

Action conflicts with current state:
- Email already in use
- Cannot delete user with active resources

### 422 Unprocessable Entity

Request understood but cannot be processed:
- User has pending operations
- Account in restricted state

## Pagination

All list endpoints support pagination:
- Use `limit` and `offset` for simple pagination
- Response includes `total` count for calculating pages
- Maximum limit is 100

## Filtering

Filter users by status:
```
GET /users?status=active
GET /users?status=suspended
```

Search by email:
```
GET /users?email=user@example.com
```

## Rate Limits

User endpoints share the global rate limit. Creating users has additional limits:
- 10 users per minute per API key
- 100 users per hour per API key
