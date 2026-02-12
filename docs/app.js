// ============================================================================
// BrowserOS Knowledge Hub - Interactive JavaScript
// Real semantic search with fuzzy matching and keyword scoring
// ============================================================================

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
        searchIndex = await response.json();
        searchIndexLoaded = true;
        console.log(`✅ Search index loaded: ${searchIndex.total_documents} documents`);
    } catch (error) {
        console.error('Failed to load search index:', error);
        searchIndexLoaded = false;
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
            
            if (query.length > 0) {
                performSearch(query, currentFilter);
            } else {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
            }
        }, 300));
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
        
        // Build loading indicator with createElement (no innerHTML)
        // Note: Spinner animation relies on .loading-spinner class in styles.css (lines ~607-619)
        const loadingDiv = document.createElement('div');
        loadingDiv.style.textAlign = 'center';
        loadingDiv.style.padding = '2rem';
        loadingDiv.style.color = 'var(--text-secondary)';
        
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
            <div style="text-align: center; padding: 2rem; color: var(--gray-500);">
                <p>No results found for "<strong>${escapeHtml(query)}</strong>"</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Try different keywords or browse <a href="#workflows" style="color: var(--primary);">workflows</a> and <a href="#knowledge-base" style="color: var(--primary);">documentation</a></p>
            </div>
        `;
    } else {
        const resultsHTML = results.map(result => `
            <a href="${result.url}" class="search-result-item" style="display: block; padding: 1rem; border-bottom: 1px solid var(--gray-200); text-decoration: none; color: inherit; transition: background 0.2s;">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; flex-wrap: wrap;">
                            <span style="background: var(--primary); color: white; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">${result.category}</span>
                            ${result.score > 500 ? '<span style="background: var(--success); color: white; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">⭐ Top Match</span>' : ''}
                        </div>
                        <h4 style="margin-bottom: 0.25rem; color: var(--gray-900); font-size: 1.125rem; font-weight: 600;">${highlightMatch(result.title, query)}</h4>
                        <p style="color: var(--gray-600); font-size: 0.875rem; line-height: 1.5;">${highlightMatch(result.description, query)}</p>
                        ${result.keywords && result.keywords.length > 0 ? `
                            <div style="display: flex; gap: 0.25rem; margin-top: 0.5rem; flex-wrap: wrap;">
                                ${result.keywords.slice(0, 5).map(kw => `
                                    <span style="background: var(--gray-100); color: var(--gray-600); padding: 0.125rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">${kw}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" style="flex-shrink: 0; color: var(--gray-400); margin-top: 0.25rem;">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                    </svg>
                </div>
            </a>
        `).join('');
        
        const relevanceNote = results.length > 5 ? 
            `<p style="font-size: 0.75rem; color: var(--gray-500); margin-top: 0.25rem;">Results ranked by relevance</p>` : '';
        
        searchResults.innerHTML = `
            <div style="margin-bottom: 1rem; padding: 0.5rem 1rem; background: var(--gray-50); border-radius: var(--radius-lg);">
                <p style="color: var(--gray-600); font-size: 0.875rem; font-weight: 500;">Found <strong style="color: var(--primary);">${results.length}</strong> result${results.length !== 1 ? 's' : ''} for "<strong>${escapeHtml(query)}</strong>"</p>
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

// Make copyCode available globally
window.copyCode = copyCode;

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
                searchResults.innerHTML = '';
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
