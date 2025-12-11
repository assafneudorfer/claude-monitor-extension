#!/usr/bin/env python3
"""
Generate simple PNG icons without external dependencies
Creates solid color icons with symbols using PIL/Pillow
"""

import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Colors matching Claude branding
COLORS = {
    'icon': '#D97706',      # Orange (Claude color)
    'success': '#10B981',   # Green
    'error': '#EF4444',     # Red
    'warning': '#F59E0B',   # Orange
    'info': '#3B82F6'       # Blue
}


def create_icon_pil(name, size):
    """Create icon using PIL"""
    color = COLORS.get(name, '#D97706')

    # Create image with rounded corners
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw circle background
    margin = size // 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=color
    )

    # Draw symbol
    white = '#FFFFFF'
    line_width = max(2, size // 16)

    if name == 'success':
        # Checkmark
        points = [
            (size * 0.3, size * 0.5),
            (size * 0.45, size * 0.65),
            (size * 0.7, size * 0.35)
        ]
        draw.line(points, fill=white, width=line_width, joint='curve')

    elif name == 'error':
        # X mark
        offset = size * 0.3
        draw.line(
            [(offset, offset), (size - offset, size - offset)],
            fill=white, width=line_width
        )
        draw.line(
            [(size - offset, offset), (offset, size - offset)],
            fill=white, width=line_width
        )

    elif name == 'warning':
        # Exclamation mark
        center_x = size // 2
        draw.line(
            [(center_x, size * 0.3), (center_x, size * 0.6)],
            fill=white, width=line_width
        )
        dot_size = line_width
        draw.ellipse(
            [center_x - dot_size, size * 0.7, center_x + dot_size, size * 0.7 + dot_size * 2],
            fill=white
        )

    elif name == 'info':
        # i symbol
        center_x = size // 2
        dot_size = line_width
        draw.ellipse(
            [center_x - dot_size, size * 0.3, center_x + dot_size, size * 0.3 + dot_size * 2],
            fill=white
        )
        draw.line(
            [(center_x, size * 0.45), (center_x, size * 0.75)],
            fill=white, width=line_width
        )

    else:  # icon
        # Draw "C" for Claude
        center = size // 2
        radius = size * 0.35
        thickness = max(2, size // 12)

        # Draw C using arc (simplified as a partial circle)
        for angle in range(45, 315, 5):
            import math
            x = center + radius * math.cos(math.radians(angle))
            y = center + radius * math.sin(math.radians(angle))
            draw.ellipse(
                [x - thickness, y - thickness, x + thickness, y + thickness],
                fill=white
            )

        # Add notification dot
        dot_x = size * 0.7
        dot_y = size * 0.3
        dot_size = size * 0.12
        draw.ellipse(
            [dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size],
            fill='#EF4444'
        )

    return img


def main():
    if not HAS_PIL:
        print("❌ PIL/Pillow not found!")
        print()
        print("Please install Pillow:")
        print("  pip3 install Pillow")
        print()
        print("Or install an SVG converter and run generate_icons.py instead")
        sys.exit(1)

    print("🎨 Generating PNG icons with PIL...")
    print()

    generated = 0

    # Generate main extension icons
    for size in [16, 48, 128]:
        png_file = SCRIPT_DIR / f'icon{size}.png'
        img = create_icon_pil('icon', size)
        img.save(png_file, 'PNG')
        print(f"✓ Generated icon{size}.png")
        generated += 1

    # Generate notification icons (128x128)
    for name in ['success', 'error', 'warning', 'info']:
        png_file = SCRIPT_DIR / f'{name}.png'
        img = create_icon_pil(name, 128)
        img.save(png_file, 'PNG')
        print(f"✓ Generated {name}.png")
        generated += 1

    print()
    print(f"🎉 Done! Generated {generated} PNG icons")


if __name__ == '__main__':
    main()
