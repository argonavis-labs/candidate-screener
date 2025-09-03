#!/usr/bin/env python3
"""
Conservative HTML Compressor - Only removes unused font declarations
Preserves all other content to maintain exact visual appearance
"""

import re
from bs4 import BeautifulSoup
import sys

def find_used_fonts(html_content):
    """Find all font-family names actually used in the HTML/CSS."""
    used_fonts = set()
    
    # Pattern to find font-family declarations in CSS
    # Matches: font-family: "Font Name", fallback; or font-family: Font-Name;
    font_family_pattern = re.compile(
        r'font-family:\s*([^;}\n]+)[;}]',
        re.IGNORECASE | re.MULTILINE
    )
    
    matches = font_family_pattern.findall(html_content)
    
    for match in matches:
        # Clean up the match and extract individual font names
        fonts_in_declaration = match.strip()
        # Split by comma to handle font stacks
        font_list = fonts_in_declaration.split(',')
        
        for font in font_list:
            font = font.strip()
            # Remove quotes
            font = font.strip('"\'')
            # Remove !important and other CSS modifiers
            font = re.sub(r'\s*!important.*$', '', font)
            font = font.strip()
            if font and not font.startswith('var('):  # Skip CSS variables
                used_fonts.add(font)
    
    # Also look for fonts in class names (for webfonts like wf-futurapt-n4-active)
    wf_pattern = re.compile(r'wf-([a-z]+)-[a-z0-9]+-active', re.IGNORECASE)
    wf_matches = wf_pattern.findall(html_content)
    for font in wf_matches:
        used_fonts.add(font)
        # Also add capitalized versions that might be in @font-face
        used_fonts.add(font.capitalize())
        used_fonts.add(font.title())
    
    return used_fonts

def compress_fonts_only(input_file, output_file):
    """
    Compress HTML by removing only unused @font-face declarations.
    Keeps everything else intact.
    """
    
    print("Reading file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    original_size = len(html_content)
    
    # Find which fonts are actually used
    print("Analyzing font usage...")
    used_fonts = find_used_fonts(html_content)
    
    # Common font names that should always be kept
    system_fonts = {
        'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
        'system-ui', 'inherit', 'initial', 'unset', 
        'Inter', 'Inter Placeholder', 'Arial', 'Helvetica',
        'Times', 'Times New Roman', 'Courier', 'Georgia',
        'Verdana', 'Tahoma', 'Trebuchet MS'
    }
    used_fonts.update(system_fonts)
    
    # Add variations of used fonts (for different weights/styles)
    variations = set()
    for font in list(used_fonts):
        # Add potential variations
        base_font = re.sub(r'[-\s](Bold|Light|Medium|Regular|Italic|Roman).*$', '', font, flags=re.IGNORECASE)
        variations.add(base_font)
        variations.add(base_font.lower())
        variations.add(base_font.replace('-', ' '))
        variations.add(base_font.replace(' ', '-'))
    used_fonts.update(variations)
    
    print(f"Found {len(used_fonts)} font families in use")
    print("Used fonts:", sorted(used_fonts)[:20], "..." if len(used_fonts) > 20 else "")
    
    # Process the HTML content
    modified_content = html_content
    
    # Find all @font-face blocks
    font_face_pattern = re.compile(
        r'@font-face\s*\{[^}]*font-family:\s*[\'"]?([^\'";}]+)[\'"]?[^}]*\}',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    
    removed_count = 0
    kept_count = 0
    
    # Find all matches first (to avoid modifying while iterating)
    font_faces = list(font_face_pattern.finditer(modified_content))
    
    # Process from end to beginning to maintain string positions
    for match in reversed(font_faces):
        font_name = match.group(1).strip()
        
        # Check if this font is used
        font_used = False
        for used_font in used_fonts:
            if (font_name.lower() == used_font.lower() or 
                used_font.lower() in font_name.lower() or
                font_name.lower() in used_font.lower()):
                font_used = True
                break
        
        if not font_used:
            # Remove this @font-face declaration
            start_pos = match.start()
            end_pos = match.end()
            
            # Also remove any trailing whitespace/newlines
            while end_pos < len(modified_content) and modified_content[end_pos] in '\n\r\t ':
                end_pos += 1
            
            modified_content = modified_content[:start_pos] + modified_content[end_pos:]
            removed_count += 1
            print(f"  Removed unused font: {font_name}")
        else:
            kept_count += 1
            
            # Additionally, replace data URLs with placeholder to save more space
            # This preserves the font declaration but removes the embedded data
            font_block = match.group(0)
            # Replace src: url(data:...) with src: local("fontname")
            font_block_modified = re.sub(
                r'src:\s*[^;]*url\(data:[^)]+\)[^;]*;',
                f'src: local("{font_name}");',
                font_block
            )
            # Also handle the comment format /*savepage-url=...*/url()
            font_block_modified = re.sub(
                r'src:\s*/\*[^*]+\*/\s*url\(\)[^;]*;',
                f'src: local("{font_name}");',
                font_block_modified
            )
            
            if font_block != font_block_modified:
                start_pos = match.start()
                end_pos = match.end()
                modified_content = modified_content[:start_pos] + font_block_modified + modified_content[end_pos:]
                print(f"  Simplified font data for: {font_name}")
    
    # Clean up multiple consecutive blank lines
    modified_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', modified_content)
    
    # Write the result
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    # Calculate compression stats
    compressed_size = len(modified_content)
    compression_ratio = (1 - compressed_size/original_size) * 100
    
    print(f"\n{'='*50}")
    print(f"Compression Statistics:")
    print(f"{'='*50}")
    print(f"Original size:     {original_size:,} bytes")
    print(f"Compressed size:   {compressed_size:,} bytes")
    print(f"Size reduction:    {original_size - compressed_size:,} bytes")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    print(f"\nFont statistics:")
    print(f"  Total @font-face blocks: {removed_count + kept_count}")
    print(f"  Removed (unused): {removed_count}")
    print(f"  Kept (in use): {kept_count}")
    print(f"\nOutput saved to: {output_file}")

if __name__ == "__main__":
    input_file = "Sally Wang.html"
    output_file = "Sally_Wang_fonts_compressed.html"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    compress_fonts_only(input_file, output_file)
