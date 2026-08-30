import os
import json
import re

base_dir = os.path.expanduser('~/ai-workspace/millashop')
old_shop = os.path.join(base_dir, 'old shop')
dist_dir = os.path.join(base_dir, 'dist')

layout_dir = os.path.join(old_shop, 'layout')
templates_dir = os.path.join(old_shop, 'templates')
sections_dir = os.path.join(old_shop, 'sections')

os.makedirs(dist_dir, exist_ok=True)

sections_html = ""
index_json_path = os.path.join(templates_dir, 'index.json')

if os.path.exists(index_json_path):
    try:
        with open(index_json_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        order = index_data.get('order', [])
        sections = index_data.get('sections', {})
        for sec_key in order:
            sec_type = sections.get(sec_key, {}).get('type', '')
            sec_file = os.path.join(sections_dir, f"{sec_type}.liquid")
            if os.path.exists(sec_file):
                with open(sec_file, 'r', encoding='utf-8', errors='ignore') as sf:
                    sections_html += sf.read()
    except Exception as e:
        print("Fout bij lezen index.json:", e)

theme_path = os.path.join(layout_dir, 'theme.liquid')
if os.path.exists(theme_path):
    with open(theme_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    if '{{ content_for_layout }}' in content:
        content = content.replace('{{ content_for_layout }}', sections_html)
    else:
        content += sections_html

    # 1. Verwijder commentaren, schema's, javascripts, stylesheets en Liquid blokken
    content = re.sub(r'\{\%\s*comment\s*\%\}.*?\{\%\s*endcomment\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*schema\s*\%\}.*?\{\%\s*endschema\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*javascript\s*\%\}.*?\{\%\s*endjavascript\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*stylesheet\s*\%\}.*?\{\%\s*endstylesheet\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*liquid.*?\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%.*?\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\{.*?\}\}', '', content, flags=re.DOTALL)

    # 2. Verwijder HTML commentaren
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # 3. Verwijder losse tekst/commentaar-regels die niet in HTML tags staan
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Als een regel geen HTML tag bevat en niet leeg is, sla over
        if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
            if 'prefers-reduced-motion' in stripped or 'slot' in stripped or 'media' in stripped or 'art direction' in stripped:
                continue
        cleaned_lines.append(line)
    content = '\n'.join(cleaned_lines)

    # 4. Zorg dat base.css gelinkt is
    if '</head>' in content and 'base.css' not in content:
        content = content.replace('</head>', '<link rel="stylesheet" href="assets/base.css">\n</head>')

    # 5. Fix asset paden
    content = re.sub(r'src=["\']([^"\']+\.(?:js|png|jpg|jpeg|svg|webp))["\']', r'src="assets/\1"', content)
    content = re.sub(r'href=["\']([^"\']+\.css)["\']', r'href="assets/\1"', content)

    out_path = os.path.join(dist_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Schoongemaakte index.html gegenereerd!")

