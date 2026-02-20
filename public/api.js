/**
 * TABOOST API Layer
 * 
 * Provides consistent API calls with mock fallbacks.
 * Both frontends import this file.
 * 
 * Usage:
 *   const data = await api.creators.list();
 *   const earnings = await api.earnings.getByCreator(1);
 */

// ── CONFIG ───────────────────────────────────────────────────
// Load from config.js if available, otherwise use defaults
const BACKEND_URL = (typeof window !== 'undefined' && window.BACKEND_URL) || 'http://localhost:8001';
const API_KEY = (typeof window !== 'undefined' && window.API_KEY) || 'tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5';
const DEV_MODE = true; // Set to false in production
const LOG_REQUESTS = true;

// ── MOCK DATA ────────────────────────────────────────────────
const MOCK = {
  creators: [
    {
      id: "c1",
      handle: '@rileydance',
      name: 'Riley Summers',
      followers: 892000,
      avgViews: 410000,
      engagement: 8.7,
      postsPerWeek: 6,
      status: 'hot',
      trend: [820, 835, 841, 858, 867, 879, 892],
      notes: 'Brand deal closing with FashionNova. Push engagement this week.'
    },
    {
      id: "c2",
      handle: '@chefmarcus',
      name: 'Marcus Webb',
      followers: 234000,
      avgViews: 98000,
      engagement: 11.2,
      postsPerWeek: 4,
      status: 'trending',
      trend: [198, 205, 210, 218, 224, 229, 234],
      notes: 'Food niche — strong CPMs. Ready for first brand deal.'
    },
    {
      id: "c3",
      handle: '@techbyjay',
      name: 'Jason Park',
      followers: 1400000,
      avgViews: 620000,
      engagement: 5.1,
      postsPerWeek: 3,
      status: 'hot',
      trend: [1310, 1330, 1350, 1368, 1380, 1392, 1400],
      notes: 'Biggest account. Keep posting consistently.'
    },
    {
      id: "c4",
      handle: '@lilylifts',
      name: 'Lily Torres',
      followers: 67000,
      avgViews: 31000,
      engagement: 14.8,
      postsPerWeek: 7,
      status: 'trending',
      trend: [51, 54, 57, 59, 62, 65, 67],
      notes: 'Engagement is insane. Build to 100k before pitching brands.'
    },
    {
      id: "c5",
      handle: '@dj_kobi',
      name: 'Kobi Mensah',
      followers: 388000,
      avgViews: 145000,
      engagement: 6.3,
      postsPerWeek: 2,
      status: 'watch',
      trend: [392, 391, 390, 389, 390, 388, 388],
      notes: 'Stagnating. Need content strategy meeting.'
    },
    {
      id: "c6",
      handle: '@gemmacooks',
      name: 'Gemma Hill',
      followers: 155000,
      avgViews: 72000,
      engagement: 9.4,
      postsPerWeek: 5,
      status: 'trending',
      trend: [138, 141, 144, 148, 151, 153, 155],
      notes: 'Consistent grower. Pitch kitchenware deals.'
    }
  ],

  earnings: {
    "c1": [
      { id: "e1", source: 'live', amount: 84.50, date: new Date().toISOString().split('T')[0], note: 'Tuesday night LIVE, 1.5hrs' },
      { id: "e2", source: 'brand', amount: 350.00, date: new Date(Date.now() - 3*86400000).toISOString().split('T')[0], note: 'Fashion Nova post' },
      { id: "e3", source: 'live', amount: 42.25, date: new Date(Date.now() - 5*86400000).toISOString().split('T')[0], note: 'Weekend LIVE' },
      { id: "e4", source: 'fund', amount: 28.10, date: new Date(Date.now() - 7*86400000).toISOString().split('T')[0], note: 'Creator Fund payout' }
    ]
  },

  scores: {
    "c1": { growth: 78, viral: 65, brand: 82 },
    "c2": { growth: 85, viral: 72, brand: 68 },
    "c3": { growth: 62, viral: 58, brand: 91 },
    "c4": { growth: 92, viral: 88, brand: 55 },
    "c5": { growth: 45, viral: 40, brand: 70 },
    "c6": { growth: 80, viral: 75, brand: 72 }
  }
};

