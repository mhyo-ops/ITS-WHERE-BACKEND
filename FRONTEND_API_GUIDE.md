# FastAPI — Frontend Integration Guide

> Generated automatically from live OpenAPI spec.
> Base URL: `http://127.0.0.1:8001`
> Full interactive docs: http://127.0.0.1:8001/docs

---

## Quick Start

### JavaScript helper (copy this into your project)

```javascript
const BASE_URL = 'http://127.0.0.1:8001'

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}
```

---

## Language Support

All public event endpoints accept `?lang=fr` | `?lang=ar` | `?lang=tzm`

- Default: `fr` if not specified
- Response always returns localized `title` and `description`
- Raw multilingual fields (`title_fr`, `title_ar`) are **never** in responses
- Discovery endpoints use `preferred_language` from user profile automatically

```
GET /events/?wilaya=Bejaia&lang=ar  → title in Arabic
GET /events/?wilaya=Bejaia&lang=fr  → title in French
```

---

## Caching Behaviour

Every event list response includes header: `x-cache: HIT` or `x-cache: MISS`

- `HIT` = served from Redis cache instantly
- `MISS` = fetched from database
- Cache invalidates automatically when admin creates/updates/deletes events
- **Do NOT cache responses in the frontend** — backend cache is already optimal

| Endpoint type | Cache TTL |
|---|---|
| Event lists | 10 minutes |
| Event detail | 30 minutes |
| Personalized discovery | 5 minutes |

---

## Error Handling

All errors follow this shape:
```json
{"detail": "Error message here"}
```

| Status | Meaning | Common cause |
|---|---|---|
| 400 | Bad Request | Duplicate email/username, invalid data |
| 401 | Unauthorized | Missing or expired token |
| 403 | Forbidden | Wrong role (user token on admin endpoint) |
| 404 | Not Found | Resource doesn't exist or is deactivated |
| 422 | Unprocessable | Missing required field in request body |

---

## Endpoints

### Authentication

#### 🔵 `POST /auth/user/register` — Register User 🌐 _public_

**Request Body:**
```json
{
  "email": "string",
  "username": "string",
  "password": "string",
  "preferred_language": "fr",
  "postal_code": "value"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "string",
  "username": "string",
  "preferred_language": "string",
  "postal_code": "value",
  "is_active": true,
  "is_verified": true
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/user/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "username": "string",
  "password": "string",
  "preferred_language": "fr",
  "postal_code": "value"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/user/register', {
  method: 'POST',
  body: JSON.stringify({
  "email": "string",
  "username": "string",
  "password": "string",
  "preferred_language": "fr",
  "postal_code": "value"
})
});
```

---

#### 🔵 `POST /auth/user/verify-email` — Verify Email 🌐 _public_

**Request Body:**
```json
{
  "email": "string",
  "code": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/user/verify-email' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "code": "string"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/user/verify-email', {
  method: 'POST',
  body: JSON.stringify({
  "email": "string",
  "code": "string"
})
});
```

---

#### 🔵 `POST /auth/user/forgot-password` — Forgot Password 🌐 _public_

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/user/forgot-password' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/user/forgot-password', {
  method: 'POST',
  body: JSON.stringify({
  "email": "string"
})
});
```

---

#### 🔵 `POST /auth/user/reset-password` — Reset Password 🌐 _public_

**Request Body:**
```json
{
  "email": "string",
  "code": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/user/reset-password' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "code": "string",
  "new_password": "string"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/user/reset-password', {
  method: 'POST',
  body: JSON.stringify({
  "email": "string",
  "code": "string",
  "new_password": "string"
})
});
```

---

#### 🔵 `POST /auth/user/login` — Login User 🌐 _public_

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/user/login' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "password": "string"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/user/login', {
  method: 'POST',
  body: JSON.stringify({
  "email": "string",
  "password": "string"
})
});
```

---

#### 🔵 `POST /auth/admin/register` — Register Admin 🌐 _public_

