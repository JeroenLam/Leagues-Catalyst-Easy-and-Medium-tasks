// Global variables
let allTasks = [];
let completedTasks = new Set();
let favoriteTasks = new Set();
let expandedTasks = new Set();

// DOM elements
const totalTasksSpan = document.getElementById('total-tasks');
const completedTasksSpan = document.getElementById('completed-tasks');
const totalPointsSpan = document.getElementById('total-points');
const searchInput = document.getElementById('search-input');
const resetBtn = document.getElementById('reset-btn');
const taskSections = document.getElementById('task-sections');

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    loadCompletedTasks();
    loadFavoriteTasks();
    loadJSONData();
    setupEventListeners();
});

// Load completed tasks from localStorage
function loadCompletedTasks() {
    const saved = localStorage.getItem('completedTasks');
    if (saved) {
        completedTasks = new Set(JSON.parse(saved));
    }
}

// Save completed tasks to localStorage
function saveCompletedTasks() {
    localStorage.setItem('completedTasks', JSON.stringify([...completedTasks]));
}

// Load favorite tasks from localStorage
function loadFavoriteTasks() {
    const saved = localStorage.getItem('favoriteTasks');
    if (saved) {
        favoriteTasks = new Set(JSON.parse(saved));
    }
}

// Save favorite tasks to localStorage
function saveFavoriteTasks() {
    localStorage.setItem('favoriteTasks', JSON.stringify([...favoriteTasks]));
}

// Setup event listeners
function setupEventListeners() {
    searchInput.addEventListener('input', handleSearch);
    resetBtn.addEventListener('click', handleReset);
}

// Load and parse JSON data
async function loadJSONData() {
    try {
        // First try to fetch JSON file
        try {
            const response = await fetch('catalyst_league_tasks.json');
            const jsonData = await response.json();
            allTasks = parseJSONTasks(jsonData.tasks);
        } catch (jsonError) {
            console.log('JSON file not found, falling back to CSV...');
            // Fallback to CSV if JSON doesn't exist
            const response = await fetch('catalyst_league_tasks.csv');
            const csvText = await response.text();
            allTasks = parseCSV(csvText);
        }
        renderTasks();
        updateStats();
    } catch (error) {
        console.error('Error loading task data:', error);
        showError('Failed to load task data');
    }
}

// Parse JSON tasks into the format expected by the application
function parseJSONTasks(tasks) {
    return tasks.map((task, index) => ({
        id: index, // Use array index as unique ID
        area: task.Area || '',
        task: task.Task || '',
        information: task.Information || '',
        requirements: task.Requirements || '',
        pts: parseInt(task.Pts) || 0,
        tags: Array.isArray(task.Tags) ? task.Tags :
            (task.Tags && typeof task.Tags === 'string' && task.Tags.trim()) ?
                task.Tags.split(';').map(tag => tag.trim()).filter(tag => tag) : []
    }));
}

// Parse CSV text into task objects (fallback method)
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    const tasks = [];

    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const values = parseCSVLine(line);
        if (values.length >= 6) {
            const task = {
                id: i - 1, // Use line number as unique ID
                area: values[0],
                task: values[1],
                information: values[2],
                requirements: values[3],
                pts: parseInt(values[4]) || 0,
                tags: values[5] ? values[5].split(';').map(tag => tag.trim()).filter(tag => tag) : []
            };
            tasks.push(task);
        }
    }

    return tasks;
}

// Parse a single CSV line handling quoted values (fallback method)
function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            values.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }

    values.push(current.trim());
    return values;
}

// Render all tasks organized by tags
function renderTasks() {
    const tasksByTag = organizeTasksByTags();

    // Clear existing content
    taskSections.innerHTML = '';

    // Create favorites section first (only if it has tasks)
    if (tasksByTag['favorites'] && tasksByTag['favorites'].length > 0) {
        createFavoritesSection(tasksByTag['favorites']);
    }

    // Render tagged tasks (excluding special categories and only if they have tasks)
    const sortedTags = Object.keys(tasksByTag)
        .filter(tag => !['', 'completed', 'favorites'].includes(tag))
        .filter(tag => tasksByTag[tag] && tasksByTag[tag].length > 0)
        .sort();

    sortedTags.forEach(tag => {
        createTagSection(tag, tasksByTag[tag]);
    });

    // Add No Tags section (only if it has tasks)
    if (tasksByTag[''] && tasksByTag[''].length > 0) {
        createNoTagsSection(tasksByTag['']);
    }

    // Add Completed section last (only if it has tasks)
    if (tasksByTag['completed'] && tasksByTag['completed'].length > 0) {
        createCompletedSection(tasksByTag['completed']);
    }

    // Update section visibility and counts
    updateSectionCounts();

    // Distribute sections across columns
    distributeSectionsAcrossColumns();
}