// ── CORE API CALLER ─────────────────────────────────────────
async function apiCall(method, path, body = null) {
  const url = `${BACKEND_URL}${path}`;
  const options = {
    method,
    headers: { 
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    }
  };

  if (body) options.body = JSON.stringify(body);

  if (LOG_REQUESTS) {
    console.log(`[API] ${method} ${url}`, body ? '→' : '', body || '');
  }

  try {
    const response = await fetch(url, options);
    
    // Handle non-JSON responses (downloads)
    const contentType = response.headers.get('content-type') || '';
    let data;
    
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = { _download: true, contentType, status: response.status };
    }

    if (LOG_REQUESTS) {
      console.log(`[API] ← ${response.status}`, data);
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${data.detail || data.message || 'Unknown error'}`);
    }

    return data;
  } catch (error) {
    console.warn(`[API] Fallback to mock data for ${method} ${path}`, error.message);
    return getMockData(method, path, body);
  }
}

// ── MOCK DATA ROUTER ────────────────────────────────────────
function getMockData(method, path, body) {
  if (!DEV_MODE) {
    throw new Error('Mock data disabled in production');
  }

  // Health check
  if (path === '/health' || path === '/api/health') {
    return { status: 'ok', service: 'taboost-api', mock: true };
  }

  // Stats
  if (path === '/api/stats' && method === 'GET') {
    return {
      totalCreators: 6,
      totalEarningsLogged: 4,
      totalEarningsAmount: 504.85,
      ytdTotal: 504.85,
      taxYear: new Date().getFullYear()
    };
  }

  // Creators list
  if (path === '/api/creators' && method === 'GET') {
    return MOCK.creators;
  }

  // Single creator
  const creatorMatch = path.match(/^\/api\/creators\/(\w+)$/);
  if (creatorMatch && method === 'GET') {
    const id = creatorMatch[1];
    return MOCK.creators.find(c => c.id === id) || null;
  }

  // Create creator
  if (path === '/api/creators' && method === 'POST') {
    const newCreator = {
      id: "c" + Date.now(),
      ...body,
      status: body.engagement > 8 ? 'hot' : 'trending',
      trend: Array.from({ length: 7 }, (_, i) => Math.round(body.followers * (0.94 + i * 0.01))),
      notes: ''
    };
    MOCK.creators.push(newCreator);
    return newCreator;
  }

  // Update notes
  const notesMatch = path.match(/^\/api\/creators\/(\w+)\/notes$/);
  if (notesMatch && method === 'PUT') {
    const id = notesMatch[1];
    const creator = MOCK.creators.find(c => c.id === id);
    if (creator) {
      creator.notes = body.notes;
      return creator;
    }
    return null;
  }

  // Get scores
  const scoresMatch = path.match(/^\/api\/creators\/(\w+)\/scores$/);
  if (scoresMatch && method === 'GET') {
    const id = scoresMatch[1];
    return MOCK.scores[id] || { growth: 50, viral: 50, brand: 50 };
  }

  // Get earnings
  const earningsMatch = path.match(/^\/api\/creators\/(\w+)\/earnings$/);
  if (earningsMatch && method === 'GET') {
    const id = earningsMatch[1];
    return MOCK.earnings[id] || [];
  }

  // Get YTD earnings
  const ytdMatch = path.match(/^\/api\/creators\/(\w+)\/earnings\/ytd$/);
  if (ytdMatch && method === 'GET') {
    const id = ytdMatch[1];
    const earnings = MOCK.earnings[id] || [];
    const year = new Date().getFullYear();
    const bySource = {};
    let total = 0;

    earnings.forEach(e => {
      const d = new Date(e.date);
      if (d.getFullYear() === year) {
        total += e.amount;
        bySource[e.source] = (bySource[e.source] || 0) + e.amount;
      }
    });

    return { creatorId: id, taxYear: year, ytdTotal: total, bySource };
  }

  // Create earning
  const createEarningMatch = path.match(/^\/api\/creators\/(\w+)\/earnings$/);
  if (createEarningMatch && method === 'POST') {
    const id = createEarningMatch[1];
    if (!MOCK.earnings[id]) MOCK.earnings[id] = [];
    
    const newEarning = {
      id: "e" + Date.now(),
      ...body
    };
    MOCK.earnings[id].unshift(newEarning);
    return newEarning;
  }

  // Delete earning
  const deleteEarningMatch = path.match(/^\/api\/creators\/(\w+)\/earnings\/(\w+)$/);
  if (deleteEarningMatch && method === 'DELETE') {
    const creatorId = deleteEarningMatch[1];
    const earningId = deleteEarningMatch[2];
    
    if (MOCK.earnings[creatorId]) {
      MOCK.earnings[creatorId] = MOCK.earnings[creatorId].filter(e => e.id !== earningId);
    }
    return { success: true, message: 'Entry deleted' };
  }

  // Export CSV (mock - just return success)
  if (path.match(/^\/api\/creators\/\w+\/export\/csv$/)) {
    console.log('[API] Mock CSV export - would trigger download');
    return { success: true, mock: true };
  }

  // Export PDF (mock - just return success)
  if (path.match(/^\/api\/creators\/\w+\/export\/pdf$/)) {
    console.log('[API] Mock PDF export - would trigger download');
    return { success: true, mock: true };
  }

  console.warn(`[API] No mock data for ${method} ${path}`);
  return null;
}

// ── API MODULE ───────────────────────────────────────────────
const api = {
  // Health check
  health: async () => {
    // Health doesn't need API key
    const url = `${BACKEND_URL}/health`;
    try {
      const response = await fetch(url);
      return await response.json();
    } catch (e) {
      return { status: 'ok', service: 'taboost-api', mock: true };
    }
  },

  // Stats
  stats: async () => apiCall('GET', '/api/stats'),

  // Creators
  creators: {
    list: async () => apiCall('GET', '/api/creators'),
    getById: async (id) => apiCall('GET', `/api/creators/${id}`),
    create: async (data) => apiCall('POST', '/api/creators', data),
    updateNotes: async (id, notes) => apiCall('PUT', `/api/creators/${id}/notes`, { notes }),
    getScores: async (id) => apiCall('GET', `/api/creators/${id}/scores`)
  },

  // Earnings
  earnings: {
    getByCreator: async (creatorId) => apiCall('GET', `/api/creators/${creatorId}/earnings`),
    getYTD: async (creatorId) => apiCall('GET', `/api/creators/${creatorId}/earnings/ytd`),
    create: async (creatorId, data) => apiCall('POST', `/api/creators/${creatorId}/earnings`, data),
    delete: async (creatorId, earningId) => apiCall('DELETE', `/api/creators/${creatorId}/earnings/${earningId}`)
  },

  // Export
  export: {
    csv: async (creatorId) => {
      window.open(`${BACKEND_URL}/api/creators/${creatorId}/export/csv?apiKey=${API_KEY}`, '_blank');
      return { success: true };
    },
    pdf: async (creatorId) => {
      window.open(`${BACKEND_URL}/api/creators/${creatorId}/export/pdf?apiKey=${API_KEY}`, '_blank');
      return { success: true };
    }
  }
};

// ── EXPORT ───────────────────────────────────────────────────
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { api, MOCK, BACKEND_URL, API_KEY };
}
