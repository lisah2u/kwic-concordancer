# Deployment Guide

This guide covers deploying the Concordancer application using Netlify (frontend) + Railway (backend).

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Backend       │
│   (Netlify)     │    │   (Railway)     │
│                 │    │                 │
│ • Static Files  │    │ • FastAPI App   │
│ • HTML/CSS/JS   │    │ • Corpus Files  │
│ • Tailwind CSS  │    │ • File Cache    │
└─────────────────┘    └─────────────────┘
```

## Prerequisites

1. **Git repository** with your code
2. **Netlify account** (free tier available)
3. **Railway account** (free tier with usage limits)
4. **Node.js 18+** for Tailwind CSS builds
5. **Python 3.11+** and **uv** for backend

## Frontend Deployment (Netlify)

### 1. Connect Repository

1. Go to [Netlify](https://netlify.com) and sign in
2. Click **"New site from Git"**
3. Connect your GitHub/GitLab repository
4. Select the `kwic-concordancer` repository

### 2. Configure Build Settings

Netlify will automatically detect the `netlify.toml` configuration:

```toml
[build]
  command = "npm run build-css"
  publish = "static"

[build.environment]
  NODE_VERSION = "18"
```

### 3. Deploy

1. Click **"Deploy site"**
2. Netlify will:
   - Install Node.js dependencies
   - Run `npm run build-css` to generate Tailwind CSS
   - Publish the `static/` directory

### 4. Custom Domain (Optional)

1. In Netlify dashboard, go to **Site Settings > Domain Management**
2. Add your custom domain
3. Configure DNS settings as instructed

## Backend Deployment (Railway)

### 1. Connect Repository

1. Go to [Railway](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `kwic-concordancer` repository

### 2. Configure Environment

Railway will automatically detect Python and use the `railway.toml` configuration:

```toml
[deploy]
startCommand = "uv run uvicorn concordance_api:app --host 0.0.0.0 --port $PORT"

[env]
PORT = "8000"
PYTHONPATH = "."
UV_SYSTEM_PYTHON = "1"
```

### 3. Environment Variables

In Railway dashboard, set these environment variables:

```bash
PORT=8000
PYTHONPATH=.
UV_SYSTEM_PYTHON=1
RAILWAY_ENVIRONMENT=production
```

### 4. Deploy

1. Railway will automatically:
   - Detect Python project
   - Install dependencies from `requirements.txt`
   - Start the FastAPI server
2. Note your Railway app URL (e.g., `https://kwic-concordancer-production.up.railway.app`)

## Update Frontend for Production

### 1. Update Backend URL

The frontend automatically detects the environment:

```javascript
// In app.js - already configured
function getApiBaseUrl() {
    if (window.location.hostname === 'localhost') {
        return '';  // Local development
    }
    return 'https://kwic-concordancer-production.up.railway.app';  // Production
}
```

### 2. Update Netlify Redirects

Update `netlify.toml` with your actual Railway URL:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://YOUR-RAILWAY-APP.up.railway.app/api/:splat"
  status = 200
  force = true
```

## Local Development vs Production

### Development Workflow

```bash
# Frontend development
npm run watch-css          # Watch Tailwind CSS changes
uv run uvicorn concordance_api:app --reload  # Backend with auto-reload

# Testing
uv run pytest test_concordance.py -v
```

### Production Build

```bash
# Frontend production build
npm run build-css          # Minified CSS
npm run build              # Same as build-css

# Backend testing
uv run uvicorn concordance_api:app --host 0.0.0.0 --port 8000
```

## Deployment Commands

### Manual Deployment

```bash
# Deploy to Netlify (requires Netlify CLI)
npm run deploy-netlify      # Production deploy
npm run preview-netlify     # Preview deploy

# Deploy to Railway (automatic on git push)
git push origin main        # Triggers Railway deployment
```

### Automatic Deployment

Both platforms support automatic deployment:

- **Netlify**: Deploys on every push to main branch
- **Railway**: Deploys on every push to main branch

## Environment-Specific Configuration

### Development (localhost:8000)
- Frontend and backend on same server
- Relative API URLs
- File watching for CSS builds
- Hot reload for backend

### Production (Netlify + Railway)
- Frontend on Netlify CDN
- Backend on Railway
- Cross-origin API calls
- Minified assets
- Production optimizations

## Monitoring and Logs

### Netlify
- Build logs in deploy section
- Function logs for serverless functions
- Analytics dashboard

### Railway
- Application logs in dashboard
- Metrics and monitoring
- Resource usage tracking

## Security Considerations

### Current Security Features ✅

**CORS Configuration** (Read-only optimized):
```python
# In concordance_api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for educational use
    allow_credentials=False,  # Secure with wildcard origins
    allow_methods=["GET", "OPTIONS"],  # Read-only operations
    allow_headers=["*"],
)
```

**Rate Limiting** (Prevents abuse):
- `/corpora` endpoint: 30 requests/minute
- `/search` endpoints: 60 requests/minute  
- `/view` endpoint: 20 requests/minute
- Automatic 429 responses when limits exceeded

**File Access Security**:
- Path traversal protection (blocks `../`, `/`, `\`)
- Restricted to `samples/` directory only
- Input validation on corpus names

**Production URLs**:
- **Frontend**: https://kwic-concordancer.netlify.app/
- **Backend**: https://kwic-concordancer-production.up.railway.app/

### HTTPS
- Netlify: Automatic HTTPS with Let's Encrypt ✅
- Railway: Automatic HTTPS for all deployments ✅

## Troubleshooting

### Common Issues

1. **API calls failing in production**
   - Check CORS settings
   - Verify Railway URL in frontend
   - Check Network tab in browser

2. **CSS not loading**
   - Ensure `npm run build-css` runs successfully
   - Check Tailwind configuration
   - Verify `static/tailwind.css` is generated

3. **Build failures**
   - Check Node.js version (requires 18+)
   - Verify all dependencies in `package.json`
   - Check build logs for specific errors

### Debug Steps

1. **Check build logs** in Netlify/Railway dashboards
2. **Test API endpoints** directly in browser
3. **Verify file paths** and static file serving
4. **Check browser console** for JavaScript errors

## Cost Optimization

### Free Tier Limits

**Netlify Free:**
- 100GB bandwidth/month
- 300 build minutes/month
- 1 concurrent build

**Railway Free:**
- $5 usage credit/month
- 500 hours runtime
- 1GB RAM, shared CPU

### Optimization Tips

1. **Enable Netlify caching** for static assets
2. **Use Railway sleep mode** for development
3. **Optimize image sizes** and corpus files
4. **Monitor usage** in both dashboards

## Next Steps

After successful deployment:

1. **Set up monitoring** and alerts
2. **Configure custom domains**
3. **Set up staging environments**
4. **Implement CI/CD pipelines**
5. **Add performance monitoring**