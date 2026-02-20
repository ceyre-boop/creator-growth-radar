#!/usr/bin/env node
/**
 * TABOOST API Connection Test
 * 
 * Tests all API endpoints and reports pass/fail status.
 * Run with: node test-connection.js
 */

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';
const API_KEY = process.env.TABOOST_API_KEY || 'tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5';

const ENDPOINTS = [
  // Health (no auth)
  { method: 'GET', path: '/health', expect: 'status', auth: false },
  { method: 'GET', path: '/', expect: 'status', auth: false },
  
  // Stats
  { method: 'GET', path: '/api/stats', expect: 'object' },
  
  // Creators
  { method: 'GET', path: '/api/creators', expect: 'array' },
  { method: 'GET', path: '/api/creators/c1', expect: 'object' },
  { method: 'GET', path: '/api/creators/invalid-id', expect: 'error', expectStatus: 404 },
  { method: 'POST', path: '/api/creators', body: { handle: '@test' + Date.now(), name: 'Test User', followers: 1000, avgViews: 500, engagement: 5.0 }, expect: 'object' },
  { method: 'GET', path: '/api/creators/c1/scores', expect: 'object' },
  { method: 'PUT', path: '/api/creators/c1/notes', body: { notes: 'Test notes from connection test' }, expect: 'object' },
  
  // Earnings
  { method: 'GET', path: '/api/creators/c1/earnings', expect: 'array' },
  { method: 'GET', path: '/api/creators/c1/earnings/ytd', expect: 'object' },
  { method: 'POST', path: '/api/creators/c1/earnings', body: { source: 'live', amount: 50.00, date: '2025-01-15', note: 'Test entry' }, expect: 'object' },
  { method: 'DELETE', path: '/api/creators/c1/earnings/invalid-id', expect: 'error', expectStatus: 404 },
  
  // Export
  { method: 'GET', path: '/api/creators/c1/export/csv', expect: 'download' },
  { method: 'GET', path: '/api/creators/c1/export/pdf', expect: 'download' },
];

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  gray: '\x1b[90m'
};

async function testEndpoint(endpoint) {
  const { method, path, body, expect, expectStatus, auth = true } = endpoint;
  const url = `${BACKEND_URL}${path}`;
  
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  
  if (auth) {
    options.headers['X-API-Key'] = API_KEY;
  }
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, options);
    const contentType = response.headers.get('content-type') || '';
    
    let data;
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else if (contentType.includes('text/') || contentType.includes('application/')) {
      data = { _download: true, contentType };
    }
    
    const passed = checkResponse(response, data, expect, expectStatus);
    
    return {
      passed,
      method,
      path,
      status: response.status,
      data: truncateData(data),
      error: null
    };
  } catch (error) {
    return {
      passed: false,
      method,
      path,
      status: null,
      data: null,
      error: error.message
    };
  }
}

function checkResponse(response, data, expect, expectStatus) {
  if (expect === 'error') {
    return response.status === (expectStatus || 400);
  }
  
  if (expect === 'download') {
    return response.ok && (data?._download || response.status === 200);
  }
  
  if (expect === 'array') {
    return Array.isArray(data);
  }
  
  if (expect === 'object') {
    return data && typeof data === 'object' && !Array.isArray(data);
  }
  
  if (expect === 'status') {
    return data && (data.status === 'ok' || data.status.includes('running'));
  }
  
  return response.ok;
}

function truncateData(data, maxLen = 100) {
  if (!data) return null;
  const str = JSON.stringify(data);
  if (str.length > maxLen) {
    return str.slice(0, maxLen) + '...';
  }
  return str;
}

async function runTests() {
  console.log(`${colors.blue}╔════════════════════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.blue}║${colors.reset}  ${colors.blue}TABOOST API Connection Test${colors.reset}                        ${colors.blue}║${colors.reset}`);
  console.log(`${colors.blue}╚════════════════════════════════════════════════════════╝${colors.reset}`);
  console.log(`${colors.gray}Backend URL: ${BACKEND_URL}${colors.reset}`);
  console.log(`${colors.gray}API Key: ${API_KEY.slice(0, 12)}...${colors.reset}\n`);
  
  const results = [];
  let passed = 0;
  let failed = 0;
  
  for (const endpoint of ENDPOINTS) {
    const result = await testEndpoint(endpoint);
    results.push(result);
    
    const statusIcon = result.passed ? `${colors.green}✓${colors.reset}` : `${colors.red}✗${colors.reset}`;
    const statusColor = result.passed ? colors.gray : colors.red;
    
    console.log(`${statusIcon} ${result.method.padEnd(6)} ${result.path.padEnd(48)} ${statusColor}HTTP ${result.status || 'ERR'}${colors.reset}`);
    
    if (!result.passed && result.error) {
      console.log(`  ${colors.red}Error: ${result.error}${colors.reset}`);
    }
    
    if (result.passed) passed++;
    else failed++;
  }
  
  // Summary
  console.log(`\n${colors.blue}────────────────────────────────────────────────────────${colors.reset}`);
  console.log(`${colors.gray}Results: ${colors.green}${passed} passed${colors.reset} / ${colors.red}${failed} failed${colors.reset} / ${ENDPOINTS.length} total${colors.reset}`);
  
  if (failed === 0) {
    console.log(`${colors.green}✓ All endpoints responding correctly!${colors.reset}`);
  } else {
    console.log(`${colors.yellow}⚠ Some endpoints failed. Check the backend is running.${colors.reset}`);
  }
  
  console.log(`${colors.blue}────────────────────────────────────────────────────────${colors.reset}\n`);
  
  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(err => {
  console.error(`${colors.red}Fatal error:${colors.reset}`, err);
  process.exit(1);
});