Creates a new admin.
Protected by superadmin_token header.
Only one person should know this token.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `admin_slug` | string | ✅ | — |
| `password` | string | ✅ | — |
| `superadmin_token` | string | ✅ | — |

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/admin/register?admin_slug=string&password=string&superadmin_token=string' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/admin/register', {
  method: 'POST',
});
```

---

#### 🔵 `POST /auth/admin/login` — Login Admin 🌐 _public_

**Request Body:**
```json
{
  "admin_slug": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/auth/admin/login' \
  -H 'Content-Type: application/json' \
  -d '{
  "admin_slug": "string",
  "password": "string"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/auth/admin/login', {
  method: 'POST',
  body: JSON.stringify({
  "admin_slug": "string",
  "password": "string"
})
});
```

---

### Categories

#### 🟢 `GET /categories/` — List Categories 🌐 _public_

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | optional | — |
| `limit` | integer | optional | — |
| `active_only` | boolean | optional | — |

**Response:**
```json
[
  {
    "name": "string",
    "description": "value",
    "id": 1,
    "is_active": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/categories/?skip=0&limit=100&active_only=True' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/categories/', {
  method: 'GET',
});
```

---

#### 🔵 `POST /categories/` — Create Category Endpoint 🔒 _auth required_

**Request Body:**
```json
{
  "name": "string",
  "description": "value"
}
```

**Response:**
```json
{
  "name": "string",
  "description": "value",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/categories/' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "string",
  "description": "value"
}'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/categories/', {
  method: 'POST',
  body: JSON.stringify({
  "name": "string",
  "description": "value"
})
});
```

---

#### 🟢 `GET /categories/{category_id}` — Read Category 🌐 _public_

**Response:**
```json
{
  "name": "string",
  "description": "value",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/categories/{category_id}' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/categories/{category_id}', {
  method: 'GET',
});
```

---

#### 🟡 `PUT /categories/{category_id}` — Update Category Endpoint 🔒 _auth required_

**Request Body:**
```json
{
  "name": "value",
  "description": "value",
  "is_active": "value"
}
```

**Response:**
```json
{
  "name": "string",
  "description": "value",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X PUT 'http://127.0.0.1:8001/categories/{category_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "value",
  "description": "value",
  "is_active": "value"
}'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/categories/{category_id}', {
  method: 'PUT',
  body: JSON.stringify({
  "name": "value",
  "description": "value",
  "is_active": "value"
})
});
```

---

#### 🔴 `DELETE /categories/{category_id}` — Delete Category 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X DELETE 'http://127.0.0.1:8001/categories/{category_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/categories/{category_id}', {
  method: 'DELETE',
});
```

---

### Events

#### 🟢 `GET /events/` — List Events 🌐 _public_

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | optional | — |
| `limit` | integer | optional | — |
| `wilaya` | string | optional | — |
| `postal_code` | string | optional | — |
| `category_id` | string | optional | — |
| `status` | string | optional | — |
| `lang` | string | optional | — |
| `active_only` | boolean | optional | — |

**Response:**
```json
[
  {
    "id": 1,
    "title": "string",
    "title_ar": "value",
    "title_fr": "value",
    "title_tam": "value",
    "wilaya": "string",
    "commune": "string",
    "postal_code": "string",
    "date_begin": "string",
    "date_end": "value",
    "category_id": 1,
    "status": "string",
    "cost": "string",
    "remaining_spots": "value",
    "registration_required": true,
    "is_volunteering": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/events/?skip=0&limit=100&wilaya=value' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/events/', {
  method: 'GET',
});
```

---

#### 🔵 `POST /events/` — Create Event Endpoint 🔒 _auth required_

**Request Body:**
```json
{
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "input_language": "fr"
}
```

**Response:**
```json
{
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/events/' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "input_language": "fr"
}'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/events/', {
  method: 'POST',
  body: JSON.stringify({
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "input_language": "fr"
})
});
```

---

#### 🟢 `GET /events/{event_id}` — Read Event 🌐 _public_

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lang` | string | optional | — |

**Response:**
```json
{
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/events/{event_id}?lang=value' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/events/{event_id}', {
  method: 'GET',
});
```

---

#### 🟡 `PUT /events/{event_id}` — Update Event Endpoint 🔒 _auth required_

**Request Body:**
```json
{
  "category_id": "value",
  "title": "value",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "value",
  "postal_code": "value",
  "commune": "value",
  "wilaya": "value",
  "date_begin": "value",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": "value",
  "is_volunteering": "value",
  "volunteer_skills": "value",
  "cost": "value",
  "status": "value",
  "is_active": "value"
}
```

**Response:**
```json
{
  "category_id": 1,
  "title": "string",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "string",
  "postal_code": "string",
  "commune": "string",
  "wilaya": "string",
  "date_begin": "string",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": false,
  "is_volunteering": false,
  "volunteer_skills": "value",
  "cost": "Free",
  "status": "upcoming",
  "id": 1,
  "is_active": true
}
```

**curl:**
```bash
curl -sS -X PUT 'http://127.0.0.1:8001/events/{event_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "category_id": "value",
  "title": "value",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "value",
  "postal_code": "value",
  "commune": "value",
  "wilaya": "value",
  "date_begin": "value",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": "value",
  "is_volunteering": "value",
  "volunteer_skills": "value",
  "cost": "value",
  "status": "value",
  "is_active": "value"
}'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/events/{event_id}', {
  method: 'PUT',
  body: JSON.stringify({
  "category_id": "value",
  "title": "value",
  "title_ar": "value",
  "title_fr": "value",
  "title_tam": "value",
  "description": "value",
  "description_ar": "value",
  "description_fr": "value",
  "description_tam": "value",
  "address": "value",
  "postal_code": "value",
  "commune": "value",
  "wilaya": "value",
  "date_begin": "value",
  "date_end": "value",
  "capacity": "value",
  "remaining_spots": "value",
  "registration_link": "value",
  "registration_contact": "value",
  "registration_required": "value",
  "is_volunteering": "value",
  "volunteer_skills": "value",
  "cost": "value",
  "status": "value",
  "is_active": "value"
})
});
```

---

#### 🔴 `DELETE /events/{event_id}` — Delete Event 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X DELETE 'http://127.0.0.1:8001/events/{event_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/events/{event_id}', {
  method: 'DELETE',
});
```

