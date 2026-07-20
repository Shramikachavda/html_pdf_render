// ==========================================================================
// DOCUCRAFT APPLICATION SCRIPT
// A4 Technical Sheet Layout Engine (XML Compiler - build.py Compatible)
// ==========================================================================

// Fallback Default Content in XML format (matching sample_content.txt exactly)
const defaultText = `<doc title="Example Research Report">

  <cover kicker="INTERNAL — DRAFT" title="Example Research Report"
         subtitle="A short demo document showing every supported tag.">
    <field name="Author">Your Name</field>
    <field name="Status">Draft v1</field>
  </cover>

  <toc title="Contents">
    <item n="01" title="Introduction" desc="Why this report exists"/>
    <item n="02" title="Findings" desc="What the research showed"/>
  </toc>

  <sheet label="EXAMPLE REPORT · INTRO" kicker="01 — OVERVIEW" title="Introduction" footnum="01">
    <p>This is a normal paragraph. You can use <b>bold</b>, <i>italic</i>,
       and <code>inline code</code> right inside the text, plus
       <link href="https://example.com">links</link>.</p>

    <h2>A subheading</h2>
    <p>More body text under the subheading.</p>

    <h3>A MINOR HEADING</h3>
    <list>
      <item>First bullet point</item>
      <item>Second bullet point</item>
    </list>

    <table>
      <row header="1"><cell>Column A</cell><cell>Column B</cell></row>
      <row><cell>Label</cell><cell mono="1">/api/v1/example</cell></row>
      <row><cell>Label</cell><cell>Plain value</cell></row>
    </table>

    <callout label="KEY TAKEAWAY">This is a blue informational callout box.</callout>

    <decision label="DECISION LOG — EXAMPLE">This is an amber decision-log box,
      used to record why a choice was made.</decision>

    <tags><tag>PRIMARY</tag><tag>EXTERNAL</tag></tags>

    <steps>
      <step title="Step one">Description of the first step.</step>
      <step title="Step two">Description of the second step.</step>
    </steps>
  </sheet>

  <sheet label="EXAMPLE REPORT · FINDINGS" kicker="02 — RESULTS" title="Findings" footnum="02">
    <p>Second page content goes here — every sheet becomes one A4 page in the PDF.</p>
    <orderedlist>
      <item>Ranked point one</item>
      <item>Ranked point two</item>
    </orderedlist>
  </sheet>

</doc>`;

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

// Global state for uploaded diagrams
const uploadedDiagrams = {};

window.triggerDiagramUpload = function(id) {
  const input = document.getElementById(`file-diagram-${id}`);
  if (input) input.click();
};

window.handleDiagramUpload = function(event, id) {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = function(evt) {
    uploadedDiagrams[id] = evt.target.result;
    renderDocument();
  };
  reader.readAsDataURL(file);
};

// Global state for diagram heights, widths, zooms, and panning offsets
const diagramHeights = {};
const diagramWidths = {};
const diagramZooms = {};
const diagramPanX = {};
const diagramPanY = {};

window.adjustDiagramHeight = function(event, id) {
  const val = event.target.value;
  diagramHeights[id] = val;
  const container = event.target.closest('.diagram-container');
  if (container) {
    const img = container.querySelector('.diagram-image');
    if (img) img.style.maxHeight = `${val}mm`;
    const valText = container.querySelector('.control-val');
    if (valText) valText.textContent = `${val}mm`;
  }
};

window.adjustDiagramWidth = function(event, id) {
  const val = event.target.value;
  diagramWidths[id] = val;
  const container = event.target.closest('.diagram-container');
  if (container) {
    const wrapper = container.querySelector('.diagram-wrapper');
    if (wrapper) wrapper.style.width = `${val}%`;
    const valText = container.querySelector('.width-val');
    if (valText) valText.textContent = `${val}%`;
  }
};

window.adjustDiagramZoom = function(event, id) {
  const val = parseFloat(event.target.value);
  diagramZooms[id] = val;
  const container = event.target.closest('.diagram-container');
  if (container) {
    const img = container.querySelector('.diagram-image');
    const px = diagramPanX[id] || 0;
    const py = diagramPanY[id] || 0;
    if (img) img.style.transform = `scale(${val}) translate(${px}px, ${py}px)`;
    const valText = event.target.nextElementSibling;
    if (valText) valText.textContent = `${Math.round(val * 100)}%`;
  }
};

let activeDragId = null;
let dragStartX = 0;
let dragStartY = 0;
let initialPanX = 0;
let initialPanY = 0;

