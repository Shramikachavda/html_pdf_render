// ==========================================================================
// DOCUCRAFT APPLICATION SCRIPT
// A4 Technical Sheet Layout Engine (XML Compiler)
// ==========================================================================

// Fallback Default Content in XML format using clean <section> tags
const defaultText = `<document title="Theta ChatBot" project="THETA CHATBOT — TECHNICAL DESIGN DOCUMENT" subtitle="Technical Design Document" author="Theta TechnoLabs" version="v1.0" owner_site="https://www.thetatechnolabs.in/">
  
  <!-- ============ COVER ============ -->
  <cover kicker="INTERNAL TECHNICAL DESIGN DOCUMENT" title="Theta ChatBot" subtitle="Retrieval-grounded website assistant for thetatechnolabs.in — architecture, technology stack, application flow and data handling, end to end.">
    <revision_table>
      <row field="Project" value="Theta ChatBot — Static Knowledge-Base Assistant" />
      <row field="Owner site" value="https://www.thetatechnolabs.in/" />
      <row field="Prepared for" value="Project Mentor Review" />
      <row field="Document status" value="Draft v1.0 — for internal review" />
      <row field="Classification" value="Internal Use Only" />
    </revision_table>
  </cover>

  <!-- ============ TOC ============ -->
  <section kicker="SHEET INDEX" number="00">
    <title>Contents</title>
    <toc>
      <item number="01" title="Executive Summary" desc="What we are building, and in one paragraph, how" />
      <item number="02" title="Overall Approach" desc="RAG methodology · knowledge-base structure, storage &amp; query" />
      <item number="03" title="Technical Stack &amp; Choices" desc="Frontend / backend / data layer, with justification for each" />
      <item number="04" title="API Inventory" desc="Every external and internal API, and its exact purpose" />
      <item number="05" title="System Architecture" desc="Full component diagram and communication paths" />
      <item number="06" title="Frontend Integration" desc="Embedding the widget into the existing Webflow site" />
      <item number="07" title="Application Flow" desc="Query lifecycle, sequence diagram, step-by-step trace" />
    </toc>
  </section>

  <!-- ============ 01 EXEC SUMMARY ============ -->
  <section kicker="01 — OVERVIEW" number="01">
    <title>Executive Summary</title>
    <p>Theta ChatBot is a website assistant embedded on <span class="mono">thetatechnolabs.in</span> that answers visitor questions using <strong>only</strong> the company's own website content. It does not answer from the open internet and does not let the underlying language model improvise facts about Theta Technolabs — every answer is grounded in a knowledge base built from our own pages, and the model is instructed to say "I don't have that information" rather than guess.</p>
    
    <p>Because the knowledge base is <strong>static</strong> (it changes only when someone deliberately re-scrapes or edits it — not on every page load), we do not need a heavy real-time crawling pipeline. This lets us keep the system small, cheap to run, and easy for one engineer to operate on our own server.</p>

    <callout label="IN ONE SENTENCE">
      A visitor's question is converted into a vector, matched against pre-embedded chunks of our own website content stored in Postgres, and the matched chunks are handed to an LLM (Gemini first, OpenAI as a paid fallback) which is told to answer <em>using only that context</em>.
    </callout>

    <h2>Scope of this document</h2>
    <p>This document is written so that a technical reviewer with no prior context can understand the full system — what is built, why each choice was made over its alternatives, how the pieces talk to each other, and what happens to a single user message from the moment it is typed to the moment a reply appears.</p>

    <h2>Key decisions at a glance</h2>
    <table class="spec">
      <tr><th style="width:28%">Decision</th><th>Choice made</th></tr>
      <tr><td>Methodology</td><td class="mono">Retrieval-Augmented Generation (RAG)</td></tr>
      <tr><td>Knowledge base store</td><td class="mono">PostgreSQL + pgvector — single unified database</td></tr>
      <tr><td>Backend</td><td class="mono">Python · FastAPI</td></tr>
      <tr><td>Frontend integration</td><td class="mono">Custom JS/CSS widget embedded into existing Webflow site</td></tr>
      <tr><td>Primary LLM</td><td class="mono">Google Gemini (1.5 / 2.0 Flash tier)</td></tr>
      <tr><td>Fallback LLM</td><td class="mono">OpenAI (usage-metered, cost-flagged)</td></tr>
      <tr><td>Admin dashboard</td><td class="mono">Custom React dashboard reading directly from Postgres</td></tr>
      <tr><td>Deployment</td><td class="mono">Docker Compose, on-premise company server</td></tr>
      <tr><td>Widget transport</td><td class="mono">REST (HTTPS JSON), no WebSocket in v1</td></tr>
    </table>
  </section>

  <!-- ============ 02 OVERALL APPROACH ============ -->
  <section kicker="02 — METHODOLOGY" number="02">
    <title>Overall Approach</title>
    
    <question number="1">
      <text>Why Retrieval-Augmented Generation (RAG)?</text>
      <why>We are <strong>not</strong> fine-tuning a model on Theta Technolabs data, and we are <strong>not</strong> letting the LLM answer from its own general knowledge. Both would risk the bot inventing facts about our company (wrong pricing, wrong services, wrong contact details). Instead we use RAG: at answer-time, we retrieve the most relevant pieces of our own website content and paste them into the model's prompt as context, then instruct the model to answer strictly from that context.</why>
    </question>

    <table class="spec">
      <tr><th style="width:30%">Approach</th><th>Verdict</th></tr>
      <tr><td>Fine-tuning an LLM on our content</td><td>Rejected — expensive to retrain every time the site changes, and doesn't reliably stop hallucination.</td></tr>
      <tr><td>Plain prompt with entire site pasted in</td><td>Rejected — website content will exceed context limits as pages grow, and is wasteful/costly per request.</td></tr>
      <tr><td><strong>RAG (retrieve → ground → generate)</strong></td><td><strong>Selected</strong> — small footprint, always answers from current content, easy to update without retraining.</td></tr>
    </table>

    <question number="2">
      <text>How is the knowledge base structured?</text>
      <why>The knowledge base is a set of <strong>chunks</strong> — short passages (roughly 150–300 words each) cut from our website pages, each stored with the text itself, a vector embedding of that text, and metadata describing where it came from.</why>
    </question>

    <question number="3">
      <text>How is the knowledge base built (hybrid pipeline)?</text>
      <why>
        <steps>
          <step number="1" title="One-time scrape">A crawler script walks thetatechnolabs.in (services, about, case studies, contact, blog) and pulls clean text per page, stripping nav/footer boilerplate.</step>
          <step number="2" title="Chunking">Each page is split into overlapping ~200-word chunks along heading boundaries, so no single chunk loses context mid-sentence.</step>
          <step number="3" title="Manual curation">Team reviews the scraped chunks in the admin panel — fixes wording, removes irrelevant boilerplate, adds anything missing from the live site (e.g. FAQs that aren't on the page).</step>
          <step number="4" title="Embedding">Each approved chunk is passed through an embedding model and the resulting vector is stored alongside it in Postgres.</step>
          <step number="5" title="Freeze as &quot;static&quot;">The knowledge base is now the fixed source of truth. It is only touched again through a deliberate re-scrape or manual edit — never automatically rewritten by user conversations.</step>
        </steps>
      </why>
    </question>
  </section>
</document>`;