---

### Users

#### 🟢 `GET /users/me` — Read Current User 🔒 _auth required_

**Response:**
```json
{
  "id": 1,
  "email": "string",
  "username": "string",
  "preferred_language": "string",
  "postal_code": "value",
  "is_active": true,
  "is_verified": true
}
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/users/me' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me', {
  method: 'GET',
});
```

---

#### 🟡 `PUT /users/me` — Update Current User 🔒 _auth required_

**Request Body:**
```json
{
  "preferred_language": "value",
  "postal_code": "value"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "string",
  "username": "string",
  "preferred_language": "string",
  "postal_code": "value",
  "is_active": true,
  "is_verified": true
}
```

**curl:**
```bash
curl -sS -X PUT 'http://127.0.0.1:8001/users/me' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "preferred_language": "value",
  "postal_code": "value"
}'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me', {
  method: 'PUT',
  body: JSON.stringify({
  "preferred_language": "value",
  "postal_code": "value"
})
});
```

---

#### 🔴 `DELETE /users/me` — Deactivate Current User 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X DELETE 'http://127.0.0.1:8001/users/me' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me', {
  method: 'DELETE',
});
```

---

#### 🟢 `GET /users/me/favourites` — Get Favourite Categories 🔒 _auth required_

**Response:**
```json
[
  {
    "name": "string",
    "description": "value",
    "id": 1,
    "is_active": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/users/me/favourites' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/favourites', {
  method: 'GET',
});
```

---

#### 🔵 `POST /users/me/favourites/{category_id}` — Add Favourite Category 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/users/me/favourites/{category_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/favourites/{category_id}', {
  method: 'POST',
});
```

---

#### 🔴 `DELETE /users/me/favourites/{category_id}` — Remove Favourite Category 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X DELETE 'http://127.0.0.1:8001/users/me/favourites/{category_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/favourites/{category_id}', {
  method: 'DELETE',
});
```

---

#### 🟢 `GET /users/me/events/discover/wilaya` — Discover Events By Wilaya 🔒 _auth required_

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `wilaya` | string | ✅ | — |
| `status` | string | optional | — |
| `skip` | integer | optional | — |
| `limit` | integer | optional | — |

**Response:**
```json
[
  {
    "id": 1,
    "title": "string",
    "title_ar": "value",
    "title_fr": "value",
    "title_tam": "value",
    "wilaya": "string",
    "commune": "string",
    "postal_code": "string",
    "date_begin": "string",
    "date_end": "value",
    "category_id": 1,
    "status": "string",
    "cost": "string",
    "remaining_spots": "value",
    "registration_required": true,
    "is_volunteering": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/users/me/events/discover/wilaya?wilaya=string&status=value&skip=0' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/events/discover/wilaya', {
  method: 'GET',
});
```

---

#### 🟢 `GET /users/me/events/discover/commune` — Discover Events By Commune 🔒 _auth required_

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `commune` | string | ✅ | — |
| `status` | string | optional | — |
| `skip` | integer | optional | — |
| `limit` | integer | optional | — |

**Response:**
```json
[
  {
    "id": 1,
    "title": "string",
    "title_ar": "value",
    "title_fr": "value",
    "title_tam": "value",
    "wilaya": "string",
    "commune": "string",
    "postal_code": "string",
    "date_begin": "string",
    "date_end": "value",
    "category_id": 1,
    "status": "string",
    "cost": "string",
    "remaining_spots": "value",
    "registration_required": true,
    "is_volunteering": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/users/me/events/discover/commune?commune=string&status=value&skip=0' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/events/discover/commune', {
  method: 'GET',
});
```

---

#### 🟢 `GET /users/me/events` — List Registered Events 🔒 _auth required_

**Response:**
```json
[
  {
    "category_id": 1,
    "title": "string",
    "title_ar": "value",
    "title_fr": "value",
    "title_tam": "value",
    "description": "value",
    "description_ar": "value",
    "description_fr": "value",
    "description_tam": "value",
    "address": "string",
    "postal_code": "string",
    "commune": "string",
    "wilaya": "string",
    "date_begin": "string",
    "date_end": "value",
    "capacity": "value",
    "remaining_spots": "value",
    "registration_link": "value",
    "registration_contact": "value",
    "registration_required": false,
    "is_volunteering": false,
    "volunteer_skills": "value",
    "cost": "Free",
    "status": "upcoming",
    "id": 1,
    "is_active": true
  }
]
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/users/me/events' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/events', {
  method: 'GET',
});
```

---

#### 🔵 `POST /users/me/events/{event_id}` — Register For Event 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/users/me/events/{event_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/events/{event_id}', {
  method: 'POST',
});
```

---

#### 🔴 `DELETE /users/me/events/{event_id}` — Unregister From Event 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X DELETE 'http://127.0.0.1:8001/users/me/events/{event_id}' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/users/me/events/{event_id}', {
  method: 'DELETE',
});
```

---

### Eco Metrics

#### 🟢 `GET /metrics/` — Get Metrics 🌐 _public_

**Response:**
```json
{
  "total_queries": 1,
  "cache_hits": 1,
  "llm_calls": 1,
  "cache_hit_rate_percent": 1.0,
  "avg_response_time_ms": 1.0,
  "avg_cached_response_time_ms": 1.0,
  "avg_llm_response_time_ms": 1.0,
  "estimated_energy_saved_wh": 1.0,
  "queries_by_language": "value",
  "queries_by_wilaya": "value",
  "period": "all-time"
}
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/metrics/' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/metrics/', {
  method: 'GET',
});
```

---

#### 🟢 `GET /metrics/reset` — Reset Metrics 🔒 _auth required_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/metrics/reset' \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
// Requires token in localStorage ('access_token')
const response = await apiFetch('/metrics/reset', {
  method: 'GET',
});
```

