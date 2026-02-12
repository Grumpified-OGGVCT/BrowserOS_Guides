#!/usr/bin/env node

/**
 * Test script for BrowserOS_Guides MCP Server
 */

const http = require('http');

const MCP_URL = process.env.MCP_URL || 'http://localhost:3000';

function makeRequest(path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, MCP_URL);
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(data);
        }
      });
    });
    
    req.on('error', reject);
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

async function runTests() {
  console.log('=' .repeat(60));
  console.log('🧪 Testing BrowserOS_Guides MCP Server');
  console.log('='.repeat(60));
  
  try {
    // Test 1: Health Check
    console.log('\n✓ Test 1: Health Check');
    const health = await makeRequest('/mcp/health');
    console.log(`  Status: ${health.status}`);
    console.log(`  Workflows: ${health.workflows_count}`);
    
    // Test 2: List Tools
    console.log('\n✓ Test 2: List Tools');
    const tools = await makeRequest('/mcp/tools');
    console.log(`  Available tools: ${tools.count}`);
    console.log(`  Tools: ${tools.tools.join(', ')}`);
    
    // Test 3: Query Knowledge
    console.log('\n✓ Test 3: Query Knowledge');
    const queryResult = await makeRequest('/mcp', 'POST', {
      tool: 'query_knowledge',
      parameters: {
        query: 'navigate step',
        format: 'json'
      }
    });
    console.log(`  Success: ${queryResult.success}`);
    console.log(`  Matches found: ${queryResult.data.count}`);
    
    // Test 4: Search Workflows
    console.log('\n✓ Test 4: Search Workflows');
    const searchResult = await makeRequest('/mcp', 'POST', {
      tool: 'search_workflows',
      parameters: {
        query: 'price',
        limit: 3
      }
    });
    console.log(`  Success: ${searchResult.success}`);
    console.log(`  Results: ${searchResult.data.length}`);
    if (searchResult.data.length > 0) {
      console.log(`  First: ${searchResult.data[0].name}`);
    }
    
    // Test 5: List Categories
    console.log('\n✓ Test 5: List Categories');
    const categories = await makeRequest('/mcp', 'POST', {
      tool: 'list_categories',
      parameters: {}
    });
    console.log(`  Success: ${categories.success}`);
    console.log(`  Categories: ${categories.data.length}`);
    categories.data.slice(0, 5).forEach(cat => {
      console.log(`    - ${cat.name}: ${cat.count} workflows`);
    });
    
    // Test 6: Validate Workflow
    console.log('\n✓ Test 6: Validate Workflow');
    const validationResult = await makeRequest('/mcp', 'POST', {
      tool: 'validate_workflow',
      parameters: {
        workflow: {
          name: 'Test Workflow',
          version: '1.0.0',
          steps: [
            {
              type: 'navigate',
              name: 'Navigate to page',
              url: 'https://example.com'
            }
          ]
        }
      }
    });
    console.log(`  Success: ${validationResult.success}`);
    console.log(`  Valid: ${validationResult.data.valid}`);
    console.log(`  Errors: ${validationResult.data.errors.length}`);
    console.log(`  Warnings: ${validationResult.data.warnings.length}`);
    
    // Test 7: Check Source Freshness
    console.log('\n✓ Test 7: Check Source Freshness');
    const freshnessResult = await makeRequest('/mcp', 'POST', {
      tool: 'check_source_freshness',
      parameters: {}
    });
    console.log(`  Success: ${freshnessResult.success}`);
    console.log(`  Last updated: ${freshnessResult.data.last_updated}`);
    console.log(`  Sources: ${freshnessResult.data.sources.length}`);
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ All tests passed!');
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

runTests();