window.startDiagramDrag = function(event, id) {
  if (event.target.classList.contains('diagram-overlay') || event.target.closest('.diagram-controls')) {
    return;
  }
  
  event.preventDefault();
  activeDragId = id;
  dragStartX = event.clientX;
  dragStartY = event.clientY;
  initialPanX = diagramPanX[id] || 0;
  initialPanY = diagramPanY[id] || 0;
  
  const wrapper = event.currentTarget;
  wrapper.style.cursor = 'grabbing';
  
  window.addEventListener('mousemove', handleDiagramDrag);
  window.addEventListener('mouseup', stopDiagramDrag);
};

function handleDiagramDrag(event) {
  if (!activeDragId) return;
  
  const id = activeDragId;
  const zoom = diagramZooms[id] || 1.0;
  const deltaX = event.clientX - dragStartX;
  const deltaY = event.clientY - dragStartY;
  
  const newPanX = initialPanX + (deltaX / zoom);
  const newPanY = initialPanY + (deltaY / zoom);
  
  diagramPanX[id] = newPanX;
  diagramPanY[id] = newPanY;
  
  const container = document.getElementById(`container-diagram-${id}`);
  if (container) {
    const img = container.querySelector('.diagram-image');
    if (img) img.style.transform = `scale(${zoom}) translate(${newPanX}px, ${newPanY}px)`;
  }
}

function stopDiagramDrag(event) {
  if (!activeDragId) return;
  
  const container = document.getElementById(`container-diagram-${activeDragId}`);
  if (container) {
    const wrapper = container.querySelector('.diagram-wrapper');
    if (wrapper) wrapper.style.cursor = 'grab';
  }
  
  activeDragId = null;
  window.removeEventListener('mousemove', handleDiagramDrag);
  window.removeEventListener('mouseup', stopDiagramDrag);
}

// Inline tag maps matching build.py
const INLINE_TAG_MAP = {
  "b": "strong",
  "strong": "strong",
  "i": "em",
  "em": "em",
  "code": "span class=\"mono\"",
  "mono": "span class=\"mono\"",
};

// ==========================================================================
// PARSING SYSTEM
// ==========================================================================

// Parse markdown helper for plain-text fallback
function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="doc-code">$1</code>');
}