---

### chat

#### 🔵 `POST /chat/` — Chat Endpoint 🌐 _public_

RAG chatbot endpoint.
Accepts natural language in FR/AR/TZM.
Returns answer + matched events.
Redis cached for 1800s per unique message.

**Request Body:**
```json
{
  "message": "string",
  "lang": "fr"
}
```

**Response:**
```json
{
  "answer": "string",
  "matched_event_ids": [
    1
  ],
  "events_used": 1,
  "cached": false
}
```

**curl:**
```bash
curl -sS -X POST 'http://127.0.0.1:8001/chat/' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "string",
  "lang": "fr"
}'
```

**JavaScript:**
```javascript
const response = await apiFetch('/chat/', {
  method: 'POST',
  body: JSON.stringify({
  "message": "string",
  "lang": "fr"
})
});
```

---

### General

#### 🟢 `GET /` — Root 🌐 _public_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/', {
  method: 'GET',
});
```

---

#### 🟢 `GET /health` — Health 🌐 _public_

**Response:**
```json
"value"
```

**curl:**
```bash
curl -sS -X GET 'http://127.0.0.1:8001/health' \
  -H 'Content-Type: application/json'
```

**JavaScript:**
```javascript
const response = await apiFetch('/health', {
  method: 'GET',
});
```

---

## Wilaya & Postal Code Reference

| Wilaya | Postal Code |
|---|---|
| Bejaia | 06000 |
| Setif | 19000 |
| Alger | 16000 |
| Tizi Ouzou | 15000 |
| Oran | 31000 |
| Constantine | 25000 |

> Real deployment will cover all 58 wilayat.

---

## Frontend Developer Checklist

1. Open http://127.0.0.1:8001/docs — confirm API is running
2. `POST /auth/user/register` — create a test account
3. `POST /auth/user/login` — get token, store in localStorage
4. `GET /categories/` — load categories for dropdowns
5. `GET /events/?lang=fr` — load all events
6. `GET /events/?wilaya=Bejaia&lang=fr` — filter by location
7. `POST /users/me/favourites/1` — add a favourite category
8. `GET /users/me/events/discover/wilaya?wilaya=Bejaia` — personalized feed
9. `POST /users/me/events/1` — register for an event
10. `POST /auth/admin/login` (slug: `admin_odej`, pass: `Admin2026!`)
11. `POST /events/` with `input_language: fr` — Arabic auto-fills
