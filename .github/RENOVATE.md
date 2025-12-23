# Renovate Bot Configuration

This repository uses [Renovate Bot](https://docs.renovatebot.com/) to automatically keep dependencies up-to-date.

## Overview

Renovate automatically:
- Detects outdated dependencies
- Creates pull requests for updates
- Groups related updates together
- Prioritizes security updates
- Auto-merges safe updates (minor/patch versions)

## Configuration

The main configuration is in [`renovate.json`](../renovate.json) at the repository root.

### Key Settings

- **Schedule**: Runs every 6 hours, preferring off-peak times (nights and weekends)
- **Rate Limiting**: Maximum 5 concurrent PRs, 2 per hour
- **Automerge**: Enabled for minor and patch updates
- **Dependency Dashboard**: Provides an overview of all pending updates
- **Security Updates**: Processed immediately, not subject to scheduling

### Package Rules

1. **Python Dependencies** (backend)
   - Minor/patch: Auto-grouped and auto-merged
   - Major: Separate PRs, manual review

2. **npm Dependencies** (frontend)
   - Minor/patch: Auto-grouped and auto-merged
   - Major: Separate PRs, manual review

3. **Docker Images**
   - Patch: Auto-merged
   - Minor/major: Manual review

4. **GitHub Actions**
   - All: Auto-grouped and auto-merged

## Workflow

The Renovate workflow (`.github/workflows/renovate.yml`) runs on:
- Schedule: Every 6 hours
- Manual trigger: Via workflow dispatch
- Config changes: When `renovate.json` is modified

## Dependency Dashboard

Renovate creates a "Dependency Dashboard" issue that shows:
- All detected dependencies
- Pending updates
- Rate-limited PRs
- Errored updates

Look for an issue titled "Dependency Dashboard" in the Issues tab.

## Disabling Renovate

To temporarily disable Renovate:

1. Add to `renovate.json`:
   ```json
   {
     "enabled": false
   }
   ```

2. Or close the Dependency Dashboard issue

## Security Updates

Security updates are:
- Processed immediately (not subject to schedule)
- Labeled with "security"
- Never auto-merged (require manual review)
- Created as separate PRs

## Customization

To modify Renovate's behavior, edit `renovate.json`. Common customizations:

### Change Schedule

```json
{
  "schedule": ["before 5am on monday"]
}
```

### Disable Automerge

```json
{
  "packageRules": [
    {
      "matchManagers": ["pip_requirements", "npm"],
      "automerge": false
    }
  ]
}
```

### Add More Reviewers

```json
{
  "reviewers": ["username1", "username2"]
}
```

## Troubleshooting

### Renovate Not Running

1. Check workflow runs in Actions tab
2. Verify `GITHUB_TOKEN` has required permissions
3. Check if rate limits are exceeded

### Too Many PRs

Adjust rate limiting:

```json
{
  "prConcurrentLimit": 2,
  "prHourlyLimit": 1
}
```

### Renovate Stuck

1. Close and reopen the Dependency Dashboard issue
2. Manually trigger the workflow
3. Check logs in Actions tab

## Resources

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Preset Configs](https://docs.renovatebot.com/presets/)
