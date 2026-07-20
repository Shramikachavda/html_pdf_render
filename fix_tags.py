import re

with open("sec_2_3_4.xml", "r") as f:
    content = f.read()

# Replace <tags> with <list> and <tag> with <item>
content = content.replace("<tags>", "<list>").replace("</tags>", "</list>")
content = content.replace("<tag>", "<item>").replace("</tag>", "</item>")
content = content.replace('<tag type="danger">', '<item>') # just in case

with open("sec_2_3_4.xml", "w") as f:
    f.write(content)
