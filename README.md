# TABOOST Creator Earnings & Tax Radar

**Two frontends + one backend for creator earnings tracking and agency management.**

---

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd taboost-radar/backend
pip install -r requirements.txt
python main.py
```

Backend runs at: **http://localhost:8000**

Health check: http://localhost:8000/health

---

### 2. Open the Frontends

**Creator View (Earnings Logger):**
- File: `public/creator-earnings-radar.html`
- Open in browser: `file:///C:/Users/Admin/clawd/taboost-radar/public/creator-earnings-radar.html`

**Agency Dashboard:**
- File: `public/taboost-dashboard.html`
- Open in browser: `file:///C:/Users/Admin/clawd/taboost-radar/public/taboost-dashboard.html`

---

### 3. Test the Connection

```bash
node test-connection.js
```

Shows pass/fail for every endpoint.

---

## 📁 Project Structure

```
taboost-radar/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python deps
├── public/
│   ├── api.js               # Shared API layer with mock fallbacks
│   ├── creator-earnings-radar.html   # Creator view
│   └── taboost-dashboard.html        # Agency view
├── API_CONTRACT.md          # Full API spec
├── test-connection.js       # Endpoint test script
└── README.md
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/creators` | List all creators |
| `GET` | `/api/creators/:id` | Get creator details |
| `POST` | `/api/creators` | Add new creator |
| `PUT` | `/api/creators/:id/notes` | Update manager notes |
| `GET` | `/api/creators/:id/scores` | Get performance scores |
| `GET` | `/api/creators/:id/earnings` | Get earnings history |
| `GET` | `/api/creators/:id/earnings/ytd` | Get YTD summary |
| `POST` | `/api/creators/:id/earnings` | Log new earning |
| `DELETE` | `/api/creators/:id/earnings/:eid` | Delete earning |
| `GET` | `/api/creators/:id/export/csv` | Download CSV |
| `GET` | `/api/creators/:id/export/pdf` | Download PDF |

See `API_CONTRACT.md` for full request/response shapes.

---

## 🧪 Mock Data Mode

The `api.js` layer has built-in mock data. If the backend is unreachable:
- Frontends still work perfectly
- Console shows `[API] Fallback to mock data`
- Toggle with `DEV_MODE` in `api.js`

---

## ⚙️ Configuration

**Change Backend URL:**
Edit `public/api.js`:
```javascript
const BACKEND_URL = 'http://localhost:8000';  // Change for production
```

**Disable Mock Data (production):**
```javascript
const DEV_MODE = false;  // No fallbacks, errors throw
```

---

## 📊 What Works End-to-End

| Feature | Creator View | Agency View |
|---------|--------------|-------------|
| Health Check | ✅ | ✅ |
| List Data | ✅ | ✅ |
| Create Entry | ✅ | ✅ |
| Delete Entry | ✅ | — |
| Update Notes | — | ✅ |
| Get Scores | — | ✅ |
| Export CSV | ✅ | — |
| Export PDF | ✅ | — |
| Mock Fallback | ✅ | ✅ |

---

## 🛠️ Next Steps

1. **Replace mock database** with SQLite/PostgreSQL
2. **Add authentication** (JWT tokens)
3. **Implement real PDF generation** (reportlab)
4. **Add creator analytics** (growth trends, predictions)
5. **Deploy to production** (Railway, Render, or VPS)

---

## 🎨 Design Notes

- **Zero visual changes** to original frontends
- All data layer changes are invisible to users
- API status indicator shows connection state
- Graceful degradation when backend is offline

---

Built for TABOOST agency • Creator earnings tracking made simple
