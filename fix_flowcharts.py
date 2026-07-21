import glob

def fix():
    files = glob.glob("*.xml")
    for f in files:
        if f == "final_content.xml":
            continue
        with open(f, 'r') as file:
            content = file.read()
        
        new_content = content.replace("flowchart TD", "flowchart LR").replace("flowchart TB", "flowchart LR")
        
        if new_content != content:
            with open(f, 'w') as file:
                file.write(new_content)
            print(f"Updated {f}")

if __name__ == "__main__":
    fix()
