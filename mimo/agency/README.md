# MiMo AI Agency

AI automation agency powered by MiMo. We build AI systems that bring customers.

## Structure

```
agency/
├── landing/           # Landing page (Carrd/HTML)
│   └── index.html     # Simple, clean landing page
├── demos/             # Demo projects for client pitches
│   ├── demo_sales_assistant.py    # 24/7 AI chat demo
│   └── demo_lead_generator.py     # Lead discovery demo
└── leads/             # Lead generation module
    └── lead_engine.py             # Lead tracking & scoring
```

## Quick Start

### 1. View Landing Page

Open `landing/index.html` in browser, or:

```bash
cd agency/landing
python -m http.server 8000
# Visit http://localhost:8000
```

### 2. Run Demos

```bash
cd agency/demos
python demo_sales_assistant.py    # AI Sales Assistant demo
python demo_lead_generator.py     # Lead Generator demo
```

### 3. Generate Leads

```python
from leads.lead_engine import add_lead, get_qualified_leads

# Add a lead
add_lead(
    company="Acme Corp",
    website="https://acme.com",
    niche="saas",
    score=85
)

# Get qualified leads
qualified = get_qualified_leads(min_score=70)
```

## Products

1. **AI Lead Generator** ($500-$3,000) - Find and qualify leads
2. **AI Sales Assistant** ($1,000-$5,000) - 24/7 customer engagement
3. **Full AI Growth System** ($3,000-$10,000+) - Complete automation

## Outreach Workflow

1. Generate leads with `lead_engine.py`
2. Score and qualify (min 70/100)
3. Generate personalized outreach messages
4. Send via LinkedIn/email/Telegram
5. Track responses and conversions

## Niche Focus

- Dental clinics
- Real estate
- Fitness studios
- E-commerce
- SaaS companies
