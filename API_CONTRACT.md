# TABOOST Creator Earnings & Tax Radar — API Contract

**Base URL (dev):** `http://localhost:8000`  
**Base URL (prod):** `https://api.taboost.com` (TBD)

---

## 🔌 Endpoints

### System

| Method | Path | Description | Frontend |
|--------|------|-------------|----------|
| `GET` | `/health` | Health check | Both (on load) |

**Response:**
```json
{ "status": "healthy", "timestamp": "2025-01-15T10:30:00Z" }
```

---

### Creators (Agency Dashboard)

| Method | Path | Description | Frontend |
|--------|------|-------------|----------|
| `GET` | `/api/creators` | Full creator roster | Agency |
| `GET` | `/api/creators/:id` | Single creator detail | Agency |
| `POST` | `/api/creators` | Add new creator | Agency |
| `PUT` | `/api/creators/:id/notes` | Save manager notes | Agency |
| `GET` | `/api/creators/:id/scores` | Growth/viral/brand scores | Agency |

---

### Earnings (Creator View + Agency)

| Method | Path | Description | Frontend |
|--------|------|-------------|----------|
| `GET` | `/api/creators/:id/earnings` | Earnings history | Both |
| `GET` | `/api/creators/:id/earnings/ytd` | YTD summary by source | Both |
| `POST` | `/api/creators/:id/earnings` | Log new earning | Creator |
| `DELETE` | `/api/creators/:id/earnings/:eid` | Delete entry | Creator |

---

### Export (Creator View)

| Method | Path | Description | Frontend |
|--------|------|-------------|----------|
| `GET` | `/api/creators/:id/export/csv` | Download CSV | Creator |
| `GET` | `/api/creators/:id/export/pdf` | Download tax pack PDF | Creator |

---

## 📦 Request/Response Shapes

### `GET /health`
**Response:**
```json
{ "status": "ok", "service": "taboost-api" }
```

---

### `GET /api/creators`
**Response:**
```json
[
  {
    "id": 1,
    "handle": "@rileydance",
    "name": "Riley Summers",
    "followers": 892000,
    "avgViews": 410000,
    "engagement": 8.7,
    "postsPerWeek": 6,
    "status": "hot",
    "trend": [820, 835, 841, 858, 867, 879, 892],
    "notes": "Brand deal closing with FashionNova."
  }
]
```

---

### `GET /api/creators/:id`
**Response:**
```json
{
  "id": 1,
  "handle": "@rileydance",
  "name": "Riley Summers",
  "followers": 892000,
  "avgViews": 410000,
  "engagement": 8.7,
  "postsPerWeek": 6,
  "status": "hot",
  "trend": [820, 835, 841, 858, 867, 879, 892],
  "notes": "Brand deal closing with FashionNova."
}
```

---

### `POST /api/creators`
**Request:**
```json
{
  "handle": "@newcreator",
  "name": "New Creator",
  "followers": 100000,
  "avgViews": 50000,
  "engagement": 7.5
}
```

**Response:** Created creator object (same as GET /:id)

---

### `PUT /api/creators/:id/notes`
**Request:**
```json
{ "notes": "Updated manager notes here" }
```

**Response:** Updated creator object

---

### `GET /api/creators/:id/scores`
**Response:**
```json
{
  "growth": 78,
  "viral": 65,
  "brand": 82
}
```

---

### `GET /api/creators/:id/earnings`
**Response:**
```json
[
  {
    "id": 1,
    "source": "live",
    "amount": 84.50,
    "date": "2025-01-14",
    "note": "Tuesday night LIVE, 1.5hrs"
  }
]
```

---

### `GET /api/creators/:id/earnings/ytd`
**Response:**
```json
{
  "creatorId": 1,
  "taxYear": 2025,
  "ytdTotal": 12450.75,
  "bySource": {
    "live": 4200.50,
    "brand": 5600.00,
    "fund": 1850.25,
    "ugc": 800.00
  }
}
```

---

### `POST /api/creators/:id/earnings`
**Request:**
```json
{
  "source": "live",
  "amount": 84.50,
  "date": "2025-01-14",
  "note": "Tuesday night LIVE, 1.5hrs"
}
```

**Response:** Created earning object

---

### `DELETE /api/creators/:id/earnings/:eid`
**Response:**
```json
{ "success": true, "message": "Entry deleted" }
```

---

### `GET /api/creators/:id/export/csv`
**Response:** `text/csv` file download

---

### `GET /api/creators/:id/export/pdf`
**Response:** `application/pdf` file download

---

## 🧪 Error Responses

**404 Not Found:**
```json
{ "error": "Creator not found" }
```

**500 Server Error:**
```json
{ "error": "Internal server error" }
```

**Fallback:** API layer returns mock data on any error (dev mode)

---

## 🔑 Auth Notes

For initial dev, **auth is disabled** — all endpoints are open.  
Production will add JWT bearer tokens via `Authorization: Bearer <token>` header.