// DOM Elements
const textEditor = document.getElementById('text-editor');
const documentSheet = document.getElementById('document-sheet');
const documentContent = document.getElementById('document-content');
const docTitleInput = document.getElementById('doc-title');
const docSubtitleInput = document.getElementById('doc-subtitle');
const docAuthorInput = document.getElementById('doc-author');
const docVersionInput = document.getElementById('doc-version');
const coverPageSelect = document.getElementById('cover-page-style');
const chkAutoNumber = document.getElementById('chk-auto-number');
const chkPageBreaks = document.getElementById('chk-page-breaks');
const fileUpload = document.getElementById('file-upload');

// Zoom controls
const btnZoomIn = document.getElementById('btn-zoom-in');
const btnZoomOut = document.getElementById('btn-zoom-out');
const zoomLevelText = document.getElementById('zoom-level');
let currentZoom = 1.0;

// Theme controls
const themeButtons = document.querySelectorAll('.theme-btn');
const colorDots = document.querySelectorAll('.color-dot');

// Active Styles
let activeTheme = 'corporate';
let activeColor = 'blue';

// flag to prevent infinite loops when updating inputs from parsed XML
let isUpdatingInputs = false;

// ==========================================================================
// PARSING SYSTEM
// ==========================================================================

// Parse markdown helper
function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="doc-code">$1</code>');
}