// Organize tasks by their tags
function organizeTasksByTags() {
    const tasksByTag = { '': [], 'favorites': [], 'completed': [] };

    allTasks.forEach(task => {
        // Handle completed tasks
        if (completedTasks.has(task.id)) {
            tasksByTag['completed'].push(task);
            return;
        }

        // Handle favorite tasks
        if (favoriteTasks.has(task.id)) {
            tasksByTag['favorites'].push(task);
        }

        // Handle tagged and untagged tasks (favorites can appear in multiple lists)
        if (task.tags.length === 0) {
            tasksByTag[''].push(task);
        } else {
            task.tags.forEach(tag => {
                if (!tasksByTag[tag]) tasksByTag[tag] = [];
                tasksByTag[tag].push(task);
            });
        }
    });

    return tasksByTag;
}

// Create a new tag section
function createTagSection(tagName, tasks) {
    const section = document.createElement('section');
    section.className = 'task-category';
    section.innerHTML = `
        <h2 class="category-title">
            <span class="toggle-icon">▼</span>
            ${tagName}
            <span class="task-count">(${tasks.length})</span>
        </h2>
        <div class="task-list" id="${tagName.toLowerCase().replace(/\s+/g, '-')}-list"></div>
    `;

    taskSections.appendChild(section);

    // Add click listener for collapsing
    const title = section.querySelector('.category-title');
    title.addEventListener('click', () => toggleSection(section));

    // Render tasks in this section
    renderTaskSection(`${tagName.toLowerCase().replace(/\s+/g, '-')}-list`, tasks, tagName);
}

// Render tasks in a specific section
function renderTaskSection(containerId, tasks, sectionName) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = '<div class="empty-state">No tasks in this category</div>';
        return;
    }

    container.innerHTML = tasks.map(task => createTaskHTML(task)).join('');

    // Add event listeners to task items
    tasks.forEach(task => {
        const taskElement = container.querySelector(`[data-task-id="${task.id}"]`);
        if (taskElement) {
            setupTaskEventListeners(taskElement, task);
        }
    });
}

// Create HTML for a single task
function createTaskHTML(task) {
    const isCompleted = completedTasks.has(task.id);
    const isFavorite = favoriteTasks.has(task.id);
    const isExpanded = expandedTasks.has(task.id);
    const areaImage = getAreaImage(task.area);

    return `
        <div class="task-item ${isExpanded ? 'expanded' : ''}" data-task-id="${task.id}">
            <div class="task-header">
                <img src="${areaImage}" alt="${task.area}" class="area-image" onerror="this.src='img/Global.webp'">
                <div class="task-summary">
                    <div class="task-title">${escapeHtml(task.task)}</div>
                    <div class="task-points">${task.pts} points</div>
                </div>
                <div class="task-status">
                    <button class="favorite-button ${isFavorite ? 'favorited' : ''}" data-task-id="${task.id}" title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                        ${isFavorite ? '★' : '☆'}
                    </button>
                    <span class="expand-icon">▼</span>
                </div>
            </div>
            <div class="task-details">
                <div class="task-details-content">
                    <div class="detail-section">
                        <div class="detail-label">Information:</div>
                        <div class="detail-text">${escapeHtml(task.information)}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">Requirements:</div>
                        <div class="detail-text">${escapeHtml(task.requirements)}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">Points:</div>
                        <div class="detail-text">${task.pts}</div>
                    </div>
                    ${task.tags.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-label">Tags:</div>
                        <div class="detail-text">${task.tags.join(', ')}</div>
                    </div>
                    ` : ''}
                    <div class="task-buttons">
                        ${isCompleted ? `
                            <button class="uncomplete-button" data-task-id="${task.id}">
                                Mark as Incomplete
                            </button>
                        ` : `
                            <button class="complete-button" data-task-id="${task.id}">
                                Mark as Complete
                            </button>
                        `}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Setup event listeners for a task element
