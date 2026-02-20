/**
 * Creator Growth Radar - Frontend Application
 * Mobile-first single page app
 */

// Configuration - Update this with your deployed backend URL
// For Vercel deployment, this gets replaced during build
let BACKEND_URL = 'https://creator-growth-radar-production.up.railway.app';

// Check for environment override (set during deployment)
if (typeof process !== 'undefined' && process.env.BACKEND_URL) {
    BACKEND_URL = process.env.BACKEND_URL;
}

// Local development override
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    BACKEND_URL = 'http://localhost:8000';
}

// DOM Elements
const form = document.getElementById('analyze-form');
const usernameInput = document.getElementById('username-input');
const analyzeBtn = document.getElementById('analyze-btn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnLoader = analyzeBtn.querySelector('.btn-loader');

const loadingSection = document.getElementById('loading-section');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const resultsSection = document.getElementById('results-section');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check for backend URL in meta tag or environment
    const metaBackend = document.querySelector('meta[name="backend-url"]');
    if (metaBackend) {
        BACKEND_URL = metaBackend.content;
    }
    
    // Allow Enter key to submit
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            form.requestSubmit();
        }
    });
    
    // Focus input on load
    usernameInput.focus();
});

// Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = usernameInput.value.trim().replace('@', '');
    
    if (!username) {
        showError('Please enter a TikTok username');
        return;
    }
    
    await analyzeCreator(username);
});

// Analyze Creator
async function analyzeCreator(username) {
    // Show loading state
    setLoadingState(true);
    
    try {
        const response = await fetch(`${BACKEND_URL}/analyze?username=${encodeURIComponent(username)}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError(error.message || 'Failed to analyze creator. Please try again.');
    } finally {
        setLoadingState(false);
    }
}

// Set Loading State
function setLoadingState(loading) {
    if (loading) {
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        loadingSection.style.display = 'flex';
        errorSection.style.display = 'none';
        resultsSection.style.display = 'none';
    } else {
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Display Results
function displayResults(data) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Creator Info
    document.getElementById('result-username').textContent = `@${data.username}`;
    
    const verifiedBadge = document.getElementById('result-verified');
    verifiedBadge.style.display = data.verified ? 'inline-block' : 'none';
    
    // Demo mode indicator
    const existingDemoBadge = document.getElementById('demo-badge');
    if (existingDemoBadge) {
        existingDemoBadge.remove();
    }
    if (data.demo_mode) {
        const demoBadge = document.createElement('span');
        demoBadge.id = 'demo-badge';
        demoBadge.className = 'demo-badge';
        demoBadge.textContent = '⚡ Demo Mode';
        document.querySelector('.creator-meta').appendChild(demoBadge);
    }
    
    // Stats
    document.getElementById('stat-followers').textContent = formatNumber(data.followers);
    document.getElementById('stat-change').textContent = `+${formatNumber(data.follower_change_24h)} (24h)`;
    document.getElementById('stat-avg-views').textContent = formatNumber(data.avg_views_last_10);
    document.getElementById('stat-engagement').textContent = `${data.engagement_rate}%`;
    document.getElementById('stat-frequency').textContent = data.posting_frequency_per_week.toFixed(1);
    
    // Scores
    updateScoreCard(
        'growth',
        data.score_breakdown.growth_velocity.raw,
        data.score_breakdown.growth_velocity.label,
        data.score_breakdown.growth_velocity.color
    );
    
    updateScoreCard(
        'viral',
        data.score_breakdown.viral_probability.raw,
        data.score_breakdown.viral_probability.label,
        data.score_breakdown.viral_probability.color
    );
    
    updateScoreCard(
        'brand',
        data.score_breakdown.brand_deal_readiness.raw,
        data.score_breakdown.brand_deal_readiness.label,
        data.score_breakdown.brand_deal_readiness.color
    );
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Update Score Card
function updateScoreCard(type, value, label, color) {
    const card = document.getElementById(`score-${type}`);
    const valueEl = document.getElementById(`score-${type}-value`);
    const fillEl = document.getElementById(`score-${type}-fill`);
    const labelEl = document.getElementById(`score-${type}-label`);
    
    // Remove all color classes
    card.classList.remove('score-green', 'score-lime', 'score-yellow', 'score-orange', 'score-red');
    
    // Add new color class
    card.classList.add(`score-${color}`);
    
    // Animate value
    animateValue(valueEl, 0, value, 1000);
    
    // Update fill width with delay for animation
    setTimeout(() => {
        fillEl.style.width = `${value}%`;
    }, 100);
    
    // Update label
    labelEl.textContent = label;
    labelEl.className = `score-label score-${color}`;
}

// Animate Number
function animateValue(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out-quart)
        const easeProgress = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + (range * easeProgress));
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Show Error
function showError(message) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'flex';
    errorMessage.textContent = message;
}

// Reset App
function resetApp() {
    usernameInput.value = '';
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';
    usernameInput.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Format Number (add commas)
function formatNumber(num) {
    if (num >= 1_000_000_000) {
        return (num / 1_000_000_000).toFixed(1) + 'B';
    } else if (num >= 1_000_000) {
        return (num / 1_000_000).toFixed(1) + 'M';
    } else if (num >= 1_000) {
        return (num / 1_000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}