// Escape helper matching build.py
function esc(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Compile XML mixed content to inline HTML matching build.py
function compileInlineHTML(elem) {
  let parts = [];
  elem.childNodes.forEach(child => {
    if (child.nodeType === Node.TEXT_NODE) {
      parts.push(esc(child.textContent));
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      const tag = child.nodeName.toLowerCase();
      const inner = compileInlineHTML(child);
      
      if (tag === 'link') {
        const href = esc(child.getAttribute('href') || '#');
        parts.push(`<a href="${href}">${inner}</a>`);
      } else if (INLINE_TAG_MAP[tag]) {
        const open_tag = INLINE_TAG_MAP[tag];
        const close_tag = open_tag.split(' ')[0];
        parts.push(`<${open_tag}>${inner}</${close_tag}>`);
      } else {
        parts.push(inner);
      }
    }
  });
  return parts.join('');
}

// Compile Table matching build.py
function renderTable(tbl) {
  let rows = '';
  tbl.querySelectorAll('row').forEach(row => {
    const isHeader = row.getAttribute('header') === '1';
    const cellTag = isHeader ? 'th' : 'td';
    let cells = '';
    
    row.querySelectorAll('cell').forEach(cell => {
      let content = compileInlineHTML(cell);
      if (cell.getAttribute('mono') === '1' && !isHeader) {
        content = `<span class="mono">${content}</span>`;
      }
      const width = cell.getAttribute('width');
      const style = width ? ` style="width:${width}"` : '';
      cells += `<${cellTag}${style}>${content}</${cellTag}>`;
    });
    rows += `<tr>${cells}</tr>`;
  });
  return `<table class="spec">${rows}</table>`;
}

// Compile Steps matching build.py
function renderSteps(stepsEl) {
  let out = '<div class="steps">';
  let i = 1;
  stepsEl.querySelectorAll('step').forEach(step => {
    const title = esc(step.getAttribute('title') || '');
    const desc = compileInlineHTML(step);
    out += `
      <div class="step">
        <span class="n">${i}</span>
        <span class="t">${title}</span>
        <span class="d">${desc}</span>
      </div>
    `;
    i++;
  });
  out += '</div>';
  return out;
}

// Compile Tags matching build.py
function renderTags(tagsEl) {
  let pills = '';
  tagsEl.querySelectorAll('tag').forEach(tag => {
    pills += `<span class="tag">${esc(tag.textContent)}</span>`;
  });
  return `<p>${pills}</p>`;
}

// Compile Callout & Decision matching build.py
function renderCallout(el, cssClass) {
  const label = el.getAttribute('label') || '';
  const body = compileInlineHTML(el);
  const lblHTML = label ? `<span class="lbl">${esc(label)}</span>` : '';
  return `<div class="${cssClass}">${lblHTML}${body}</div>`;
}

// Compile List matching build.py
function renderList(el, tag) {
  let items = '';
  el.querySelectorAll('item').forEach(item => {
    items += `<li>${compileInlineHTML(item)}</li>`;
  });
  return `<${tag}>${items}</${tag}>`;
}

// Compile ADR element
function renderADR(el) {
  const title = esc(el.getAttribute('title') || '');
  
  const decisionEl = el.querySelector('decision');
  const decisionText = decisionEl ? compileInlineHTML(decisionEl) : '';
  
  const altsEl = el.querySelector('alternatives');
  let altsHtml = '';
  if (altsEl) {
    const items = Array.from(altsEl.querySelectorAll('item'))
      .map(item => `<li>${compileInlineHTML(item)}</li>`)
      .join('');
    altsHtml = `<ul>${items}</ul>`;
  }
  
  const ratEl = el.querySelector('rationale');
  const ratText = ratEl ? compileInlineHTML(ratEl) : '';
  
  const impEl = el.querySelector('impact');
  let impHtml = '';
  if (impEl) {
    const pos = esc(impEl.getAttribute('pos') || '');
    const neg = esc(impEl.getAttribute('neg') || '');
    const posHtml = pos ? `<span class="impact-pos">Positive:</span> ${pos}<br/>` : '';
    const negHtml = neg ? `<span class="impact-neg">Trade-off:</span> ${neg}` : '';
    impHtml = `${posHtml}${negHtml}`;
  }
  
  return `
    <div class="adr">
      <div class="adr-head">${title}</div>
      <div class="adr-body">
        <div class="adr-row"><span class="k">DECISION</span>${decisionText}</div>
        <div class="adr-row"><span class="k">ALTERNATIVES CONSIDERED</span>${altsHtml}</div>
        <div class="adr-row"><span class="k">RATIONALE</span>${ratText}</div>
        <div class="adr-row"><span class="k">IMPACT</span>${impHtml}</div>
      </div>
    </div>
  `;
}

// Dispatch block-level element compilation matching build.py
function renderBlock(el) {
  if (el.nodeType !== Node.ELEMENT_NODE) return '';
  const t = el.nodeName.toLowerCase();
  
  if (t === "h2") {
    return `<h2>${compileInlineHTML(el)}</h2>`;
  }
  if (t === "h3") {
    return `<h3>${compileInlineHTML(el)}</h3>`;
  }
  if (t === "p") {
    return `<p>${compileInlineHTML(el)}</p>`;
  }
  if (t === "table") {
    return renderTable(el);
  }
  if (t === "callout") {
    return renderCallout(el, "callout");
  }
  if (t === "decision") {
    return renderCallout(el, "decision");
  }
  if (t === "steps") {
    return renderSteps(el);
  }
  if (t === "tags") {
    return renderTags(el);
  }
  if (t === "list") {
    return renderList(el, "ul");
  }
  if (t === "orderedlist") {
    return renderList(el, "ol");
  }
  if (t === "why") {
    const infoIconSVG = `<span class="why-meta"><svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline; margin-right:4px; vertical-align:middle; color:var(--doc-secondary);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><strong>Why this is asked:</strong></span>`;
    return `<p class="why-text">${infoIconSVG} ${compileInlineHTML(el)}</p>`;
  }
  if (t === "diagram") {
    const id = el.getAttribute('id') || `diagram-${Math.random().toString(36).substr(2, 9)}`;
    const caption = el.getAttribute('caption') || '';
    
    // Parse height from attribute (e.g. "60mm" -> 60)
    const xmlHeightAttr = el.getAttribute('height') || '60';
    const xmlHeightVal = parseInt(xmlHeightAttr.replace(/[^0-9]/g, ''), 10) || 60;
    const currentHeightVal = diagramHeights[id] !== undefined ? diagramHeights[id] : xmlHeightVal;

    // Parse width from attribute (e.g. "100%" -> 100)
    const xmlWidthAttr = el.getAttribute('width') || '100';
    const xmlWidthVal = parseInt(xmlWidthAttr.replace(/[^0-9]/g, ''), 10) || 100;
    const currentWidthVal = diagramWidths[id] !== undefined ? diagramWidths[id] : xmlWidthVal;
    
    const currentZoom = diagramZooms[id] || 1.0;
    const currentPanX = diagramPanX[id] || 0;
    const currentPanY = diagramPanY[id] || 0;
    const imageSrc = uploadedDiagrams[id];
    
    return `
      <div class="diagram-container" id="container-diagram-${id}">
        ${imageSrc ? `
          <div class="diagram-wrapper" onmousedown="startDiagramDrag(event, '${id}')" style="width:${currentWidthVal}%; cursor: grab;">
            <img src="${imageSrc}" class="diagram-image" style="max-height:${currentHeightVal}mm; object-fit:contain; transform: scale(${currentZoom}) translate(${currentPanX}px, ${currentPanY}px); transform-origin: center; transition: none;" />
            <div class="diagram-overlay" onclick="triggerDiagramUpload('${id}')">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              Change Diagram
            </div>
            <!-- Interactive controls (height + width + zoom sliders) -->
            <div class="diagram-controls no-print" onmousedown="event.stopPropagation()">
              <span class="control-label">H:</span>
              <input type="range" min="20" max="150" value="${currentHeightVal}" oninput="adjustDiagramHeight(event, '${id}')" style="width: 50px;" />
              <span class="control-val">${currentHeightVal}mm</span>
              
              <span class="control-separator">|</span>

              <span class="control-label">W:</span>
              <input type="range" min="30" max="100" value="${currentWidthVal}" oninput="adjustDiagramWidth(event, '${id}')" style="width: 50px;" />
              <span class="control-val width-val">${currentWidthVal}%</span>
              
              <span class="control-separator">|</span>
              
              <span class="control-label">Z:</span>
              <input type="range" min="1.0" max="3.0" step="0.05" value="${currentZoom}" oninput="adjustDiagramZoom(event, '${id}')" style="width: 50px;" />
              <span class="control-val">${Math.round(currentZoom * 100)}%</span>
            </div>
          </div>
        ` : `
          <div class="diagram-placeholder" onclick="triggerDiagramUpload('${id}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--doc-secondary); margin-bottom:8px;"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            <span>Click to upload diagram (ID: <strong>${id}</strong>)</span>
          </div>
        `}
        <input type="file" id="file-diagram-${id}" style="display:none;" onchange="handleDiagramUpload(event, '${id}')" accept="image/*" />
        ${caption ? `<div class="diagram-caption">${esc(caption)}</div>` : ''}
      </div>
    `;
  }
  if (t === "adr") {
    return renderADR(el);
  }
  if (t === "svg") {
    return new XMLSerializer().serializeToString(el);
  }
  if (t === "raw") {
    return el.textContent.trim();
  }
  return "";
}

// Compile Sheet Page matching build.py (including backward compatibility for <section>)
function renderSheet(sheetEl, docTitle) {
  const label = esc(sheetEl.getAttribute('label') || docTitle);
  const kicker = esc(sheetEl.getAttribute('kicker') || '');
  
  // Backward compatibility check for nested <title> elements inside sections
  const titleTag = sheetEl.querySelector('title');
  const title = esc(sheetEl.getAttribute('title') || (titleTag ? titleTag.textContent : ''));
  const footnum = esc(sheetEl.getAttribute('footnum') || '');
  
  let bodyHTML = '';
  sheetEl.childNodes.forEach(child => {
    if (child.nodeName.toLowerCase() === 'title') return;
    bodyHTML += renderBlock(child);
  });
  
  const kickerHTML = kicker ? `<div class="kicker">${kicker}</div>` : '';
  
  return `
    <div class="sheet">
      <div class="rail"><div class="rail-label mono">${label}</div></div>
      <div class="sheet-body">
        ${kickerHTML}
        ${title ? `<h1 class="section-title">${title}</h1>` : ''}
        ${bodyHTML}
      </div>
      <div class="sheet-foot"><span>${esc(docTitle)}</span><span class="num">SHEET ${footnum}</span></div>
    </div>
  `;
}

// Compile Cover Page matching build.py
function renderCover(coverEl, docTitle) {
  const kicker = esc(coverEl.getAttribute('kicker') || '');
  const title = esc(coverEl.getAttribute('title') || docTitle);
  const subtitle = esc(coverEl.getAttribute('subtitle') || '');
  const image = esc(coverEl.getAttribute('image') || '');
  
  let rows = '';
  coverEl.querySelectorAll('field').forEach(f => {
    const fieldName = esc(f.getAttribute('name') || '');
    const fieldValue = compileInlineHTML(f);
    rows += `<tr><td>${fieldName}</td><td>${fieldValue}</td></tr>`;
  });
  
  const tableHTML = rows ? `<table class="revtable"><tr><th>Field</th><th>Value</th></tr>${rows}</table>` : '';
  const imgHTML = image ? `<div style="text-align:center; margin-bottom: 20mm;"><img src="${image}" style="max-width:200px;" /></div>` : '';
  
  return `
    <div class="sheet cover">
      <div class="cover-inner">
        ${imgHTML}
        <div class="kicker2">${kicker}</div>
        <h1>${title}</h1>
        <div class="subtitle">${subtitle}</div>
        ${tableHTML}
      </div>
    </div>
  `;
}

// Compile TOC Page matching build.py
function renderTOC(tocEl, docTitle) {
  const title = esc(tocEl.getAttribute('title') || 'Contents');
  const label = esc(tocEl.getAttribute('label') || docTitle);
  
  let rows = '';
  tocEl.querySelectorAll('item').forEach(item => {
    const n = esc(item.getAttribute('n') || '');
    const itemTitle = esc(item.getAttribute('title') || '');
    const desc = esc(item.getAttribute('desc') || '');
    rows += `
      <span class="toc-row">
        <span class="tn">${n}</span>
        <span class="tt">${itemTitle}</span>
        <span class="td">${desc}</span>
      </span>
    `;
  });
  
  return `
    <div class="sheet">
      <div class="rail"><div class="rail-label mono">${label}</div></div>
      <div class="sheet-body">
        <div class="kicker">SHEET INDEX</div>
        <h1 class="section-title">${title}</h1>
        ${rows}
      </div>
      <div class="sheet-foot"><span>${esc(docTitle)}</span><span class="num">SHEET 00</span></div>
    </div>
  `;
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

  const root = xmlDoc.querySelector('doc') || xmlDoc.querySelector('document');
  
  // Read current input values as dynamic fallbacks
  let docTitle = docTitleInput.value || '';
  if (root) {
    docTitle = root.getAttribute('title') || docTitle;
    
    // Safely update on-screen settings
    if (!isUpdatingInputs) {
      isUpdatingInputs = true;
      if (root.hasAttribute('title')) docTitleInput.value = docTitle;
      isUpdatingInputs = false;
    }
  }

  let finalHTML = '';
  const childNodes = root ? root.childNodes : xmlDoc.childNodes;

  childNodes.forEach(node => {
    if (node.nodeType !== Node.ELEMENT_NODE) return;

    const name = node.nodeName.toLowerCase();

    if (name === 'cover') {
      finalHTML += renderCover(node, docTitle);
    } else if (name === 'toc') {
      finalHTML += renderTOC(node, docTitle);
    } else if (name === 'sheet' || name === 'section') {
      finalHTML += renderSheet(node, docTitle);
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
  let pageCounter = 1;

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

  // 2. Body pages (1 page per section)
  sections.forEach((sec, idx) => {
    const secKicker = `${sec.number.padStart(2, '0')} — OVERVIEW`;
    const secTitle = sec.title;
    const pageNum = pageCounter.toString().padStart(2, '0');
    
    const contentParagraphs = sec.content.split('\n');
    let compiledBody = '';
    
    contentParagraphs.forEach(pText => {
      const trimmed = pText.trim();
      if (trimmed.startsWith('Question')) {
        const cleanQText = trimmed.replace(/^Question\s*\d*\s*/i, '').trim();
        compiledBody += `<p class="question-body"><strong>${parseMarkdown(cleanQText)}</strong></p>`;
      } else if (trimmed.startsWith('Why')) {
        const cleanWhyText = trimmed.replace(/^(Why this question is asked:|Why:)\s*/i, '').trim();
        const infoIconSVG = `<span class="why-meta"><svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline; margin-right:4px; vertical-align:middle; color:var(--doc-secondary);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><strong>Why this is asked:</strong></span>`;
        compiledBody += `<p class="why-text">${infoIconSVG} ${parseMarkdown(cleanWhyText)}</p>`;
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
          <span>${title}</span>
          <span class="num">SHEET ${pageNum}</span>
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
