# Quick Reference: Backend Deployment

This is a condensed guide for quick backend deployment. For detailed instructions, see [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md).

## ⚡ Fastest Way to Deploy (Railway)

1. **Sign up**: Go to [railway.app](https://railway.app) and sign in with GitHub
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select repo**: Choose `DevSecNinja/ha-discover`
4. **Configure**: 
   - Set root directory to `backend`
   - Railway auto-detects `railway.toml`
5. **Deploy**: Railway builds and deploys automatically
6. **Get URL**: Copy your Railway URL (e.g., `https://ha-discover-api-production.up.railway.app`)

## 🔗 Connect Frontend to Backend

After deploying backend, configure the frontend:

### Method 1: GitHub Secret (Recommended)

```bash
# Go to: https://github.com/DevSecNinja/ha-discover/settings/secrets/actions
# Click "New repository secret"
# Name: API_URL
# Value: https://your-backend-url.com/api/v1
# Save and trigger deployment
```

### Method 2: Direct Edit

Edit `.github/workflows/deploy.yml` line 78:

```yaml
NEXT_PUBLIC_API_URL: https://your-backend-url.railway.app/api/v1
```

Then push to trigger deployment.

## ✅ Verify Deployment

```bash
# Test backend health
curl https://your-backend-url.com/api/v1/health
# Should return: {"status":"ok"}

# Open API docs
open https://your-backend-url.com/docs

# Check frontend
open https://devsecninja.github.io/ha-discover/
```

## 🐛 Common Issues

### Frontend can't connect to backend

1. **Check API URL**: Verify `NEXT_PUBLIC_API_URL` is correct in workflow
2. **Check CORS**: Backend allows `https://devsecninja.github.io`
3. **Check backend**: Ensure it's running and accessible
4. **Rebuild frontend**: Push to `main` to trigger new deployment

### Backend deployment fails

1. **Check logs**: View deployment logs in your platform dashboard
2. **Check Python version**: Should be 3.12+
3. **Check requirements**: Ensure all dependencies install correctly

### GitHub Actions fails

1. **Check secrets**: Ensure `API_URL` secret is set if using that method
2. **Check workflow**: Verify no syntax errors in `.github/workflows/deploy.yml`
3. **Check backend tests**: Tests must pass before deployment

## 📚 Full Documentation

- [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) - Comprehensive deployment guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Frontend deployment guide
- [README.md](./README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design

## 🆘 Need Help?

Open an issue on GitHub: https://github.com/DevSecNinja/ha-discover/issues
