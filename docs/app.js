// ============================================================================
// BrowserOS Knowledge Hub - Interactive JavaScript
// Real semantic search with fuzzy matching and keyword scoring
// ============================================================================

// Configuration
const CONFIG = {
    SEARCH_DEBOUNCE_MS: 300,  // Configurable debounce delay for search input
    SEARCH_MIN_CHARS: 1,      // Minimum characters before triggering search
    SEARCH_MAX_RESULTS: 50    // Maximum number of results to display
};

// Global search index - loaded from search-index.json
let searchIndex = null;
let searchIndexLoaded = false;

// Initialize on page load with error boundary
document.addEventListener('DOMContentLoaded', function() {
    try {
        loadSearchIndex();
        initializeSearch();
        initializeNavigation();
        initializeAnimations();
        initializeMobileMenu();
        initializeCategoryNavigation();
        initializeCopyButtons();
    } catch (error) {
        console.error('Initialization error:', error);
        // Display user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: var(--error); color: white; padding: 1rem 1.5rem; border-radius: 8px; z-index: 9999; box-shadow: var(--shadow-lg);';
        errorDiv.textContent = 'An error occurred during page initialization. Some features may not work correctly.';
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
});

// ============================================================================
// Load Search Index
// ============================================================================

async function loadSearchIndex() {
    try {
        const response = await fetch('search-index.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        searchIndex = await response.json();
        searchIndexLoaded = true;
        console.log(`✅ Search index loaded: ${searchIndex.total_documents} documents`);
    } catch (error) {
        console.error('Failed to load search index:', error);
        searchIndexLoaded = false;
        
        // Display user-friendly error message
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'padding: 1rem; background: var(--bg-secondary, #1A1F26); border-radius: 8px; margin-top: 1rem;';
            
            const warningP = document.createElement('p');
            warningP.style.cssText = 'color: var(--warning, #F59E0B); font-weight: 600; margin-bottom: 0.5rem;';
            warningP.textContent = '⚠️ Search temporarily unavailable';
            
            const messageP = document.createElement('p');
            messageP.style.cssText = 'color: var(--text-secondary, #9AA0A6); font-size: 0.875rem;';
            messageP.textContent = 'Unable to load search index. Please try refreshing the page or browse the ';
            
            const workflowLink = document.createElement('a');
            workflowLink.href = '#workflows';
            workflowLink.style.color = 'var(--browseros-orange, #FF7900)';
            workflowLink.textContent = 'workflows';
            
            const directlyText = document.createTextNode(' directly.');
            
            messageP.appendChild(workflowLink);
            messageP.appendChild(directlyText);
            
            errorDiv.appendChild(warningP);
            errorDiv.appendChild(messageP);
            
            // Store for later display when user tries to search
            searchResults.dataset.errorMessage = errorDiv.outerHTML;
        }
    }
}

// ============================================================================
// Search Functionality
// ============================================================================

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    let currentFilter = 'all';
    
    // Handle search input
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase().trim();
            
            if (query.length >= CONFIG.SEARCH_MIN_CHARS) {
                performSearch(query, currentFilter);
            } else {
                searchResults.classList.remove('active');
                searchResults.replaceChildren(); // Safer than innerHTML = ''
            }
        }, CONFIG.SEARCH_DEBOUNCE_MS));
    }
    
    // Handle filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            
            // Re-run search if there's a query
            const query = searchInput.value.toLowerCase().trim();
            if (query.length > 0) {
                performSearch(query, currentFilter);
            }
        });
    });
}

function performSearch(query, filter) {
    const searchResults = document.getElementById('searchResults');
    
    if (!searchIndexLoaded || !searchIndex) {
        // Clear existing content safely
        searchResults.textContent = '';
        
        // Check if there's a stored error message
        if (searchResults.dataset.errorMessage) {
            // Create a temporary container and use it to safely parse the stored HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = searchResults.dataset.errorMessage;
            // Move the child element (the error div) to searchResults
            while (tempDiv.firstChild) {
                searchResults.appendChild(tempDiv.firstChild);
            }
            searchResults.classList.add('active');
            return;
        }
        
        // Build loading indicator with createElement (no innerHTML)
        // Note: Spinner animation relies on .loading-spinner class in styles.css (lines ~607-619)
        const loadingDiv = document.createElement('div');
        loadingDiv.style.textAlign = 'center';
        loadingDiv.style.padding = '2rem';
        loadingDiv.style.color = 'var(--text-secondary, #9AA0A6)';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        const message = document.createElement('p');
        message.textContent = '⏳ Loading search index...';
        
        loadingDiv.appendChild(spinner);
        loadingDiv.appendChild(message);
        searchResults.appendChild(loadingDiv);
        return;
    }
    
    let documents = searchIndex.documents;
    
    // Filter by category
    if (filter === 'workflows') {
        documents = documents.filter(doc => doc.category === 'Workflow');
    } else if (filter === 'usecases') {
        documents = documents.filter(doc => doc.category === 'Use Case');
    } else if (filter === 'docs') {
        documents = documents.filter(doc => 
            doc.category === 'Documentation' || 
            doc.category === 'Knowledge Base' || 
            doc.category === 'Advanced Guide'
        );
    }
    
    // Perform semantic search with scoring
    const results = documents.map(doc => {
        const score = calculateSearchScore(doc, query);
        return { ...doc, score };
    })
    .filter(doc => doc.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 20); // Top 20 results
    
    displaySearchResults(results, query);
}

