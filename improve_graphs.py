import os
import re

repo_path = '.'
date_folders = ['26-02-06', '26-02-09', '26-02-10', '26-02-11', '26-02-12']

def get_node_id(index):
    res = ""
    while index >= 0:
        res = chr(65 + (index % 26)) + res
        index = (index // 26) - 1
    return res

def generate_mermaid_improved(content, exercise_name):
    # Special handling for the large exercise sheets
    if "Exercise_Sheets" in exercise_name:
        cases = re.findall(r'case "(.*?)":', content)
        mermaid = "graph TD\n"
        mermaid += '    Start["Start"] --> Menu["Show Exercise List"]\n'
        mermaid += '    Menu --> Selection["User Selects Exercise"]\n'
        
        for i, case in enumerate(cases):
            case_id = f"C{i}"
            # Clean case name
            clean_case = case.split(' ', 1)[1] if ' ' in case else case
            mermaid += f'    Selection -- "{case.split(" ")[0]}" --> {case_id}["{clean_case}"]\n'
            mermaid += f'    {case_id} --> End["End"]\n'
        return mermaid

    # General improvement for smaller files (detecting basic branching)
    lines = content.split('\n')
    nodes = []
    
    # Simple state machine to detect key points
    for line in lines:
        line = line.strip()
        if 'Console.ReadLine' in line:
            nodes.append(("Input", "Get user input"))
        elif 'Console.WriteLine' in line or 'Console.Write' in line:
            nodes.append(("Output", "Show message"))
        elif 'if (' in line or 'if(' in line:
            nodes.append(("Decision", "Check condition"))
        elif 'for (' in line or 'while (' in line:
            nodes.append(("Loop", "Looping"))

    # If no nodes found, just return a simple one
    if not nodes:
        return "graph TD\n    A[Start] --> B[Execute Code] --> C[End]"

    mermaid = "graph TD\n"
    mermaid += '    Start["Start"]\n'
    
    prev_id = "Start"
    for i, (ntype, label) in enumerate(nodes):
        node_id = get_node_id(i)
        shape = '["' if ntype != "Decision" else '{"'
        end_shape = '"]' if ntype != "Decision" else '"}'
        mermaid += f'    {node_id}{shape}{label}{end_shape}\n'
        
        # Connect to previous
        mermaid += f'    {prev_id} --> {node_id}\n'
        prev_id = node_id
        
    mermaid += f'    {prev_id} --> End["End"]\n'
    return mermaid

for date in date_folders:
    date_path = os.path.join(repo_path, date)
    if not os.path.exists(date_path):
        continue
    
    for exercise_folder in os.listdir(date_path):
        exercise_path = os.path.join(date_path, exercise_folder)
        if not os.path.isdir(exercise_path):
            continue
            
        cs_files = [f for f in os.listdir(exercise_path) if f.endswith('.cs')]
        if not cs_files:
            continue
            
        cs_file = cs_files[0]
        with open(os.path.join(exercise_path, cs_file), 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        title = exercise_folder.replace('_', ' ')
        clean_title = ' '.join(title.split(' ')[1:]) if title.split(' ')[0].isdigit() else title
        
        description = f"A C# exercise demonstrating {clean_title.lower()}."
        if "hello world" in title.lower():
            description = "A classic Hello World program in C#."
        elif "inquiry" in title.lower():
            description = "A simple program that asks for user input and displays it."
        elif "check" in title.lower():
            description = "A program that uses conditional logic to check a value."
            
        mermaid = generate_mermaid_improved(content, exercise_folder)
        
        readme_content = f"""# {title}

{description}

## 📝 Description
This program was generated from a Structorizer diagram and demonstrates basic programming concepts such as input/output and control flow.

## 📊 Logic Flow
```mermaid
{mermaid}
```

## 💻 Code Snippet
```csharp
{content.strip()}
```
"""
        with open(os.path.join(exercise_path, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Updated README with improved graph for {exercise_folder}")
