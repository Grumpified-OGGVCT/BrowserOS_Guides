#!/usr/bin/env python3
"""
Convert PNG screenshots to WebP format for better compression
"""
import os
from pathlib import Path
from PIL import Image

def convert_to_webp(png_path, quality=85):
    """Convert a PNG image to WebP format"""
    webp_path = png_path.with_suffix('.webp')
    
    # Open and convert
    with Image.open(png_path) as img:
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Save as WebP
        img.save(webp_path, 'WebP', quality=quality, method=6)
    
    # Get file sizes
    png_size = png_path.stat().st_size
    webp_size = webp_path.stat().st_size
    reduction = ((png_size - webp_size) / png_size) * 100
    
    print(f"✅ {png_path.name}")
    print(f"   PNG:  {png_size:,} bytes")
    print(f"   WebP: {webp_size:,} bytes")
    print(f"   Saved: {reduction:.1f}%")
    
    return webp_path

def main():
    # Get screenshots directory
    screenshots_dir = Path(__file__).parent.parent / 'docs' / 'screenshots'
    
    if not screenshots_dir.exists():
        print(f"❌ Screenshots directory not found: {screenshots_dir}")
        return
    
    print(f"Converting screenshots in: {screenshots_dir}\n")
    
    # Convert all PNG files
    png_files = list(screenshots_dir.glob('*.png'))
    
    if not png_files:
        print("No PNG files found")
        return
    
    total_png_size = 0
    total_webp_size = 0
    
    for png_file in sorted(png_files):
        png_size = png_file.stat().st_size
        webp_file = convert_to_webp(png_file, quality=85)
        webp_size = webp_file.stat().st_size
        
        total_png_size += png_size
        total_webp_size += webp_size
        print()
    
    print("=" * 60)
    print(f"Total PNG size:  {total_png_size:,} bytes ({total_png_size / 1024:.1f} KB)")
    print(f"Total WebP size: {total_webp_size:,} bytes ({total_webp_size / 1024:.1f} KB)")
    print(f"Total reduction: {((total_png_size - total_webp_size) / total_png_size) * 100:.1f}%")
    print("=" * 60)
    
    print("\n📝 Note: PNG files kept for compatibility. Update README.md to use .webp extensions.")

if __name__ == '__main__':
    main()