function calculateSearchScore(doc, query) {
    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);
    
    let score = 0;
    
    // Exact title match (highest score)
    if (doc.title.toLowerCase() === queryLower) {
        score += 1000;
    }
    
    // Title contains query
    if (doc.title.toLowerCase().includes(queryLower)) {
        score += 500;
    }
    
    // Title word matches
    queryWords.forEach(word => {
        if (doc.title.toLowerCase().includes(word)) {
            score += 100;
        }
    });
    
    // Description matches
    if (doc.description && doc.description.toLowerCase().includes(queryLower)) {
        score += 200;
    }
    
    // Description word matches
    queryWords.forEach(word => {
        if (doc.description && doc.description.toLowerCase().includes(word)) {
            score += 50;
        }
    });
    
    // Keyword matches
    if (doc.keywords) {
        queryWords.forEach(word => {
            if (doc.keywords.some(k => k.includes(word) || word.includes(k))) {
                score += 75;
            }
        });
    }
    
    // Heading matches
    if (doc.headings) {
        queryWords.forEach(word => {
            doc.headings.forEach(heading => {
                if (heading.toLowerCase().includes(word)) {
                    score += 30;
                }
            });
        });
    }
    
    // Category match
    if (doc.category.toLowerCase().includes(queryLower)) {
        score += 40;
    }
    
    // Fuzzy match for typos (Levenshtein distance)
    queryWords.forEach(word => {
        if (word.length > 4) {
            const titleWords = doc.title.toLowerCase().split(/\s+/);
            titleWords.forEach(titleWord => {
                if (levenshteinDistance(word, titleWord) <= 2) {
                    score += 25;
                }
            });
        }
    });
    
    // Boost score for shorter documents (more focused content)
    if (doc.word_count < 500) {
        score *= 1.2;
    }
    
    return score;
}

function levenshteinDistance(str1, str2) {
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(0));
    
    for (let i = 0; i <= len1; i++) matrix[i][0] = i;
    for (let j = 0; j <= len2; j++) matrix[0][j] = j;
    
    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
            matrix[i][j] = Math.min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost
            );
        }
    }
    
    return matrix[len1][len2];
}