function setupTaskEventListeners(taskElement, task) {
    const header = taskElement.querySelector('.task-header');
    const completeBtn = taskElement.querySelector('.complete-button');
    const uncompleteBtn = taskElement.querySelector('.uncomplete-button');
    const favoriteBtn = taskElement.querySelector('.favorite-button');

    header.addEventListener('click', (e) => {
        // Don't expand if clicking on buttons
        if (e.target.closest('.favorite-button')) return;
        toggleSpecificTaskExpansion(taskElement, task.id);
    });

    if (completeBtn) {
        completeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            markTaskComplete(task.id);
        });
    }

    if (uncompleteBtn) {
        uncompleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            markTaskIncomplete(task.id);
        });
    }

    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleTaskFavorite(task.id);
        });
    }
}

// Get the appropriate image path for an area
function getAreaImage(area) {
    const areaMap = {
        'Lumbridge': 'img/Lumbridge.webp',
        'Draynor': 'img/Draynor.webp',
        'Edgeville': 'img/Edgevile.webp',
        'Fort': 'img/Fort.webp',
        'Varrock': 'img/Varrock.webp',
        'Global': 'img/Global.webp',
        'Burthorpe': 'img/Burthorpe.webp',
        'Falador': 'img/Falador.webp',
        'PortSarim': 'img/Portsarim.webp',
        'Taverley': 'img/Taverly.webp',
        'Menaphos': 'img/Menephos.webp',
        'AlKharid': 'img/Alkharid.webp',
        'Sophanem': 'img/Sophanem.webp',
        'Desert': 'img/Desert.webp',
        'Lunar': 'img/Lunar.webp',
        'Fremennik': 'img/Frenebbik.webp',
        'Gnomes': 'img/Gnomes.webp',
        'Feldip': 'img/Feldip.webp',
        'Ardougne': 'img/Ardougne.webp',
        'Seer': 'img/Seers.webp',
        'Piscatorius': 'img/Piscatorius.webp',
        'Yanille': 'img/Yanille.webp',
        'Anachronia': 'img/Anachronia.webp',
        'elves': 'img/Elven.webp',
        'Karamja': 'img/Karamja.webp',
        'Wilderness': 'img/Wilderness.webp',
        'Daemonheim': 'img/Demonheim.webp',
        'Morytania': 'img/Morytania.webp',
        'Um': 'img/Um.webp'
    };

    return areaMap[area] || 'img/Global.webp';
}

// Toggle task expansion for a specific element
function toggleSpecificTaskExpansion(taskElement, taskId) {
    const isCurrentlyExpanded = taskElement.classList.contains('expanded');

    if (isCurrentlyExpanded) {
        taskElement.classList.remove('expanded');
        expandedTasks.delete(taskId);
    } else {
        taskElement.classList.add('expanded');
        expandedTasks.add(taskId);
    }
}

// Toggle task expansion (for backward compatibility)
function toggleTaskExpansion(taskId) {
    if (expandedTasks.has(taskId)) {
        expandedTasks.delete(taskId);
    } else {
        expandedTasks.add(taskId);
    }

    const taskElements = document.querySelectorAll(`[data-task-id="${taskId}"]`);
    taskElements.forEach(element => {
        element.classList.toggle('expanded');
    });
}

// Mark a task as complete
function markTaskComplete(taskId) {
    completedTasks.add(taskId);
    saveCompletedTasks();
    renderTasks();
    updateStats();
}

// Mark a task as incomplete
function markTaskIncomplete(taskId) {
    completedTasks.delete(taskId);
    saveCompletedTasks();
    renderTasks();
    updateStats();
}

// Toggle task favorite status
function toggleTaskFavorite(taskId) {
    if (favoriteTasks.has(taskId)) {
        favoriteTasks.delete(taskId);
    } else {
        favoriteTasks.add(taskId);
    }
    saveFavoriteTasks();
    renderTasks();
}

// Create favorites section
function createFavoritesSection(tasks) {
    const section = document.createElement('section');
    section.className = 'task-category favorites-section';
    section.innerHTML = `
        <h2 class="category-title">
            <span class="toggle-icon">▼</span>
            ★ Favorites
            <span class="task-count">(${tasks.length})</span>
        </h2>
        <div class="task-list" id="favorites-list"></div>
    `;

    taskSections.appendChild(section);

    // Add click listener for collapsing
    const title = section.querySelector('.category-title');
    title.addEventListener('click', () => toggleSection(section));

    // Render tasks in this section
    renderTaskSection('favorites-list', tasks, 'Favorites');
}

