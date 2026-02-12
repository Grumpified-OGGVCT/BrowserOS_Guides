#!/usr/bin/env node

/**
 * BrowserOS_Guides MCP Server
 * 
 * HTTP-based Model Context Protocol server providing access to the
 * BrowserOS workflows knowledge base, executable templates, and validation tools.
 * 
 * Designed for integration with BrowserOS and other MCP-capable tools.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Configuration
// Support multiple environment variable names for flexibility
const PORT = process.env.MCP_SERVER_PORT || process.env.MCP_PORT || process.env.BROWSEROS_GUIDES_PORT || 3100;
const HOST = process.env.MCP_HOST || process.env.BROWSEROS_GUIDES_HOST || 'localhost';
const ENABLE_CACHE = process.env.BROWSEROS_GUIDES_ENABLE_CACHE === 'true';
const LOG_LEVEL = process.env.BROWSEROS_GUIDES_LOG_LEVEL || 'info';

// Paths
const REPO_ROOT = path.join(__dirname, '..');
const KB_PATH = path.join(REPO_ROOT, 'BrowserOS', 'Research', 'BrowserOS_Workflows_KnowledgeBase.md');
const ANTI_PATTERNS_PATH = path.join(REPO_ROOT, 'BrowserOS', 'ANTI_PATTERNS_AND_CONSTRAINTS.md');
const WORKFLOWS_DIR = path.join(REPO_ROOT, 'BrowserOS', 'Workflows');
const LIBRARY_DIR = path.join(REPO_ROOT, 'library');
const SOURCES_PATH = path.join(REPO_ROOT, 'BrowserOS', 'Research', 'sources.json');

// Cache
const cache = new Map();

// Logger
const log = {
  info: (...args) => LOG_LEVEL !== 'silent' && console.log('[INFO]', ...args),
  warn: (...args) => console.warn('[WARN]', ...args),
  error: (...args) => console.error('[ERROR]', ...args),
  debug: (...args) => LOG_LEVEL === 'debug' && console.log('[DEBUG]', ...args)
};

/**
 * Load knowledge base into memory
 */
function loadKnowledgeBase() {
  log.info('Loading knowledge base...');
  
  const kb = {
    content: fs.readFileSync(KB_PATH, 'utf8'),
    antiPatterns: fs.existsSync(ANTI_PATTERNS_PATH) ? fs.readFileSync(ANTI_PATTERNS_PATH, 'utf8') : '',
    sources: JSON.parse(fs.readFileSync(SOURCES_PATH, 'utf8')),
    workflows: loadWorkflows(),
    templates: loadTemplates(),
    lastUpdated: fs.statSync(KB_PATH).mtime.toISOString(),
    hash: crypto.createHash('sha256').update(fs.readFileSync(KB_PATH)).digest('hex')
  };
  
  log.info(`✓ Loaded KB with ${kb.workflows.length} workflows`);
  return kb;
}

/**
 * Load all workflows from directory
 */
function loadWorkflows() {
  const workflows = [];
  
  function scanDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.name.endsWith('.json')) {
        try {
          const workflow = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
          workflow._path = path.relative(WORKFLOWS_DIR, fullPath);
          workflows.push(workflow);
        } catch (e) {
          log.warn(`Failed to parse workflow: ${fullPath}`);
        }
      }
    }
  }
  
  if (fs.existsSync(WORKFLOWS_DIR)) {
    scanDir(WORKFLOWS_DIR);
  }
  
  return workflows;
}

/**
 * Load templates from library
 */
function loadTemplates() {
  const templatesDir = path.join(LIBRARY_DIR, 'templates');
  if (!fs.existsSync(templatesDir)) {
    return { steps: {}, baseWorkflows: [], patterns: null };
  }
  
  const templates = {
    steps: {},
    baseWorkflows: [],
    patterns: null
  };
  
  // Load step templates
  const stepsDir = path.join(templatesDir, 'steps');
  if (fs.existsSync(stepsDir)) {
    const stepFiles = fs.readdirSync(stepsDir).filter(f => f.endsWith('.json'));
    for (const file of stepFiles) {
      const stepType = file.replace('_template.json', '');
      templates.steps[stepType] = JSON.parse(fs.readFileSync(path.join(stepsDir, file), 'utf8'));
    }
  }
  
  // Load base workflows
  const baseDir = path.join(templatesDir, 'base_workflows');
  if (fs.existsSync(baseDir)) {
    const baseFiles = fs.readdirSync(baseDir).filter(f => f.endsWith('.json'));
    for (const file of baseFiles) {
      templates.baseWorkflows.push(JSON.parse(fs.readFileSync(path.join(baseDir, file), 'utf8')));
    }
  }
  
  // Load pattern index
  const patternIndexPath = path.join(templatesDir, 'pattern_index.json');
  if (fs.existsSync(patternIndexPath)) {
    templates.patterns = JSON.parse(fs.readFileSync(patternIndexPath, 'utf8'));
  }
  
  return templates;
}

