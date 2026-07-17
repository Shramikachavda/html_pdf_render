import re
with open('appendics.xml', 'r') as f:
    xml = f.read()

lists_to_convert = [
    ("The testing process aims to verify:", 9),
    ("Validation Process", 5),
    ("Example evaluation criteria:", 5),
    ("Validation criteria include:", 6),
    ("Prompt validation should verify:", 6),
    ("Regression testing should be performed after:", 7),
    ("The dataset should include questions from all major categories of the Theta Technolabs website, including:", 8),
    ("Recommended measurements include:", 6),
    ("Example scenarios:", 5),
    ("Expected behavior:", 3),
    ("The chatbot will be considered ready for deployment when:", 8),
    ("Examples include:", 6)
]

for header, count in lists_to_convert:
    # Match the header and exactly `count` following <p> elements (with optional whitespace)
    # Use re.DOTALL so .*? matches newlines if any, but since we are looking for <p>.*?</p> we probably don't need it.
    pattern = r'(<p>' + re.escape(header) + r'</p>)\s*' + r'((?:<p>.*?</p>\s*){' + str(count) + r'})'
    
    def repl(match):
        header_tag = match.group(1)
        items_block = match.group(2)
        
        # Extract each item
        item_matches = re.findall(r'<p>(.*?)</p>', items_block)
        
        out = [header_tag, '    <list>']
        for item in item_matches:
            out.append(f'      <item>{item}</item>')
        out.append('    </list>')
        return '\n'.join(out) + '\n'
    
    xml = re.sub(pattern, repl, xml, flags=re.DOTALL)

with open('appendics.xml', 'w') as f:
    f.write(xml)

print("Done fixing lists.")