function displaySearchResults(results, query) {
    const searchResults = document.getElementById('searchResults');
    
    if (results.length === 0) {
        searchResults.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--gray-500, #6B7280);">
                <p>No results found for "<strong>${escapeHtml(query)}</strong>"</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Try different keywords or browse <a href="#workflows" style="color: var(--primary, #FF7900);">workflows</a> and <a href="#knowledge-base" style="color: var(--primary, #FF7900);">documentation</a></p>
            </div>
        `;
    } else {
        const resultsHTML = results.map(result => `
            <a href="${escapeHtml(result.url)}" class="search-result-item" style="display: block; padding: 1rem; border-bottom: 1px solid var(--gray-200, #E5E7EB); text-decoration: none; color: inherit; transition: background 0.2s;">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; flex-wrap: wrap;">
                            <span style="background: var(--primary, #FF7900); color: white; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">${escapeHtml(result.category)}</span>
                            ${result.score > 500 ? '<span style="background: var(--success, #10B981); color: white; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">⭐ Top Match</span>' : ''}
                        </div>
                        <h4 style="margin-bottom: 0.25rem; color: var(--gray-900, #111827); font-size: 1.125rem; font-weight: 600;">${highlightMatch(result.title, query)}</h4>
                        <p style="color: var(--gray-600, #4B5563); font-size: 0.875rem; line-height: 1.5;">${highlightMatch(result.description, query)}</p>
                        ${result.keywords && result.keywords.length > 0 ? `
                            <div style="display: flex; gap: 0.25rem; margin-top: 0.5rem; flex-wrap: wrap;">
                                ${result.keywords.slice(0, 5).map(kw => `
                                    <span style="background: var(--gray-100, #F3F4F6); color: var(--gray-600, #4B5563); padding: 0.125rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">${escapeHtml(kw)}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" style="flex-shrink: 0; color: var(--gray-400, #9CA3AF); margin-top: 0.25rem;">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                    </svg>
                </div>
            </a>
        `).join('');
        
        const relevanceNote = results.length > 5 ? 
            `<p style="font-size: 0.75rem; color: var(--gray-500, #6B7280); margin-top: 0.25rem;">Results ranked by relevance</p>` : '';
        
        searchResults.innerHTML = `
            <div style="margin-bottom: 1rem; padding: 0.5rem 1rem; background: var(--gray-50, #F9FAFB); border-radius: var(--radius-lg, 0.75rem);">
                <p style="color: var(--gray-600, #4B5563); font-size: 0.875rem; font-weight: 500;">Found <strong style="color: var(--primary, #FF7900);">${results.length}</strong> result${results.length !== 1 ? 's' : ''} for "<strong>${escapeHtml(query)}</strong>"</p>
                ${relevanceNote}
            </div>
            ${resultsHTML}
        `;
    }
    
    searchResults.classList.add('active');
    
    // Add hover effects
    document.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.background = 'var(--gray-50)';
            this.style.borderLeftWidth = '4px';
            this.style.borderLeftColor = 'var(--primary)';
            this.style.paddingLeft = 'calc(1rem - 3px)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.background = 'white';
            this.style.borderLeftWidth = '0';
            this.style.paddingLeft = '1rem';
        });
    });
}

function highlightMatch(text, query) {
    if (!query) return escapeHtml(text);
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark style="background: yellow; padding: 0 0.25rem; border-radius: 0.125rem;">$1</mark>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ============================================================================
// Navigation
// ============================================================================

function initializeNavigation() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 80; // Account for fixed navbar
                const targetPosition = target.offsetTop - offset;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Navbar scroll effect
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.style.boxShadow = 'var(--shadow-lg)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });
}

// ============================================================================
// Mobile Menu
// ============================================================================

function initializeMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
}

// ============================================================================
// Mobile Menu
// ============================================================================

function initializeMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', function() {
            // Toggle menu visibility
            navLinks.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
            
            // Update ARIA attributes
            const isExpanded = navLinks.classList.contains('active');
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
            
            // Prevent body scroll when menu is open
            document.body.style.overflow = isExpanded ? 'hidden' : '';
        });
        
        // Close menu when clicking nav links
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar') && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        });
        
        // Handle escape key to close menu
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
                mobileMenuToggle.focus(); // Return focus to toggle button
            }
        });
    }
}

// ============================================================================
// Animations
// ============================================================================

function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements
    document.querySelectorAll('.category-card, .kb-card, .tool-card, .about-card').forEach(el => {
        observer.observe(el);
    });
}

// ============================================================================
// Utilities
// ============================================================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function copyCode(button) {
    const codeBlock = button.closest('.code-example').querySelector('code');
    const text = codeBlock.textContent;
    
    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.background = 'var(--success)';
        
        setTimeout(function() {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy:', err);
        button.textContent = 'Failed';
        setTimeout(function() {
            button.textContent = 'Copy';
        }, 2000);
    });
}

// ============================================================================
// Initialize Copy Buttons
// ============================================================================

function initializeCopyButtons() {
    // Attach event listeners to all copy buttons
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            copyCode(this);
        });
    });
}

// ============================================================================
// Category Navigation
// ============================================================================

function initializeCategoryNavigation() {
    // Add keyboard shortcuts for search
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('searchInput');
            const searchResults = document.getElementById('searchResults');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchResults.classList.remove('active');
                searchResults.replaceChildren(); // Safer than innerHTML = ''
            }
        }
    });
    
    // Add visual feedback to category cards
    document.querySelectorAll('.category-card, .industry-card, .kb-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(99, 102, 241, 0.3)';
            ripple.style.width = ripple.style.height = '100px';
            ripple.style.left = `${e.offsetX - 50}px`;
            ripple.style.top = `${e.offsetY - 50}px`;
            ripple.style.animation = 'ripple 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add search hints
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const hints = [
            'Try "price monitoring"',
            'Try "web scraping"',
            'Try "e2e testing"',
            'Try "lead generation"',
            'Try "workflow automation"',
            'Try "social media"'
        ];
        
        let hintIndex = 0;
        setInterval(() => {
            if (searchInput !== document.activeElement && !searchInput.value) {
                searchInput.placeholder = `Search... ${hints[hintIndex]}`;
                hintIndex = (hintIndex + 1) % hints.length;
            }
        }, 3000);
    }
}

// Add ripple animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================================================
// Performance Monitoring
// ============================================================================

// Log page load performance
window.addEventListener('load', function() {
    if (window.performance) {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page loaded in ${pageLoadTime}ms`);
    }
});

