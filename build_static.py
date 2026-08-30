import os
import re
import json

base_dir = os.path.expanduser('~/ai-workspace/millashop')
old_shop = os.path.join(base_dir, 'old shop')
dist_dir = os.path.join(base_dir, 'dist')

theme_path = os.path.join(old_shop, 'layout', 'theme.liquid')
index_json_path = os.path.join(old_shop, 'templates', 'index.json')
sections_dir = os.path.join(old_shop, 'sections')

# 1. Lees homepage secties uit index.json
sections_html = ""
if os.path.exists(index_json_path):
    with open(index_json_path, 'r', encoding='utf-8') as f:
        try:
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

# 2. Lees theme.liquid en voeg secties in
if os.path.exists(theme_path):
    with open(theme_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Plaats de homepage secties op de juiste plek
    if '{{ content_for_layout }}' in content:
        content = content.replace('{{ content_for_layout }}', sections_html)
    else:
        content += sections_html

    # Strip Liquid logica en tags
    content = re.sub(r'\{\%\s*comment\s*\%\}.*?\{\%\s*endcomment\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*schema\s*\%\}.*?\{\%\s*endschema\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*javascript\s*\%\}.*?\{\%\s*endjavascript\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\%\s*stylesheet\s*\%\}.*?\{\%\s*endstylesheet\s*\%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\{.*?\}\}', '', content)
    content = re.sub(r'\{\%.*?\%\}', '', content)
    
    # Herstel asset-paden
    content = re.sub(r'src=["\']([^"\']+\.(?:js|png|jpg|jpeg|svg|webp))["\']', r'src="assets/\1"', content)
    content = re.sub(r'href=["\']([^"\']+\.css)["\']', r'href="assets/\1"', content)

    out_path = os.path.join(dist_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Volledige index.html inclusief secties succesvol gegenereerd!")
