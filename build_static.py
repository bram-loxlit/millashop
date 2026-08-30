import os
import json
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(base_dir, 'dist')
layout_dir = os.path.join(base_dir, 'layout')
templates_dir = os.path.join(base_dir, 'templates')
sections_dir = os.path.join(base_dir, 'sections')

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
                    sections_html += f"\n<!-- SECTION: {sec_type} -->\n" + sf.read()
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

    # Grondig strippen van multi-line en single-line Liquid code
    content = re.sub(r'\{\%\s*comment\s*\%\}.*?\{\%\s*endcomment\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*schema\s*\%\}.*?\{\%\s*endschema\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*javascript\s*\%\}.*?\{\%\s*endjavascript\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*stylesheet\s*\%\}.*?\{\%\s*endstylesheet\s*\%\}', '', content, flags=re.DOTALL)
    
    # Verwijder multi-line Liquid blokken ({% liquid ... %})
    content = re.sub(r'\{\%\s*liquid.*?\%\}', '', content, flags=re.DOTALL)
    
    # Verwijder alle overige inline/multi-line tags en variabelen
    content = re.sub(r'\{\%.*?\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\{.*?\}\}', '', content, flags=re.DOTALL)

    # Herstel asset-paden
    content = re.sub(r'src=["\']([^"\']+\.(?:js|png|jpg|jpeg|svg|webp))["\']', r'src="assets/\1"', content)
    content = re.sub(r'href=["\']([^"\']+\.css)["\']', r'href="assets/\1"', content)

    out_path = os.path.join(dist_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Volledige schone index.html succesvol gegenereerd!")
