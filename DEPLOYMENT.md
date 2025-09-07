# GitHub Pages Deployment Guide

## 🚀 Quick Setup

### 1. Create Repository
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `rs-leagues-tasks` (or your preferred name)
3. Make it **public** (required for free GitHub Pages)

### 2. Upload Files
Upload all these files to your repository:
- [`index.html`](index.html) - Main webpage
- [`styles.css`](styles.css) - Styling
- [`script.js`](script.js) - JavaScript functionality  
- [`catalyst_league_tasks.json`](catalyst_league_tasks.json) - Task data
- [`_config.yml`](_config.yml) - Jekyll configuration
- [`README.md`](README.md) - Documentation
- [`img/`](img/) - All area images (30 .webp files)

### 3. Enable GitHub Pages
1. Go to repository **Settings**
2. Scroll to **Pages** section
3. Under **Source**, select **Deploy from a branch**
4. Choose **main** branch
5. Choose **/ (root)** folder
6. Click **Save**

### 4. Access Your Site
- Your site will be available at: `https://YOUR-USERNAME.github.io/REPOSITORY-NAME`
- It may take 5-10 minutes for initial deployment

## 📋 Pre-deployment Checklist

✅ **Required Files Present**
- [x] index.html (entry point)
- [x] styles.css (styling)
- [x] script.js (functionality)
- [x] catalyst_league_tasks.json (data)
- [x] img/ folder with all area images

✅ **GitHub Pages Configuration**
- [x] _config.yml (Jekyll config)
- [x] .gitignore (excludes unnecessary files)
- [x] README.md (documentation)

✅ **Path Verification**
- [x] All paths use relative references
- [x] No localhost or absolute URLs
- [x] Images reference `img/` folder correctly
- [x] JSON data loads via relative path

## 🔄 Updating Task Data

To refresh task data from the RuneScape wiki:

```bash
python3 catalyst_league_scraper.py
git add catalyst_league_tasks.json
git commit -m "Update task data"
git push
```

## 🐛 Troubleshooting

**Site not loading?**
- Ensure repository is public
- Check that GitHub Pages is enabled
- Verify main branch is selected

**Missing images?**
- Ensure all .webp files are uploaded to `img/` folder
- Check file names match exactly (case-sensitive)

**Data not loading?**
- Verify `catalyst_league_tasks.json` is present
- Check browser console for errors
- Ensure JSON format is valid

## 🌟 Features Working

Once deployed, users can:
- ⭐ Favorite important tasks
- ✅ Track completion progress  
- 🔍 Search through all tasks
- 📱 Use on any device
- 💾 Persistent progress storage

---

**Ready for GitHub Pages deployment! 🚀**