// Compile XML Nodes to HTML
function compileXMLNode(node, sectionNum) {
  if (node.nodeType === Node.TEXT_NODE) {
    return parseMarkdown(node.textContent);
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return '';
  }

  const name = node.nodeName.toLowerCase();

  // Custom Question tag (Compiles to standard technical document heading and paragraph)
  if (name === 'question') {
    const num = node.getAttribute('number') || '';
    let qText = node.getAttribute('text') || '';
    if (!qText) {
      const textTag = node.querySelector('text');
      if (textTag) qText = textTag.textContent;
    }
    
    let whyContent = '';
    const whyTag = node.querySelector('why') || node.querySelector('explanation');
    if (whyTag) {
      whyContent = compileXMLNode(whyTag, sectionNum);
    } else {
      // Fallback: collect children that are not text or why/explanation
      node.childNodes.forEach(child => {
        const cName = child.nodeName.toLowerCase();
        if (cName !== 'text' && cName !== 'why' && cName !== 'explanation') {
          whyContent += compileXMLNode(child, sectionNum);
        }
      });
    }

    // Format heading text matching section number prefix (e.g. 11.1)
    let headingText = qText.trim();
    if (sectionNum && num) {
      const cleanSecNum = parseInt(sectionNum, 10).toString();
      headingText = `${cleanSecNum}.${num} ${headingText}`;
    } else if (num) {
      headingText = `${num} ${headingText}`;
    }

    let bodyHTML = whyContent.trim();
    // Wrap in paragraph if it doesn't already start with block tags
    if (bodyHTML && !bodyHTML.startsWith('<p>') && !bodyHTML.startsWith('<div') && !bodyHTML.startsWith('<ul') && !bodyHTML.startsWith('<ol')) {
      bodyHTML = `<p>${bodyHTML}</p>`;
    }

    return `
      <h2>${parseMarkdown(headingText)}</h2>
      ${bodyHTML}
    `;
  }

  // Wrapper tags return compiled children directly
  if (name === 'why' || name === 'explanation' || name === 'text') {
    let inner = '';
    node.childNodes.forEach(child => {
      inner += compileXMLNode(child, sectionNum);
    });
    return inner;
  }

  // Custom Callout tag
  if (name === 'callout') {
    const label = node.getAttribute('label') || 'NOTE';
    let innerContent = '';
    node.childNodes.forEach(child => {
      innerContent += compileXMLNode(child, sectionNum);
    });
    return `
      <div class="callout">
        <span class="lbl">${label}</span>
        ${innerContent}
      </div>
    `;
  }

  // Custom Decision tag
  if (name === 'decision') {
    const label = node.getAttribute('label') || 'DECISION';
    let innerContent = '';
    node.childNodes.forEach(child => {
      innerContent += compileXMLNode(child, sectionNum);
    });
    return `
      <div class="decision">
        <span class="lbl">${label}</span>
        ${innerContent}
      </div>
    `;
  }

  // Custom steps tag
  if (name === 'steps') {
    let innerContent = '';
    node.childNodes.forEach(child => {
      if (child.nodeName.toLowerCase() === 'step') {
        const num = child.getAttribute('number') || '';
        const title = child.getAttribute('title') || '';
        let desc = '';
        child.childNodes.forEach(c => { desc += compileXMLNode(c, sectionNum); });
        innerContent += `
          <div class="step">
            ${num ? `<span class="n">${num}</span>` : ''}
            ${title ? `<span class="t">${title}</span>` : ''}
            <div class="d">${desc}</div>
          </div>
        `;
      }
    });
    return `<div class="steps">${innerContent}</div>`;
  }

  // Custom toc tag
  if (name === 'toc') {
    let innerContent = '';
    node.childNodes.forEach(child => {
      if (child.nodeName.toLowerCase() === 'item') {
        const num = child.getAttribute('number') || '';
        const title = child.getAttribute('title') || '';
        const desc = child.getAttribute('desc') || '';
        innerContent += `
          <span class="toc-row">
            <span class="tn">${num}</span>
            <span class="tt">${title}</span>
            <span class="td">${desc}</span>
          </span>
        `;
      }
    });
    return innerContent;
  }

  // Compile normal HTML tags (recursively compile attributes and children)
  let attrStr = '';
  for (let i = 0; i < node.attributes.length; i++) {
    const attr = node.attributes[i];
    attrStr += ` ${attr.name}="${attr.value}"`;
  }

  let childrenHTML = '';
  node.childNodes.forEach(child => {
    childrenHTML += compileXMLNode(child, sectionNum);
  });

  return `<${name}${attrStr}>${childrenHTML}</${name}>`;
}

