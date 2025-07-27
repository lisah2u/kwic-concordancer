/**
 * Concordancer Frontend JavaScript
 * Handles search functionality and KWIC rendering
 */

// Configuration - detect environment for API base URL
const API_BASE_URL = getApiBaseUrl();

/**
 * Get the appropriate API base URL based on environment
 */
function getApiBaseUrl() {
    // Check if we're running on localhost (development)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return '';  // Use relative URLs for local development
    }
    
    // Production: frontend on Netlify, backend on Railway
    return 'https://kwic-concordancer-production.up.railway.app';
}

// DOM Elements
const corpusSelect = document.getElementById('corpus');
const viewFileBtn = document.getElementById('viewFileBtn');
const searchSection = document.getElementById('searchSection');
const fileSearchQuery = document.getElementById('fileSearchQuery');
const caseSensitive = document.getElementById('caseSensitive');
const searchFileBtn = document.getElementById('searchFileBtn');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const noResults = document.getElementById('noResults');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// File Viewer Elements
const fileViewerSection = document.getElementById('fileViewerSection');
const fileStats = document.getElementById('fileStats');
const fileName = document.getElementById('fileName');
const fileContent = document.getElementById('fileContent');
const fileSearchResults = document.getElementById('fileSearchResults');
const fileSearchStats = document.getElementById('fileSearchStats');
const fileSearchTable = document.getElementById('fileSearchTable');

// State management
let currentCorpus = null;

/**
 * Initialize the application
 */
async function init() {
    await loadCorpora();
    setupEventListeners();
}

/**
 * Load available corpora from the API
 */
async function loadCorpora() {
    try {
        const response = await fetch(`${API_BASE_URL}/corpora`);
        const data = await response.json();
        
        corpusSelect.innerHTML = '';
        
        if (data.corpora && data.corpora.length > 0) {
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select a corpus to view...';
            corpusSelect.appendChild(defaultOption);
            
            // Add corpus options
            data.corpora.forEach(corpus => {
                const option = document.createElement('option');
                option.value = corpus;
                option.textContent = formatCorpusName(corpus);
                corpusSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No corpora available';
            corpusSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading corpora:', error);
        corpusSelect.innerHTML = '<option value="">Error loading corpora</option>';
    }
}

/**
 * Format corpus name for display
 */
function formatCorpusName(corpusName) {
    return corpusName
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Corpus selection changes
    corpusSelect.addEventListener('change', handleCorpusChange);
    
    // File viewing
    viewFileBtn.addEventListener('click', handleViewFile);
    
    // File search functionality
    searchFileBtn.addEventListener('click', handleSearchInFile);
    clearSearchBtn.addEventListener('click', handleClearSearch);

    // Enable search on Enter in file search input
    fileSearchQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSearchInFile();
        }
    });
}

/**
 * Handle corpus selection change
 */
function handleCorpusChange() {
    const selectedCorpus = corpusSelect.value;
    currentCorpus = selectedCorpus;
    
    console.log('Corpus selected:', selectedCorpus); // Debug log
    
    if (selectedCorpus) {
        viewFileBtn.disabled = false;
    } else {
        viewFileBtn.disabled = true;
        hideAllSections();
        searchSection.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    hideMessages();
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

/**
 * Hide all message sections
 */
function hideMessages() {
    resultsSection.classList.add('hidden');
    noResults.classList.add('hidden');
    errorMessage.classList.add('hidden');
}



/**
 * Handle file viewing
 */
async function handleViewFile() {
    console.log('handleViewFile called, currentCorpus:', currentCorpus); // Debug log
    
    if (!currentCorpus) {
        showError('Please select a corpus first');
        return;
    }
    
    try {
        hideAllSections();
        
        const url = `${API_BASE_URL}/view/${encodeURIComponent(currentCorpus)}`;
        console.log('Fetching URL:', url); // Debug log
        
        const response = await fetch(url);
        
        console.log('Response status:', response.status); // Debug log
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load file');
        }
        
        const data = await response.json();
        displayFileContent(data);
        
        // Show search section after file is loaded
        searchSection.classList.remove('hidden');
        
    } catch (error) {
        console.error('File view error:', error);
        showError(error.message);
    }
}

/**
 * Handle search within file
 */
async function handleSearchInFile() {
    if (!currentCorpus) {
        showError('Please select and view a file first');
        return;
    }
    
    const query = fileSearchQuery.value.trim();
    const isCaseSensitive = caseSensitive.checked;
    
    if (!query) {
        showError('Please enter a search term');
        return;
    }
    
    try {
        hideAllSections();
        
        const response = await fetch(
            `${API_BASE_URL}/search-in-file/${encodeURIComponent(currentCorpus)}?query=${encodeURIComponent(query)}&case_sensitive=${isCaseSensitive}`
        );
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Search failed');
        }
        
        const data = await response.json();
        displayFileSearchResults(data);
        
    } catch (error) {
        console.error('File search error:', error);
        showError(error.message);
    }
}

/**
 * Handle clear search - return to file view
 */
