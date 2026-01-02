# Deployment Guide

This document describes the deployment process for hadiscover, including Docker images and GitHub Pages.

## Overview

The deployment process is triggered when a version tag (e.g., `v1.2.3`) is pushed to the repository. The release workflow performs the following steps:

1. **Test**: Run backend tests to ensure code quality
2. **Build & Push**: Build and push Docker images for backend and frontend to GitHub Container Registry
3. **Security Scan**: Scan Docker images for vulnerabilities
4. **Create Release**: Create a GitHub release with release notes
5. **Build Pages**: Build the frontend for static GitHub Pages deployment
6. **Deploy Pages**: Deploy to GitHub Pages (requires manual approval)

## GitHub Pages Deployment with Approval

### Why Manual Approval?

GitHub Pages deployment requires manual approval to ensure:
- Backend API changes are deployed and ready before frontend deployment
- Coordinated upgrades that require both backend and frontend changes
- Time to verify backend deployment health before exposing users to new frontend
- Ability to review release notes and deployment plan before going live

### Setting Up Environment Protection

To enable manual approval for GitHub Pages deployment, configure the `github-pages` environment:

1. Go to your repository settings on GitHub
2. Navigate to **Settings** → **Environments**
3. Select or create the `github-pages` environment
4. Enable **Required reviewers**:
   - Add team members or maintainers who should approve deployments
   - Recommended: At least 1-2 reviewers with deployment permissions
5. (Optional) Configure **Deployment branches** to restrict which branches can deploy
6. Save the environment configuration

### Deployment Workflow

When a release tag is pushed:

1. The release workflow runs automatically (test, build, scan, release creation)
2. After the release is created, the `build-pages` job builds the frontend
3. The `deploy-pages` job waits for manual approval
4. **Required reviewers receive a notification** to approve the deployment
5. Once approved, GitHub Pages is deployed with the new frontend build
6. The deployment URL is available in the workflow output

### Approving a Deployment

When you receive a deployment approval request:

1. Go to the **Actions** tab in the repository
2. Click on the running **Release** workflow
3. Review the workflow progress and ensure:
   - All tests passed
   - Docker images built successfully
   - Security scans completed without critical issues
   - Backend API is deployed and healthy (verify separately)
4. Click **Review deployments**
5. Select the `github-pages` environment
6. Add an optional comment (e.g., "Backend v1.2.3 deployed and verified")
7. Click **Approve and deploy**

### Emergency Deployments

For emergency situations (hotfixes, critical bugs), use the manual **Deploy to GitHub Pages (Emergency Only)** workflow:

1. Go to **Actions** tab
2. Select **Deploy to GitHub Pages (Emergency Only)** workflow
3. Click **Run workflow**
4. Select the branch to deploy
5. Click **Run workflow**

**Important**: Emergency deployments bypass the normal release coordination. Ensure the backend API is ready before deploying.

## Docker Image Deployment

Docker images are automatically built and pushed to GitHub Container Registry (GHCR) during the release workflow:

- **Backend**: `ghcr.io/devsecninja/hadiscover/backend:VERSION`
- **Frontend**: `ghcr.io/devsecninja/hadiscover/frontend:VERSION`

Tags include:
- Full version: `1.2.3`
- Major.minor: `1.2`
- Major: `1`
- `latest` (for stable releases only, not pre-releases)

### Deploying Docker Images

See the release notes for specific deployment instructions. Example:

```bash
# Pull the released images
docker pull ghcr.io/devsecninja/hadiscover/backend:1.2.3
docker pull ghcr.io/devsecninja/hadiscover/frontend:1.2.3

# Or use docker-compose with the version specified
docker-compose -f docker-compose.prod.yml up -d
```

## Release Process

### Creating a Release

1. Ensure all changes are merged to `main`
2. Create and push a version tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. The release workflow automatically triggers
4. Monitor the workflow progress in the Actions tab
5. Once the release is created, approve the GitHub Pages deployment

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- Pre-releases: `1.2.3-beta.1`, `1.2.3-rc.1`

### Rollback

If issues are discovered after deployment:

1. **Backend**: Deploy previous Docker image version
2. **Frontend**: 
   - Emergency: Use emergency deployment workflow with previous branch/commit
   - Proper: Create a new patch release with fixes

## Monitoring Deployments

### GitHub Actions

- View workflow runs in the **Actions** tab
- Check logs for any failures or warnings
- Review security scan results in **Security** → **Code scanning alerts**

### GitHub Pages

- Deployment URL: [https://hadiscover.com](https://hadiscover.com) (or your configured domain)
- Check deployment status in **Settings** → **Pages**
- View deployment history in **Deployments** page

### Docker Images

- View published packages in **Packages** section
- Check image vulnerability scan results
- Monitor image pull statistics

## Troubleshooting

### Deployment Stuck Waiting for Approval

- Check that the `github-pages` environment has required reviewers configured
- Ensure reviewers have appropriate permissions
- Check for pending approval notifications

### Build Failures

- Review the workflow logs in Actions tab
- Common issues:
  - Backend tests failing
  - Frontend build errors (check NEXT_PUBLIC_API_URL configuration)
  - Docker build issues

### GitHub Pages Not Updating

- Verify the deployment was approved and completed
- Check browser cache (hard refresh with Ctrl+Shift+R or Cmd+Shift+R)
- Verify the correct API_URL secret is configured
- Check if Pages is enabled in repository settings

## Support

For issues or questions about the deployment process:
- Open an issue in the repository
- Check existing documentation in README.md and ARCHITECTURE.md
- Review workflow files in `.github/workflows/`