// XML Document compiler
function compileXML(text) {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(text, 'application/xml');
  
  // Check for XML parsing error
  const parserError = xmlDoc.querySelector('parsererror');
  if (parserError) {
    return {
      error: true,
      message: parserError.textContent
    };
  }

  const docRoot = xmlDoc.querySelector('document');
  let title = 'Theta ChatBot';
  let project = 'THETA CHATBOT — TECHNICAL DESIGN DOCUMENT';
  let subtitle = 'Technical Design Document';
  let author = 'Theta TechnoLabs';
  let version = 'v1.0';

  if (docRoot) {
    title = docRoot.getAttribute('title') || title;
    project = docRoot.getAttribute('project') || project;
    subtitle = docRoot.getAttribute('subtitle') || subtitle;
    author = docRoot.getAttribute('author') || author;
    version = docRoot.getAttribute('version') || version;

    // Safely update on-screen settings
    if (!isUpdatingInputs) {
      isUpdatingInputs = true;
      docTitleInput.value = title;
      docSubtitleInput.value = subtitle;
      docAuthorInput.value = author;
      docVersionInput.value = version;
      isUpdatingInputs = false;
    }
  }

  let finalHTML = '';
  const childNodes = docRoot ? docRoot.childNodes : xmlDoc.childNodes;
  let pageCounter = 0;

  childNodes.forEach(node => {
    if (node.nodeType !== Node.ELEMENT_NODE) return;

    const name = node.nodeName.toLowerCase();

    // 1. Compile Cover Page
    if (name === 'cover') {
      const kicker = node.getAttribute('kicker') || 'TECHNICAL DOCUMENT';
      const cTitle = node.querySelector('title') ? node.querySelector('title').textContent : title;
      const cSubtitle = node.querySelector('subtitle') ? node.querySelector('subtitle').textContent : subtitle;
      
      let revTableHTML = '';
      const revTable = node.querySelector('revision_table');
      if (revTable) {
        let rows = '';
        revTable.querySelectorAll('row').forEach(row => {
          const f = row.getAttribute('field') || '';
          const v = row.getAttribute('value') || '';
          rows += `<tr><td>${f}</td><td>${v}</td></tr>`;
        });
        revTableHTML = `
          <table class="revtable">
            <thead>
              <tr><th>Field</th><th>Value</th></tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        `;
      }

      finalHTML += `
        <div class="sheet cover">
          <div class="cover-inner">
            <div class="kicker2">${kicker}</div>
            <h1>${cTitle}</h1>
            <div class="subtitle">${cSubtitle}</div>
            ${revTableHTML}
          </div>
        </div>
      `;
      pageCounter++;
    }

    // 2. Compile standard page sheets/sections
    if (name === 'sheet' || name === 'section') {
      const kicker = node.getAttribute('kicker') || '';
      const titleTag = node.querySelector('title');
      const sTitle = node.getAttribute('title') || (titleTag ? titleTag.textContent : '');
      const customNum = node.getAttribute('number') || `SHEET ${pageCounter.toString().padStart(2, '0')}`;
      const sectionNum = node.getAttribute('number') || '';
      
      let bodyContent = '';
      node.childNodes.forEach(child => {
        if (name === 'section' && child.nodeName.toLowerCase() === 'title') return;
        bodyContent += compileXMLNode(child, sectionNum);
      });

      finalHTML += `
        <div class="sheet">
          <div class="rail">
            <div class="rail-label mono">${project}</div>
          </div>
          <div class="sheet-body">
            ${kicker ? `<div class="kicker">${kicker}</div>` : ''}
            ${sTitle ? `<h1 class="section-title">${sTitle}</h1>` : ''}
            ${bodyContent}
          </div>
          <div class="sheet-foot">
            <span class="proj">${project}</span>
            <span class="num">${customNum}</span>
          </div>
        </div>
      `;
      pageCounter++;
    }
  });

  return finalHTML;
}

