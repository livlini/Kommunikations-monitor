# CFO Communication Monitor

A deployable Streamlit MVP for monitoring public trends relevant to CFO, Audit, Tax and AI communication.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Push this folder to a Git repository and deploy it on a Streamlit-compatible host. The dashboard itself needs no API key in prototype mode.

## Weekly automation architecture

Use a scheduled job (GitHub Actions / cloud cron) to:
1. fetch permitted public RSS/API/web sources;
2. normalize and deduplicate articles;
3. classify and summarize them;
4. aggregate topics by week;
5. write a JSON/CSV/database snapshot consumed by `app.py`.

Keep API keys in deployment secrets, never in source code.

## Initial categories / keywords

- AI: generative AI, AI agents, agentic AI, AI governance, Copilot
- CFO: CFO, finance transformation, forecasting, ERP, financial reporting, automation
- Audit: audit, assurance, revision, financial reporting
- Tax: tax, VAT, moms, transfer pricing, e-invoicing

## Initial public source universe

- KPMG Denmark Insights
- FSR – danske revisorer
- Skattestyrelsen
- Digitaliseringsstyrelsen

Before automating extraction from any site, verify its robots.txt, terms and/or use an offered RSS/API. Prefer RSS/API feeds where available.