// Create no tags section
function createNoTagsSection(tasks) {
    const section = document.createElement('section');
    section.className = 'task-category no-tags-section';
    section.innerHTML = `
        <h2 class="category-title">
            <span class="toggle-icon">▼</span>
            No Tags
            <span class="task-count">(${tasks.length})</span>
        </h2>
        <div class="task-list" id="no-tags-list-new"></div>
    `;

    taskSections.appendChild(section);

    // Add click listener for collapsing
    const title = section.querySelector('.category-title');
    title.addEventListener('click', () => toggleSection(section));

    // Render tasks in this section
    renderTaskSection('no-tags-list-new', tasks, 'No Tags');
}

// Create completed section
function createCompletedSection(tasks) {
    const section = document.createElement('section');
    section.className = 'task-category completed-section';
    section.innerHTML = `
        <h2 class="category-title">
            <span class="toggle-icon">▼</span>
            Completed
            <span class="task-count">(${tasks.length})</span>
        </h2>
        <div class="task-list" id="completed-list-new"></div>
    `;

    taskSections.appendChild(section);

    // Add click listener for collapsing
    const title = section.querySelector('.category-title');
    title.addEventListener('click', () => toggleSection(section));

    // Render tasks in this section
    renderTaskSection('completed-list-new', tasks, 'Completed');
}

// Distribute sections across columns
function distributeSectionsAcrossColumns() {
    const sections = document.querySelectorAll('.task-category');
    const totalSections = sections.length;

    // Calculate sections per column (try to distribute evenly)
    const columnsCount = getColumnsCount();
    const sectionsPerColumn = Math.ceil(totalSections / columnsCount);

    sections.forEach((section, index) => {
        const columnIndex = Math.floor(index / sectionsPerColumn);
        section.style.order = columnIndex;
    });
}

// Get number of columns based on screen size
function getColumnsCount() {
    const width = window.innerWidth;
    if (width < 768) return 1;
    if (width < 1200) return 2;
    return 3;
}

// Setup collapse listeners for existing sections
function setupCollapseListeners() {
    // Add window resize listener for responsive columns
    window.addEventListener('resize', distributeSectionsAcrossColumns);
}

// Toggle section collapse
function toggleSection(section) {
    section.classList.toggle('collapsed');
}

// Handle search functionality
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const taskItems = document.querySelectorAll('.task-item');

    taskItems.forEach(item => {
        const taskId = parseInt(item.dataset.taskId);
        const task = allTasks.find(t => t.id === taskId);

        if (!task) {
            item.classList.add('hidden');
            return;
        }

        const searchableText = [
            task.task,
            task.information,
            task.requirements,
            task.area,
            ...task.tags
        ].join(' ').toLowerCase();

        if (searchTerm === '' || searchableText.includes(searchTerm)) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });

    updateSectionCounts();
}

// Handle reset functionality
function handleReset() {
    if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
        completedTasks.clear();
        favoriteTasks.clear();
        expandedTasks.clear();
        localStorage.removeItem('completedTasks');
        localStorage.removeItem('favoriteTasks');
        renderTasks();
        updateStats();
    }
}

// Update statistics
function updateStats() {
    const total = allTasks.length;
    const completed = completedTasks.size;
    const totalPoints = allTasks.reduce((sum, task) => sum + task.pts, 0);
    const completedPoints = allTasks
        .filter(task => completedTasks.has(task.id))
        .reduce((sum, task) => sum + task.pts, 0);

    totalTasksSpan.textContent = total;
    completedTasksSpan.textContent = completed;
    totalPointsSpan.textContent = `${completedPoints}/${totalPoints}`;
}

// Update section counts based on visible tasks
function updateSectionCounts() {
    const sections = document.querySelectorAll('.task-category');

    sections.forEach(section => {
        const taskList = section.querySelector('.task-list');
        const visibleTasks = taskList.querySelectorAll('.task-item:not(.hidden)');
        const countSpan = section.querySelector('.task-count');

        if (countSpan) {
            countSpan.textContent = `(${visibleTasks.length})`;
        }

        // Hide sections with no visible tasks during search
        const searchTerm = searchInput.value.toLowerCase().trim();
        if (searchTerm && visibleTasks.length === 0) {
            section.style.display = 'none';
        } else {
            section.style.display = 'block';
        }
    });
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show error message
function showError(message) {
    const main = document.querySelector('main');
    main.innerHTML = `
        <div class="loading">
            <h2>Error</h2>
            <p>${message}</p>
            <button onclick="location.reload()">Retry</button>
        </div>
    `;
}