// Fallback plain-text parser (compiles plain text into matching sheet layouts)
function compilePlainText(text) {
  const lines = text.split('\n');
  const sections = [];
  let currentSection = null;
  let currentParagraphs = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line === '') continue;

    // Heading detect
    const sectionMatch = line.match(/^\s*(\d+)\.\s*(.*)/);
    if (sectionMatch) {
      if (currentSection) {
        currentSection.content = currentParagraphs.join('\n');
        sections.push(currentSection);
      }
      currentSection = {
        number: sectionMatch[1],
        title: sectionMatch[2],
        content: ''
      };
      currentParagraphs = [];
    } else {
      if (!currentSection) {
        currentSection = {
          number: '0',
          title: 'General Overview',
          content: ''
        };
      }
      currentParagraphs.push(line);
    }
  }
  if (currentSection) {
    currentSection.content = currentParagraphs.join('\n');
    sections.push(currentSection);
  }

  const title = docTitleInput.value || 'Untitled Document';
  const subtitle = docSubtitleInput.value || '';
  const author = docAuthorInput.value || '';
  const version = docVersionInput.value || '';
  const project = title.toUpperCase() + ' — TECHNICAL DOCUMENT';

  let finalHTML = '';
  let pageCounter = 0;

  // 1. Cover page
  finalHTML += `
    <div class="sheet cover">
      <div class="cover-inner">
        <div class="kicker2">INTERNAL TECHNICAL DOCUMENT</div>
        <h1>${title}</h1>
        <div class="subtitle">${subtitle}</div>
        <table class="revtable">
          <tr><th>Field</th><th>Value</th></tr>
          <tr><td>Prepared By</td><td>${author}</td></tr>
          <tr><td>Version</td><td>${version}</td></tr>
          <tr><td>Date</td><td>${new Date().toLocaleDateString()}</td></tr>
        </table>
      </div>
    </div>
  `;
  pageCounter++;

  // 2. Body pages (1 page per section)
  sections.forEach((sec, idx) => {
    const secKicker = `${sec.number.padStart(2, '0')} — OVERVIEW`;
    const secTitle = sec.title;
    const pageNum = `SHEET ${pageCounter.toString().padStart(2, '0')}`;
    
    const contentParagraphs = sec.content.split('\n');
    let compiledBody = '';
    
    contentParagraphs.forEach(pText => {
      const trimmed = pText.trim();
      if (trimmed.startsWith('Question')) {
        compiledBody += `<h2>${parseMarkdown(trimmed)}</h2>`;
      } else if (trimmed.startsWith('Why')) {
        compiledBody += `<div class="callout"><span class="lbl">EXPLANATION</span>${parseMarkdown(trimmed)}</div>`;
      } else {
        compiledBody += `<p>${parseMarkdown(trimmed)}</p>`;
      }
    });

    finalHTML += `
      <div class="sheet">
        <div class="rail">
          <div class="rail-label mono">${project}</div>
        </div>
        <div class="sheet-body">
          <div class="kicker">${secKicker}</div>
          <h1 class="section-title">${secTitle}</h1>
          ${compiledBody}
        </div>
        <div class="sheet-foot">
          <span class="proj">${project}</span>
          <span class="num">${pageNum}</span>
        </div>
      </div>
    `;
    pageCounter++;
  });

  return finalHTML;
}

// Router/Wrapper Compiler
function renderDocument() {
  const text = textEditor.value;
  const trimmed = text.trim();
  let compiledHTML = '';

  if (trimmed.startsWith('<')) {
    const result = compileXML(text);
    if (result && result.error) {
      documentContent.innerHTML = `
        <div class="xml-error-container">
          <div class="xml-error-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            XML Parsing Error
          </div>
          <p>There is a markup syntax error in your document tags. Please review your closing elements and brackets.</p>
          <pre style="margin-top: 12px; font-family: monospace; white-space: pre-wrap; font-size: 9.5pt; color: #b91c1c; background: rgba(0,0,0,0.03); padding: 10px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.1);">${result.message}</pre>
        </div>
      `;
      return;
    }
    compiledHTML = result;
  } else {
    compiledHTML = compilePlainText(text);
  }

  documentContent.innerHTML = compiledHTML || '<div style="color: var(--text-muted); font-style:italic; text-align:center; padding: 40px 0;">Empty Document. Start typing inside the editor...</div>';
}

// ==========================================================================
// EXPORTING AND DOWNLOAD LOGIC
// ==========================================================================

