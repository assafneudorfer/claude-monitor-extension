# Claude Monitor Icons

Icons generated using Claude branding colors (orange/purple gradient).

## Generated Files

### Extension Icons
- `icon16.png` - 16x16px - Toolbar icon
- `icon48.png` - 48x48px - Extension management
- `icon128.png` - 128x128px - Chrome Web Store

### Notification Icons
- `success.png` - Green with checkmark (✓)
- `error.png` - Red with X mark (✗)
- `warning.png` - Orange with exclamation (!)
- `info.png` - Blue with i symbol (ℹ)

## Design

All icons feature:
- **Circular design** with solid colored backgrounds
- **White symbols** for clarity at all sizes
- **Claude orange (#D97706)** for main icon with notification dot
- **Priority colors** for notification states

## Main Icon

The extension icon features:
- Orange gradient background (Claude branding)
- White "C" letter for Claude
- Red notification dot in top-right corner

## Regenerating Icons

If you want to regenerate or modify the icons:

### Option 1: From SVG (Best Quality)

1. Install a converter:
   ```bash
   brew install imagemagick
   # or
   pip3 install cairosvg
   ```

2. Run:
   ```bash
   python3 generate_icons.py
   ```

### Option 2: Simple PNG (Current)

Uses PIL/Pillow to create icons programmatically:

```bash
pip3 install Pillow
python3 generate_simple_icons.py
```

### Option 3: Edit SVG Files

The SVG source files are included:
- `icon.svg`
- `success.svg`
- `error.svg`
- `warning.svg`
- `info.svg`

Edit these in any vector graphics editor (Figma, Illustrator, Inkscape) then regenerate PNGs.

## Color Palette

```
Main Icon:    #D97706 (Orange)
Success:      #10B981 (Green)
Error:        #EF4444 (Red)
Warning:      #F59E0B (Orange)
Info:         #3B82F6 (Blue)
Notification: #EF4444 (Red dot)
```

## File Sizes

```
icon16.png:   ~200 bytes
icon48.png:   ~450 bytes
icon128.png:  ~1.1 KB
success.png:  ~1.0 KB
error.png:    ~1.1 KB
warning.png:  ~860 bytes
info.png:     ~870 bytes
```

Total: ~5.5 KB for all icons

## Usage in Extension

Icons are referenced in `manifest.json`:

```json
{
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "action": {
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

And in `background.js` for notifications:

```javascript
const iconMap = {
  success: 'icons/success.png',
  error: 'icons/error.png',
  warning: 'icons/warning.png',
  info: 'icons/info.png'
};
```
