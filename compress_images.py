#!/usr/bin/env python3
"""Compress images and update HTML references.

Finds all images in the project, creates compressed copies (originals untouched),
and updates HTML files to reference the compressed versions.
"""

import os
import sys
import re
import shutil
from PIL import Image


def find_image_files(project_root):
    """Find all image files in the project directory."""
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    image_files = []

    for root, dirs, files in os.walk(project_root):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in image_exts:
                image_files.append(os.path.join(root, f))

    return sorted(set(image_files))


def compress_image(img_path, project_root):
    """Create a compressed copy of an image.

    The original file is untouched. The compressed copy is saved with
    '-compressed' suffix before the extension.
    """
    base, ext = os.path.splitext(img_path)
    compressed_path = base + '-compressed' + ext

    try:
        with Image.open(img_path) as img:
            # Handle RGBA images - convert to RGB for JPEG
            if ext.lower() in ('.jpg', '.jpeg'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(compressed_path, 'JPEG', quality=80, optimize=True)
            # For PNG, use optimize parameter
            elif ext.lower() == '.png':
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGBA')
                img.save(compressed_path, 'PNG', optimize=True)
            # For GIF
            elif ext.lower() == '.gif':
                img.save(compressed_path)
            # For WebP
            elif ext.lower() == '.webp':
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGBA')
                img.save(compressed_path, 'WebP', quality=80, optimize=True)
            else:
                # Copy original for unknown formats
                shutil.copy2(img_path, compressed_path)

        orig_size = os.path.getsize(img_path)
        new_size = os.path.getsize(compressed_path)
        ratio = new_size / orig_size * 100 if orig_size > 0 else 100
        rel = os.path.relpath(img_path, start=os.path.dirname(project_root) + os.sep)
        print(f"  Compressed: {rel} -> {new_size} bytes ({(ratio):.1f}% of original)")

        return compressed_path
    except Exception as e:
        print(f"  Error compressing {img_path}: {e}")
        return None


def update_html_references(html_path, project_root):
    """Update HTML file to reference compressed images instead of originals."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all img src attributes that reference images in the project
    # Pattern matches <img> tags with src attribute
    img_pattern = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>', re.IGNORECASE)

    changed = False
    for match in img_pattern.finditer(content):
        src = match.group(1)
        # Check if the src is a path within the project (not a full URL)
        if src and not src.startswith('http') and not src.startswith('//'):
            # Normalize the path - handle both / and \\
            normalized_src = src.replace('\\', '/')
            # Make it relative to project root if it starts ./
            if normalized_src.startswith('./'):
                normalized_src = normalized_src[2:]

            full_path = os.path.join(project_root, normalized_src)
            # Check if this exact file exists (original, not compressed yet)
            if os.path.exists(full_path) and not normalized_src.endswith('-compressed.jpg') and \
               not normalized_src.endswith('-compressed.jpeg') and \
               not normalized_src.endswith('-compressed.png') and \
               not normalized_src.endswith('-compressed.gif') and \
               not normalized_src.endswith('-compressed.webp'):
                # Create the compressed version path
                base, ext = os.path.splitext(normalized_src)
                comp_rel = base + '-compressed' + ext

                # Check if compressed version already exists
                full_comp = os.path.join(project_root, comp_rel)
                if not os.path.exists(full_comp):
                    # Compress the image - pass project_root
                    compress_image(full_path, project_root)

                # Replace the src in the HTML
                new_src = comp_rel
                # Replace just the src attribute value
                content = content.replace(
                    'src="' + src + '"',
                    'src="' + new_src + '"'
                )
                changed = True

    if changed:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # Extract just the filename for display
        rel_path = os.path.relpath(html_path, start=os.path.dirname(project_root) + os.sep)
        print(f"  Updated HTML: {rel_path}")

    return changed


def main():
    project_root = 'T:/!projects/IMAGE HOSTING/studiosoctave-images'
    # Verify path exists
    if not os.path.exists(project_root):
        # Try with fixed path
        project_root = 'T:/!projects/IMAGE HOSTING/studiosoctave-images'.replace('!', '')
    
    print(f"Project root: {project_root}")

    # Find all image files
    image_files = find_image_files(project_root)
    print(f"Found {len(image_files)} image files")

    # Compress each image
    compressed_count = 0
    for img_path in image_files:
        result = compress_image(img_path, project_root)
        if result:
            compressed_count += 1

    print(f"\nCompressed {compressed_count} images")

    # Find all HTML files and update image references
    html_files = []
    for root, dirs, files in os.walk(project_root):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))

    print(f"Found {len(html_files)} HTML files")

    updated_count = 0
    for html_path in html_files:
        if update_html_references(html_path, project_root):
            updated_count += 1

    print(f"\nUpdated {updated_count} HTML files")


if __name__ == '__main__':
    main()