// Load KB on startup
let knowledgeBase = loadKnowledgeBase();

// Reload KB periodically
setInterval(() => {
  log.info('Reloading knowledge base...');
  knowledgeBase = loadKnowledgeBase();
}, 5 * 60 * 1000); // Every 5 minutes

/**
 * MCP Tool Implementations
 */

const tools = {
  query_knowledge: async ({ query, category, format = 'markdown' }) => {
    const kb = knowledgeBase.content;
    const lines = kb.split('\n');
    const matchingLines = [];
    
    // Simple keyword search
    const keywords = query.toLowerCase().split(' ');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lowerLine = line.toLowerCase();
      
      if (keywords.some(kw => lowerLine.includes(kw))) {
        const start = Math.max(0, i - 3);
        const end = Math.min(lines.length, i + 4);
        const context = lines.slice(start, end).join('\n');
        
        if (!matchingLines.some(m => m.includes(context))) {
          matchingLines.push(context);
        }
      }
    }
    
    if (format === 'json') {
      return { matches: matchingLines, count: matchingLines.length };
    }
    
    return matchingLines.join('\n\n---\n\n');
  },
  
  validate_workflow: async ({ workflow, strict = false }) => {
    const errors = [];
    const warnings = [];
    const suggestions = [];
    
    if (!workflow.name) errors.push('Missing required field: name');
    if (!workflow.steps || !Array.isArray(workflow.steps)) errors.push('Missing or invalid steps array');
    if (!workflow.version) warnings.push('Missing version field');
    
    if (workflow.steps) {
      for (const [idx, step] of workflow.steps.entries()) {
        if (!step.type) {
          errors.push(`Step ${idx}: missing type field`);
        } else if (!knowledgeBase.templates.steps[step.type]) {
          warnings.push(`Step ${idx}: Unknown step type '${step.type}'`);
        }
      }
    }
    
    if (knowledgeBase.antiPatterns) {
      if (workflow.steps && workflow.steps.some(s => s.type === 'loop' && !s.max_iterations)) {
        warnings.push('Loop without max_iterations may create infinite loop');
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  },
  
  search_workflows: async ({ query, category, difficulty, tags, limit = 10 }) => {
    let results = knowledgeBase.workflows;
    
    if (category) {
      results = results.filter(w => w.category === category);
    }
    
    if (difficulty) {
      results = results.filter(w => w.difficulty === difficulty);
    }
    
    if (tags && tags.length > 0) {
      results = results.filter(w => 
        w.tags && tags.some(t => w.tags.includes(t))
      );
    }
    
    if (query) {
      const keywords = query.toLowerCase().split(' ');
      results = results.filter(w => {
        const searchText = `${w.name} ${w.description}`.toLowerCase();
        return keywords.some(kw => searchText.includes(kw));
      });
    }
    
    results = results.slice(0, limit);
    
    return results.map(w => ({
      name: w.name,
      description: w.description,
      category: w.category,
      difficulty: w.difficulty,
      tags: w.tags,
      _path: w._path
    }));
  },
  
  get_workflow_template: async ({ workflow_id, include_metadata = true }) => {
    const workflow = knowledgeBase.workflows.find(w => 
      w.name === workflow_id || w._path.includes(workflow_id)
    );
    
    if (!workflow) {
      throw new Error(`Workflow not found: ${workflow_id}`);
    }
    
    if (!include_metadata) {
      const { metadata, _path, ...core } = workflow;
      return core;
    }
    
    return workflow;
  },
  
  check_constraints: async ({ workflow, include_suggestions = true }) => {
    const violations = [];
    
    if (workflow.steps) {
      for (const [idx, step] of workflow.steps.entries()) {
        if (step.selector && step.selector.includes(':nth-child')) {
          violations.push({
            step: idx,
            type: 'anti-pattern',
            severity: 'warning',
            message: 'Hardcoded nth-child selector detected',
            suggestion: 'Use semantic selectors (IDs, data attributes)'
          });
        }
        
        if (step.type === 'loop' && !step.max_iterations) {
          violations.push({
            step: idx,
            type: 'constraint',
            severity: 'error',
            message: 'Loop without max_iterations',
            suggestion: 'Add max_iterations to prevent infinite loops'
          });
        }
      }
    }
    
    return { violations, count: violations.length };
  },
  
  get_step_documentation: async ({ step_type, include_examples = true }) => {
    const kb = knowledgeBase.content;
    const lines = kb.split('\n');
    
    const tableStart = lines.findIndex(l => l.includes('Step Types Catalog'));
    if (tableStart === -1) {
      throw new Error('Step Types Catalog not found in KB');
    }
    
    const stepLine = lines.slice(tableStart).find(l => 
      l.includes(`**${step_type}**`)
    );
    
    if (!stepLine) {
      throw new Error(`Step type not found: ${step_type}`);
    }
    
    const template = knowledgeBase.templates.steps[step_type];
    
    return {
      step_type,
      description: stepLine,
      template: template || null,
      examples: include_examples ? [] : undefined
    };
  },
  
  list_categories: async () => {
    const categories = {};
    
    for (const workflow of knowledgeBase.workflows) {
      const cat = workflow.category || 'uncategorized';
      categories[cat] = (categories[cat] || 0) + 1;
    }
    
    return Object.entries(categories).map(([name, count]) => ({
      name,
      count,
      slug: name
    }));
  },
  
  get_anti_patterns: async ({ filter }) => {
    let content = knowledgeBase.antiPatterns;
    
    if (filter) {
      const sections = content.split('##');
      content = sections.find(s => s.toLowerCase().includes(filter.toLowerCase())) || content;
    }
    
    return { content };
  },
  
  check_source_freshness: async () => {
    return {
      last_updated: knowledgeBase.lastUpdated,
      kb_hash: knowledgeBase.hash.substring(0, 16) + '...',
      sources: knowledgeBase.sources.map(s => ({
        url: s.url,
        last_accessed: s.accessed,
        has_hash: !!s.last_processed_hash
      })),
      workflows_count: knowledgeBase.workflows.length
    };
  },
  
  generate_workflow_stub: async ({ use_case, difficulty = 'intermediate', include_error_handling = true }) => {
    const baseTemplate = knowledgeBase.templates.baseWorkflows[0];
    
    if (!baseTemplate) {
      throw new Error('No base templates available');
    }
    
    const stub = {
      ...baseTemplate,
      name: `Generated: ${use_case.substring(0, 50)}`,
      description: use_case,
      difficulty,
      metadata: {
        ...baseTemplate.metadata,
        generated_at: new Date().toISOString(),
        generated_from: use_case
      }
    };
    
    if (include_error_handling) {
      stub.error_handling = {
        on_error: 'continue',
        retry_count: 3,
        log_errors: true
      };
    }
    
    return stub;
  }
};

/**
 * MCP Request Handler
 */
async function handleMCPRequest(body) {
  const startTime = Date.now();
  
  try {
    const { tool, parameters = {} } = body;
    
    if (!tool) {
      throw new Error('Missing required field: tool');
    }
    
    if (!tools[tool]) {
      throw new Error(`Unknown tool: ${tool}`);
    }
    
    log.debug(`Executing tool: ${tool}`, parameters);
    
    const data = await tools[tool](parameters);
    
    return {
      success: true,
      data,
      metadata: {
        timestamp: new Date().toISOString(),
        kb_version: `kb-${knowledgeBase.lastUpdated.split('T')[0]}`,
        source_hash: knowledgeBase.hash.substring(0, 16) + '...',
        processing_time_ms: Date.now() - startTime
      },
      provenance: {
        sources: ['BrowserOS_Workflows_KnowledgeBase.md', 'sources.json'],
        last_updated: knowledgeBase.lastUpdated
      }
    };
    
  } catch (error) {
    log.error('Tool execution error:', error.message);
    
    return {
      success: false,
      error: {
        code: 'EXECUTION_ERROR',
        message: error.message,
        details: {}
      }
    };
  }
}

/**
 * HTTP Server
 */
const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  if (req.url === '/mcp/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      version: '1.0.0',
      kb_loaded: !!knowledgeBase,
      workflows_count: knowledgeBase.workflows.length,
      last_updated: knowledgeBase.lastUpdated
    }));
    return;
  }
  
  if (req.url === '/mcp/tools' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      tools: Object.keys(tools),
      count: Object.keys(tools).length
    }));
    return;
  }
  
  if (req.url === '/mcp' && req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        const requestBody = JSON.parse(body);
        const response = await handleMCPRequest(requestBody);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(response, null, 2));
        
      } catch (error) {
        log.error('Request error:', error.message);
        
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: false,
          error: {
            code: 'INVALID_REQUEST',
            message: error.message
          }
        }));
      }
    });
    
    return;
  }
  
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, HOST, () => {
  log.info('='.repeat(60));
  log.info('🚀 BrowserOS_Guides MCP Server');
  log.info('='.repeat(60));
  log.info(`📡 Listening on http://${HOST}:${PORT}/mcp`);
  log.info(`✅ Health check: http://${HOST}:${PORT}/mcp/health`);
  log.info(`🔧 Available tools: ${Object.keys(tools).length}`);
  log.info(`📚 Loaded workflows: ${knowledgeBase.workflows.length}`);
  log.info('='.repeat(60));
});

process.on('SIGTERM', () => {
  log.info('Received SIGTERM, shutting down gracefully...');
  server.close(() => {
    log.info('Server closed');
    process.exit(0);
  });
});
