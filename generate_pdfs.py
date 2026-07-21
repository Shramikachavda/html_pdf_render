import base64
import urllib.request
import os
import json

diagrams = {
    "{{DIAGRAM_WORKFLOW}}": """graph LR
A[User Query] --> B[Query Processing]
B --> C[Knowledge Retrieval]
C --> D[Response Generation]
D --> E[Grounded Answer]""",

    "{{DIAGRAM_SEQUENCE}}": """sequenceDiagram
participant U as Frontend Widget
participant A as FastAPI Backend
participant V as Vector DB
participant L as LLM (Gemini)
U->>A: User Question
A->>A: Validate & Embed
A->>V: Semantic Search
V-->>A: Top-K Context Chunks
A->>A: Build Prompt
A->>L: Generate Response
L-->>A: LLM Answer
A->>A: Validate Confidence
A-->>U: JSON (Answer + Sources)""",

    "{{DIAGRAM_COMPONENTS}}": """graph TD
A[Webflow Site] -->|Embedded Widget| B[FastAPI REST API]
B --> C[Request Validator]
B --> D[Retrieval Engine]
D --> E[(Vector Database)]
B --> F[Prompt Builder]
F --> G[LLM Provider]""",

    "{{DIAGRAM_GUARDRAIL}}": """graph TD
A[User Query] --> B{Scope Check}
B -->|Out of Scope| C[Fallback Response]
B -->|In Scope| D[Retrieval]
D --> E{Confidence >= 0.6?}
E -->|No| F[Low Confidence Fallback]
E -->|Yes| G[LLM Generation]
G --> H{Hallucination Check}
H -->|Failed| I[Safe Fallback]
H -->|Passed| J[Final Answer]""",

    "{{DIAGRAM_FALLBACK}}": """graph LR
A[Invalid Query] --> B[Scope Clarification]
C[Prompt Injection] --> D[Sanitization & Rejection]
E[No Relevant Data] --> F[Polite Decline & Contact Link]"""
}

with open("new_html.html", "r", encoding="utf-8") as f:
    html_content = f.read()

for i, (placeholder, mermaid_code) in enumerate(diagrams.items()):
    # Convert mermaid code to base64
    b64 = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
    url = f"https://mermaid.ink/svg/{b64}"
    
    img_filename = f"diagram_new_{i}.svg"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(img_filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        
        img_tag = f'<div class="diagram-box"><img src="{img_filename}" style="width:100%; max-width:800px; display:block; margin:auto;" /></div>'
        html_content = html_content.replace(placeholder, img_tag)
        print(f"Replaced {placeholder} with {img_filename}")
    except Exception as e:
        print(f"Failed to fetch diagram for {placeholder}: {e}")

with open("final_output.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated final_output.html")