async function handleClearSearch() {
    if (!currentCorpus) {
        return;
    }
    
    // Clear search input
    fileSearchQuery.value = '';
    
    // Hide search results and show file content again
    try {
        hideAllSections();
        
        const response = await fetch(`${API_BASE_URL}/view/${encodeURIComponent(currentCorpus)}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load file');
        }
        
        const data = await response.json();
        displayFileContent(data);
        
    } catch (error) {
        console.error('File view error:', error);
        showError(error.message);
    }
}

/**
 * Display file content
 */
function displayFileContent(data) {
    fileName.textContent = data.filename;
    fileStats.textContent = `${data.line_count} lines, ${data.word_count} words, ${data.char_count} characters`;
    
    // Display content with line numbers
    const lines = data.content.split('\n');
    const numberedContent = lines.map((line, index) => {
        const lineNum = (index + 1).toString().padStart(4, ' ');
        return `<span class="line-number">${lineNum}</span> ${escapeHtml(line)}`;
    }).join('\n');
    
    fileContent.innerHTML = numberedContent;
    fileViewerSection.classList.remove('hidden');
}

/**
 * Display file search results
 */
function displayFileSearchResults(data) {
    fileSearchStats.textContent = `${data.total_lines_matched} lines matched, ${data.total_matches} total matches for "${data.query}"`;
    
    // Clear and populate results table
    fileSearchTable.innerHTML = '';
    
    if (data.results && data.results.length > 0) {
        data.results.forEach(result => {
            const row = createFileSearchRow(result, data.query, data.case_sensitive);
            fileSearchTable.appendChild(row);
        });
        
        fileSearchResults.classList.remove('hidden');
    } else {
        noResults.classList.remove('hidden');
    }
}

/**
 * Create a table row for file search result in KWIC format
 */
function createFileSearchRow(result, query, caseSensitive) {
    const row = document.createElement('tr');
    row.className = 'kwic-row';
    
    // Extract KWIC contexts
    const kwicContexts = extractKWICContexts(result.content, query, caseSensitive);
    
    // Create a row for each match in the line
    const firstMatch = kwicContexts[0] || { left: '', match: query, right: result.content };
    
    // Line number
    const lineCell = document.createElement('td');
    lineCell.className = 'kwic-line px-3 py-3';
    lineCell.textContent = result.line_number;
    
    // Left context
    const leftCell = document.createElement('td');
    leftCell.className = 'kwic-left px-6 py-3';
    leftCell.textContent = firstMatch.left;
    
    // Match (search term)
    const matchCell = document.createElement('td');
    matchCell.className = 'kwic-match px-4 py-3';
    matchCell.textContent = firstMatch.match;
    
    // Right context
    const rightCell = document.createElement('td');
    rightCell.className = 'kwic-right px-6 py-3';
    rightCell.textContent = firstMatch.right;
    
    row.appendChild(lineCell);
    row.appendChild(leftCell);
    row.appendChild(matchCell);
    row.appendChild(rightCell);
    
    return row;
}

/**
 * Extract KWIC contexts from a line of text
 */
function extractKWICContexts(text, query, caseSensitive, contextSize = 5) {
    const contexts = [];
    const searchQuery = caseSensitive ? query : query.toLowerCase();
    const searchText = caseSensitive ? text : text.toLowerCase();
    
    // Split text into words while preserving positions
    const words = text.split(/\s+/);
    const lowerWords = words.map(w => w.toLowerCase());
    
    // Find all matches
    for (let i = 0; i < words.length; i++) {
        const word = caseSensitive ? words[i] : lowerWords[i];
        
        if (word.includes(searchQuery)) {
            // Calculate context boundaries
            const leftStart = Math.max(0, i - contextSize);
            const rightEnd = Math.min(words.length, i + 1 + contextSize);
            
            const leftContext = words.slice(leftStart, i).join(' ');
            const match = words[i];
            const rightContext = words.slice(i + 1, rightEnd).join(' ');
            
            contexts.push({
                left: leftContext,
                match: match,
                right: rightContext
            });
        }
    }
    
    // If no matches found, return the whole line as right context
    if (contexts.length === 0) {
        contexts.push({
            left: '',
            match: query,
            right: text
        });
    }
    
    return contexts;
}

/**
 * Highlight search matches in text
 */
function highlightMatches(text, query, caseSensitive) {
    if (!query) return escapeHtml(text);
    
    const escapedText = escapeHtml(text);
    const flags = caseSensitive ? 'g' : 'gi';
    const escapedQuery = escapeRegex(query);
    const regex = new RegExp(escapedQuery, flags);
    
    return escapedText.replace(regex, '<span class="search-highlight">$&</span>');
}

/**
 * Escape HTML characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Escape regex special characters
 */
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Hide all content sections
 */
function hideAllSections() {
    noResults.classList.add('hidden');
    errorMessage.classList.add('hidden');
    fileViewerSection.classList.add('hidden');
    fileSearchResults.classList.add('hidden');
}

/**
 * Hide all message sections (original function, kept for compatibility)
 */
function hideMessages() {
    hideAllSections();
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', init);