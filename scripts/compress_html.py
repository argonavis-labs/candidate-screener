#!/usr/bin/env python3
"""
HTML Compressor for Visual Design Assessment
Strips unnecessary elements while preserving visual design integrity
"""

import re
from bs4 import BeautifulSoup, Comment
import sys

def compress_html_for_design_assessment(input_file, output_file):
    """
    Compress HTML file by removing unnecessary elements while preserving
    visual design assessment capabilities.
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Remove all scripts - not needed for visual assessment
    for script in soup.find_all('script'):
        script.decompose()
    
    # 2. Remove all comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # 3. Remove data-savepage attributes (SavePage artifacts)
    for tag in soup.find_all(True):
        attrs_to_remove = [attr for attr in tag.attrs if 'savepage' in attr.lower()]
        for attr in attrs_to_remove:
            del tag[attr]
    
    # 4. Remove tracking and analytics related elements
    for tag in soup.find_all(['noscript', 'iframe']):
        tag.decompose()
    
    # 5. Replace base64 images with placeholders (preserve layout but not actual images)
    for tag in soup.find_all(['img', 'link']):
        if tag.has_attr('src') and 'data:image' in str(tag.get('src', '')):
            tag['src'] = 'placeholder.jpg'
            tag['data-original'] = 'base64-image-removed'
        if tag.has_attr('href') and 'data:image' in str(tag.get('href', '')):
            tag['href'] = 'placeholder.ico'
            tag['data-original'] = 'base64-image-removed'
    
    # 6. Simplify font declarations - keep only essential ones
    for style in soup.find_all('style'):
        if style.string:
            # Remove url() data URIs in fonts
            style.string = re.sub(r'src:\s*/\*.*?\*/\s*url\(\)\s*format\([^;]+\);?', 
                                 'src: local("placeholder");', style.string)
            # Remove empty url() calls
            style.string = re.sub(r'url\(\)', 'url(placeholder)', style.string)
    
    # 7. Remove unnecessary data attributes (keep only essential ones for layout)
    preserve_attrs = ['class', 'id', 'style', 'href', 'src', 'alt', 'title', 
                     'role', 'aria-label', 'data-type', 'data-layout']
    
    for tag in soup.find_all(True):
        attrs_to_keep = {}
        for attr, value in tag.attrs.items():
            if attr in preserve_attrs or attr.startswith('data-layout'):
                attrs_to_keep[attr] = value
        tag.attrs = attrs_to_keep
    
    # 8. Collapse excessive whitespace
    for tag in soup.find_all(string=True):
        if tag.parent.name not in ['style', 'pre', 'code']:
            tag.replace_with(re.sub(r'\s+', ' ', tag))
    
    # 9. Remove empty divs and spans that don't contribute to layout
    for tag in soup.find_all(['div', 'span']):
        if not tag.get_text(strip=True) and not tag.find_all() and not tag.get('class'):
            tag.decompose()
    
    # 10. Minify the output
    output = str(soup)
    # Remove unnecessary newlines and spaces between tags
    output = re.sub(r'>\s+<', '><', output)
    output = re.sub(r'\n\s*\n', '\n', output)
    
    # Write compressed file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    # Calculate compression stats
    original_size = len(html_content)
    compressed_size = len(output)
    compression_ratio = (1 - compressed_size/original_size) * 100
    
    print(f"Original size: {original_size:,} bytes")
    print(f"Compressed size: {compressed_size:,} bytes")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    input_file = "Sally Wang.html"
    output_file = "Sally_Wang_compressed.html"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    compress_html_for_design_assessment(input_file, output_file)
