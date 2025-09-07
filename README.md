# RuneScape Catalyst League Tasks Tracker

A comprehensive web application for tracking RuneScape Catalyst League tasks, built for GitHub Pages.

## 🌟 Features

- **📋 Task Organization**: Tasks automatically organized by tags (Skills, Quests, Bosses, etc.)
- **⭐ Favorites System**: Star your important tasks for quick access
- **✅ Progress Tracking**: Mark tasks as complete/incomplete with persistent storage
- **🔍 Smart Search**: Search across task names, descriptions, requirements, and tags
- **📱 Responsive Design**: Scales from mobile to ultra-wide displays
- **💾 Local Storage**: All progress saved in your browser

## 🚀 Live Demo

Visit the live site: [https://YOUR-USERNAME.github.io/rs-leagues-tasks](https://YOUR-USERNAME.github.io/rs-leagues-tasks)

## 📁 Project Structure

```
rs-leagues-tasks/
├── index.html              # Main webpage
├── styles.css              # Styling
├── script.js               # Core functionality
├── catalyst_league_tasks.json  # Task data (508 tasks)
├── catalyst_league_scraper.py  # Data scraper
├── img/                    # Area images
│   ├── Lumbridge.webp
│   ├── Varrock.webp
│   └── ... (30 area images)
└── README.md               # This file
```

## 🎮 How to Use

1. **Browse Tasks**: Tasks are organized by categories (Skills, Quests, Areas, etc.)
2. **Favorite Tasks**: Click the ☆ button to add tasks to your Favorites list
3. **Track Progress**: Click on tasks to expand details, then mark as complete
4. **Search**: Use the search bar to find specific tasks
5. **Filter**: Collapse/expand sections to focus on what matters

## 📊 Task Categories

- **⭐ Favorites**: Your starred tasks
- **🏷️ Tag-based Lists**: 
  - Skills (Mining, Fishing, Combat, etc.)
  - Activities (Quest, Boss, Diary, etc.)
  - Difficulty (Beginner, Intermediate, Advanced)
- **📝 No Tags**: Uncategorized tasks
- **✅ Completed**: All finished tasks

## 🛠️ Data Updates

To update task data:

1. Run the scraper: `python3 catalyst_league_scraper.py`
2. This generates fresh `catalyst_league_tasks.json` from the RuneScape wiki
3. Commit and push the updated JSON file

## 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/rs-leagues-tasks.git
cd rs-leagues-tasks

# Start local server
python3 -m http.server 8000

# Visit http://localhost:8000
```

## 📱 Responsive Breakpoints

- **Mobile** (< 768px): 1 column
- **Tablet** (768px - 1200px): 2+ columns  
- **Desktop** (> 1200px): 3+ columns
- **Ultra-wide** (> 2000px): 6+ columns

## 💾 Browser Storage

The application uses localStorage to persist:
- ✅ Completed tasks (`completedTasks`)
- ⭐ Favorite tasks (`favoriteTasks`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is open source. The task data is sourced from the [RuneScape Wiki](https://runescape.wiki/).

---

**Happy task hunting! 🎯**