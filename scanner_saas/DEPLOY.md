# Deployment Guide

## Backend (Render)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: New Web Service
1. Click "New" → "Web Service"
2. Connect GitHub repo or upload folder
3. Settings:
   - Name: `leakfinder-api`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add in Render dashboard:
```
GOOGLE_MAPS_API_KEY=your_key_here
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_BUSINESS_PRICE_ID=price_...
```

### Step 4: Deploy
Click "Create Web Service"

Your API will be at: `https://leakfinder-api.onrender.com`

---

## Frontend (Vercel)

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### Step 2: New Project
1. Click "New Project"
2. Upload `frontend` folder
3. Framework: `Other`

### Step 3: Update API URL
In `landing.html`, change:
```javascript
const API_URL = 'https://leakfinder-api.onrender.com';
```

### Step 4: Deploy
Click "Deploy"

Your frontend will be at: `https://leakfinder.vercel.app`

---

## Post-Deploy Checklist

1. Test scan endpoint
2. Test checkout flow
3. Verify Stripe payments
4. Check all env vars are set

---

## Troubleshooting

### Backend not starting?
- Check logs in Render dashboard
- Verify all env vars are set
- Check `requirements.txt` has all dependencies

### Frontend can't connect?
- Verify CORS is enabled (already done)
- Check API_URL is correct
- Check browser console for errors

### Stripe not working?
- Verify STRIPE_SECRET_KEY is set
- Check Stripe dashboard for errors
- Test with Stripe test cards
