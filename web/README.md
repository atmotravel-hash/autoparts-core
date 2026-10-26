# AutoParts Core — website

Next.js сайт (не Streamlit). Деплой на Vercel из папки `web/`.

## Local

```bash
cd web
npm install
npm run dev
```

Откройте http://localhost:3000

## Vercel

Root Directory: `web`  
Framework: Next.js  
Region: `fra1`

## API

`GET /api/search?q=фара+Passat+B8&sources=olx_ua,prom_ua,nine99_md,olx_ro&limit=6`

Default sources (UA · MD · RO): `olx_ua,prom_ua,flagma_ua,nine99_md,prom_md,olx_ro`
