#!/usr/bin/env python3
"""Verify all internal links in HTML files."""

import os
import re

project_root = 'T:/!projects/IMAGE HOSTING/studiosoctave-images'

# Find all HTML files
html_files = []
for root, dirs, files in os.walk(project_root):
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

print(f'Checking links in {len(html_files)} HTML files\n')

issues = []
for html_path in html_files:
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all anchor tags with href
    href_pattern = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>', re.IGNORECASE)
    matches = list(href_pattern.finditer(content))
    
    for match in matches:
        href = match.group(1)
        # Check for relative paths that might be broken
        if href and not href.startswith('http') and not href.startswith('//'):
            # Normalize
            norm_href = href.replace('\\', '/')
            if norm_href.startswith('./'):
                norm_href = norm_href[2:]
            if norm_href.startswith('/'):
                norm_href = norm_href[1:]
            
            # Check if the file exists
            full_path = os.path.join(project_root, norm_href) if norm_href else None
            if full_path and not os.path.exists(full_path) and norm_href != '':
                # Check if it's a known pattern (like index.html, index.html etc.)
                # Don't flag if it's just a hash or empty
                if norm_href and norm_href != '#':
                    rel = os.path.relpath(html_path, project_root)
                    issues.append(f'{rel}: href="{href}" references missing file')

if issues:
    print('LINK ISSUES FOUND:')
    for i in issues:
        print(f'  {i}')
else:
    print('All internal links appear valid!')

# Show a sample of back/ home links
print('\nSample back/home links:')
checked = 0
for html_path in html_files[:20]:
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    back_pattern = re.compile(r'<a[^>]+class="back"[^>]*href="([^"]+)"[^>]*>', re.IGNORECASE)
    back_matches = list(back_pattern.finditer(content))
    
    for match in back_matches:
        href = match.group(1)
        if checked < 10:
            rel_path = os.path.relpath(html_path, project_root)
            print(f'  {rel_path}: back href="{href}"')
            checked += 1