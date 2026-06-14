# Business Scanner SaaS v1

Find businesses that are losing money from operational gaps.

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m api.main
```

API runs on http://localhost:8000

### Frontend

Open `frontend/index.html` in browser, or:

```bash
cd frontend
python -m http.server 3000
```

Frontend runs on http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/scan` | POST | Scan businesses |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger docs |

## Example Request

```json
POST /scan
{
  "city": "Bishkek",
  "niche": "dental",
  "limit": 10
}
```

## Example Response

```json
{
  "city": "Bishkek",
  "niche": "dental",
  "total_found": 10,
  "results": [
    {
      "name": "Али-Дент",
      "score": 87,
      "tier": "A",
      "monthly_loss_estimate": 8500,
      "reasons": [
        "No online booking system",
        "No live chat or instant response"
      ]
    }
  ],
  "summary": {
    "total_estimated_monthly_loss": 52000
  }
}
```

## Monetization

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 1 scan/day |
| Pro | $19/mo | Unlimited scans + PDF export |
| Business | $49/mo | API access + AI insights |

## Tech Stack

- Backend: FastAPI
- Frontend: HTML/CSS/JS
- Deploy: Render (backend) + Vercel (frontend)