function downloadFile(content, fileName, contentType) {
  const a = document.createElement("a");
  const file = new Blob([content], { type: contentType });
  a.href = URL.createObjectURL(file);
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function exportSelfContainedHTML() {
  const docTitle = docTitleInput.value || 'document';
  const cleanFileName = docTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  
  let styleSheetContent = '';
  try {
    const response = await fetch('styles.css');
    styleSheetContent = await response.text();
  } catch (error) {
    console.warn("Could not fetch external stylesheet, building inline styles from DOM styles...", error);
    for (let i = 0; i < document.styleSheets.length; i++) {
      const sheet = document.styleSheets[i];
      try {
        if (sheet.href && sheet.href.includes('styles.css')) {
          const rules = sheet.cssRules || sheet.rules;
          for (let r = 0; r < rules.length; r++) {
            styleSheetContent += rules[r].cssText + '\n';
          }
        }
      } catch (e) {
        console.error("CORS error reading stylesheet rules", e);
      }
    }
  }

  const contentHTML = documentContent.innerHTML;
  
  const finalHTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${docTitle}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #0b0f19;
      font-family: 'Inter', sans-serif;
    }
    
    .standalone-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
      gap: 30px;
      background: radial-gradient(circle at center, #1e293b 0%, #0b0f19 100%);
      min-height: 100vh;
    }
    
    ${styleSheetContent}
    
    .sheet {
      box-shadow: 0 10px 35px rgba(0,0,0,0.35);
      margin: 0 auto;
    }
    
    @media print {
      body {
        background-color: #fff !important;
      }
      .standalone-container {
        padding: 0;
        background: none;
        gap: 0;
        display: block;
      }
      .sheet {
        box-shadow: none !important;
        margin: 0 !important;
      }
    }
  </style>
</head>
<body>
  <div class="standalone-container">
    <div class="document-sheet theme-${activeTheme} color-${activeColor}">
      ${contentHTML}
    </div>
  </div>
</body>
</html>`;

  downloadFile(finalHTML, `${cleanFileName}.html`, 'text/html');
}

// ==========================================================================
// EVENT HANDLERS & INITIALIZATION
// ==========================================================================

textEditor.addEventListener('input', renderDocument);

function handleMetadataChange() {
  if (isUpdatingInputs) return;
  renderDocument();
}

docTitleInput.addEventListener('input', handleMetadataChange);
docSubtitleInput.addEventListener('input', handleMetadataChange);
docAuthorInput.addEventListener('input', handleMetadataChange);
docVersionInput.addEventListener('input', handleMetadataChange);
coverPageSelect.addEventListener('change', renderDocument);
chkAutoNumber.addEventListener('change', renderDocument);
chkPageBreaks.addEventListener('change', renderDocument);

// Theme selectors
themeButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    themeButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    activeTheme = btn.getAttribute('data-theme');
    documentSheet.className = `document-sheet theme-${activeTheme} color-${activeColor}`;
    renderDocument();
  });
});

// Color dots selectors
colorDots.forEach(dot => {
  dot.addEventListener('click', (e) => {
    colorDots.forEach(d => d.classList.remove('active'));
    dot.classList.add('active');
    
    activeColor = dot.getAttribute('data-color');
    documentSheet.className = `document-sheet theme-${activeTheme} color-${activeColor}`;
    renderDocument();
  });
});

// Zoom triggers
btnZoomIn.addEventListener('click', () => {
  if (currentZoom < 1.5) {
    currentZoom += 0.1;
    documentSheet.style.setProperty('--zoom-factor', currentZoom);
    zoomLevelText.textContent = `${Math.round(currentZoom * 100)}%`;
  }
});

btnZoomOut.addEventListener('click', () => {
  if (currentZoom > 0.5) {
    currentZoom -= 0.1;
    documentSheet.style.setProperty('--zoom-factor', currentZoom);
    zoomLevelText.textContent = `${Math.round(currentZoom * 100)}%`;
  }
});

// Export triggers
document.getElementById('btn-export-html').addEventListener('click', exportSelfContainedHTML);
document.getElementById('btn-print-pdf').addEventListener('click', () => {
  window.print();
});

// Clear and reset sample options
document.getElementById('btn-clear-all').addEventListener('click', () => {
  if (confirm("Are you sure you want to clear all text?")) {
    textEditor.value = '';
    renderDocument();
  }
});

document.getElementById('btn-reset-sample').addEventListener('click', () => {
  if (confirm("Reset to default sample XML question structure?")) {
    textEditor.value = defaultText;
    renderDocument();
  }
});

// Support local file importing
fileUpload.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    textEditor.value = evt.target.result;
    renderDocument();
  };
  reader.readAsText(file);
});

// Load initial content
async function loadInitialData() {
  try {
    const response = await fetch('html.txt');
    if (response.ok) {
      const txt = await response.text();
      textEditor.value = txt;
    } else {
      textEditor.value = defaultText;
    }
  } catch (error) {
    console.warn("Could not fetch html.txt dynamically, falling back to local preloaded text.", error);
    textEditor.value = defaultText;
  }
  renderDocument();
}

// Initial Run
window.addEventListener('DOMContentLoaded', loadInitialData);
