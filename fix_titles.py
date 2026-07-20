import re
import os
from glob import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # We want to remove <h2>X. Title</h2> where X is a chapter number (no dot after, like 5. not 5.1.)
    # We will look for <h2> followed by 1 to 2 digits, a dot, a space, and text.
    # Wait, in sec_2_3_4.xml, "2. Overall Approach" is a chapter title.
    # Let's remove <h2>\d+\.\s+[^<]+</h2> but ONLY if it's the very first <h2> in the sheet or matches the sheet title.
    
    # Actually, let's just find all <h2>\d+\.\s+[A-Za-z][^<]*</h2>
    # and if the number doesn't have a sub-dot (like 5.1), we remove it.
    
    def replacer(match):
        full_match = match.group(0)
        inner_text = match.group(1)
        # Check if inner_text starts with "Number. " (e.g. "5. ") but NOT "5.1 "
        if re.match(r'^\d+\.\s+[A-Za-z]', inner_text):
            print(f"Removing Chapter Title <h2>: {inner_text} in {filepath}")
            return "" # Remove it
        return full_match
        
    # Also remove "<h2>Chapter X: ...</h2>"
    content = re.sub(r'<h2>Chapter\s+\d+[^<]*</h2>\s*', '', content)

    content = re.sub(r'<h2>(.*?)</h2>\s*', replacer, content)

    with open(filepath, 'w') as f:
        f.write(content)

for f in glob('*.xml'):
    fix_file(f)

