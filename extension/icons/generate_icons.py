#!/usr/bin/env python3
"""
Generate PNG icons from SVG files for Chrome extension
Supports multiple conversion methods based on available tools
"""

import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SIZES = {
    'icon': [16, 48, 128],  # Extension icons
    'success': [128],        # Notification icons
    'error': [128],
    'warning': [128],
    'info': [128]
}


def check_tool(command):
    """Check if a command-line tool is available"""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_with_imagemagick(svg_file, png_file, size):
    """Convert SVG to PNG using ImageMagick"""
    cmd = [
        'convert',
        '-background', 'none',
        '-density', '300',
        '-resize', f'{size}x{size}',
        str(svg_file),
        str(png_file)
    ]
    subprocess.run(cmd, check=True)


def convert_with_inkscape(svg_file, png_file, size):
    """Convert SVG to PNG using Inkscape"""
    cmd = [
        'inkscape',
        str(svg_file),
        '--export-type=png',
        f'--export-filename={png_file}',
        f'--export-width={size}',
        f'--export-height={size}'
    ]
    subprocess.run(cmd, check=True)


def convert_with_rsvg(svg_file, png_file, size):
    """Convert SVG to PNG using rsvg-convert"""
    cmd = [
        'rsvg-convert',
        '-w', str(size),
        '-h', str(size),
        '-o', str(png_file),
        str(svg_file)
    ]
    subprocess.run(cmd, check=True)


def convert_with_cairosvg(svg_file, png_file, size):
    """Convert SVG to PNG using cairosvg Python library"""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_file),
            write_to=str(png_file),
            output_width=size,
            output_height=size
        )
        return True
    except ImportError:
        return False


def main():
    print("🎨 Generating PNG icons from SVG files...")
    print()

    # Detect available conversion tool
    converter = None
    if check_tool('convert'):
        print("✓ Using ImageMagick (convert)")
        converter = convert_with_imagemagick
    elif check_tool('inkscape'):
        print("✓ Using Inkscape")
        converter = convert_with_inkscape
    elif check_tool('rsvg-convert'):
        print("✓ Using rsvg-convert")
        converter = convert_with_rsvg
    else:
        # Try Python cairosvg
        svg_file = SCRIPT_DIR / 'icon.svg'
        png_file = SCRIPT_DIR / 'test.png'
        if convert_with_cairosvg(svg_file, png_file, 16):
            print("✓ Using cairosvg (Python library)")
            converter = convert_with_cairosvg
            png_file.unlink()  # Remove test file
        else:
            print("❌ No SVG conversion tool found!")
            print()
            print("Please install one of:")
            print("  • ImageMagick:  brew install imagemagick")
            print("  • Inkscape:     brew install inkscape")
            print("  • rsvg-convert: brew install librsvg")
            print("  • cairosvg:     pip3 install cairosvg")
            sys.exit(1)

    print()
    generated = 0

    # Generate icons
    for name, sizes in SIZES.items():
        svg_file = SCRIPT_DIR / f'{name}.svg'

        if not svg_file.exists():
            print(f"⚠️  Skipping {name}.svg (not found)")
            continue

        for size in sizes:
            if name == 'icon':
                png_file = SCRIPT_DIR / f'icon{size}.png'
            else:
                png_file = SCRIPT_DIR / f'{name}.png'

            try:
                converter(svg_file, png_file, size)
                print(f"✓ Generated {png_file.name} ({size}x{size})")
                generated += 1
            except Exception as e:
                print(f"✗ Failed to generate {png_file.name}: {e}")

    print()
    print(f"🎉 Done! Generated {generated} PNG icon(s)")
    print()
    print("Generated files:")
    for f in sorted(SCRIPT_DIR.glob('*.png')):
        size_kb = f.stat().st_size / 1024
        print(f"  • {f.name} ({size_kb:.1f} KB)")


if __name__ == '__main__':
    main()