// ============================================================================
// Workflow Generator Form Handler
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('workflow-generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const loadingState = document.getElementById('loading-state');
    const resultsContainer = document.getElementById('results-container');
    const errorContainer = document.getElementById('error-container');
    
    if (!form) return; // Form not on this page
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        const useCase = formData.get('use_case');
        const industry = formData.get('industry');
        const complexity = formData.get('complexity');
        
        // Validate
        if (!useCase || useCase.trim().length < 10) {
            alert('Please provide a more detailed use case (at least 10 characters)');
            return;
        }
        
        // Hide previous results/errors
        resultsContainer.style.display = 'none';
        errorContainer.style.display = 'none';
        
        // Show loading state
        loadingState.style.display = 'block';
        generateBtn.disabled = true;
        
        try {
            // Call the API
            const response = await fetch('http://localhost:3100/api/generate-workflow', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    use_case: useCase,
                    industry: industry,
                    complexity: complexity
                })
            });
            
            const data = await response.json();
            
            // Hide loading
            loadingState.style.display = 'none';
            generateBtn.disabled = false;
            
            if (data.rejected || (data.success === false && data.rejected)) {
                // Safety rejection
                showError(
                    'Request Rejected - Safety Filter',
                    data.message || data.reason || 'This use case was rejected by safety filters.',
                    data.details
                );
                return;
            }
            
            if (!data.success) {
                // Other error
                showError(
                    'Generation Failed',
                    data.error || 'Failed to generate workflow',
                    data.details || data.note
                );
                return;
            }
            
            // Success! Display the workflow
            displayWorkflow(data.workflow, data.metadata);
            
        } catch (error) {
            loadingState.style.display = 'none';
            generateBtn.disabled = false;
            
            console.error('Error:', error);
            showError(
                'Connection Error',
                'Could not connect to the workflow generator API.',
                'Make sure the MCP server is running on port 3100: npm run mcp-server'
            );
        }
    });
    
    function showError(title, message, details) {
        const errorTitle = document.getElementById('error-title');
        const errorMessage = document.getElementById('error-message');
        
        errorTitle.textContent = title;
        errorMessage.innerHTML = `
            <p>${escapeHtml(message)}</p>
            ${details ? `<p style="margin-top: var(--space-3); font-size: 0.85rem; color: var(--text-tertiary);">${escapeHtml(details)}</p>` : ''}
        `;
        
        errorContainer.style.display = 'block';
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function displayWorkflow(workflow, metadata) {
        // Update title
        const workflowTitle = document.getElementById('workflow-title');
        workflowTitle.textContent = workflow.name || 'Workflow Generated!';
        
        // Update metadata
        const metadataContainer = document.getElementById('workflow-metadata');
        metadataContainer.innerHTML = `
            <div><strong>Steps:</strong> ${workflow.steps ? workflow.steps.length : 'N/A'}</div>
            <div><strong>Difficulty:</strong> ${workflow.metadata?.difficulty || 'N/A'}</div>
            <div><strong>Category:</strong> ${workflow.metadata?.category || 'N/A'}</div>
            <div><strong>Model:</strong> ${metadata?.model || 'kimi-k2.5:cloud'}</div>
        `;
        
        // Display JSON
        const workflowJson = document.getElementById('workflow-json');
        workflowJson.querySelector('code').textContent = JSON.stringify(workflow, null, 2);
        
        // Store workflow data for download/copy
        workflowJson.dataset.workflow = JSON.stringify(workflow);
        
        // Show results
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Setup copy and download buttons
        setupResultButtons(workflow);
    }
    
    function setupResultButtons(workflow) {
        // Copy button
        const copyBtn = document.getElementById('copy-workflow-btn');
        copyBtn.onclick = function() {
            const jsonText = JSON.stringify(workflow, null, 2);
            navigator.clipboard.writeText(jsonText).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            });
        };
        
        // Download button
        const downloadBtn = document.getElementById('download-workflow-btn');
        downloadBtn.onclick = function() {
            const jsonText = JSON.stringify(workflow, null, 2);
            const blob = new Blob([jsonText], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${workflow.name || 'workflow'}.json`.replace(/[^a-z0-9_-]/gi, '_');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };
    }
    
    // Button hover effects
    generateBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 6px 20px rgba(255, 121, 0, 0.4)';
    });
    
    generateBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'var(--shadow-orange)';
    });
});
