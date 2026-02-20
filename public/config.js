/**
 * TABOOST Frontend Configuration
 * 
 * This file is gitignored - do not commit real API keys to production.
 * For local dev, the key below works with the local backend.
 */

// Backend URL - update for production
const BACKEND_URL = 'http://localhost:8001';

// API Key - matches backend/.env
const API_KEY = 'tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5';

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { BACKEND_URL, API_KEY };
}
