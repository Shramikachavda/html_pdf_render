import os

titles = {
    "sec_2_3_4.xml": [
        "Figure 2.1: System Workflow",
        "Figure 3.1: Synchronization Workflow",
        "Figure 3.2: Knowledge Lifecycle",
        "Figure 4.1: Request Processing Sequence",
        "Figure 4.2: Prompt Assembly Flow",
        "Figure 4.3: End-to-End Query Handling"
    ],
    "sec_5.xml": [
        "Figure 5.1: Component Communication"
    ],
    "sec_6.xml": [
        "Figure 6.1: Component Interaction Architecture"
    ],
    "sec_7.xml": [
        "Figure 7.1: API Communication Architecture"
    ],
    "sec_8.xml": [
        "Figure 8.1: Frontend Integration Overview",
        "Figure 8.3: Frontend Request Flow"
    ],
    "gradrails.xml": [
        "Figure 9.1: Guardrail Workflow",
        "Figure 9.2: Fallback Strategy Decision Process"
    ],
    "sec_9_10_11.xml": [
        "Figure 10.1: Dashboard Architecture Overview"
    ],
    "sec_12.xml": [
        "Figure 12.1: Monitoring and Observability Strategy"
    ]
}

def add_titles():
    for filename, file_titles in titles.items():
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parts = content.split('</mermaid-diagram>')
        
        if len(parts) - 1 != len(file_titles):
            print(f"Warning: Expected {len(file_titles)} diagrams in {filename}, found {len(parts) - 1}")
            continue
            
        new_content = ""
        for i, title in enumerate(file_titles):
            new_content += parts[i] + f'</mermaid-diagram>\n    <p align="center" style="text-align: center !important; color: #555555 !important;"><b>{title}</b></p>'
            
        new_content += parts[-1]
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {filename}")

if __name__ == "__main__":
    add_titles()
