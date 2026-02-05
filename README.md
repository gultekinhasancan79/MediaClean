# Media Folder Cleaner

A lightweight Windows desktop application for quickly cleaning image and video folders using keyboard controls. Files are moved to a `_trash` subfolder—nothing is permanently deleted.

## Features

- **Images**: JPG, JPEG, PNG, WEBP, BMP, GIF
- **Videos**: MP4, AVI, MOV, MKV, WEBM, WMV, FLV, M4V (thumbnail preview)
- Keyboard-only workflow for fast browsing
- Undo support to restore files from trash

## Requirements

- Python 3.x
- Pillow (PIL)
- opencv-python (for video support)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python image_cleaner.py
```

1. Select a folder via the file picker (or press Ctrl+O)
2. Browse through images and videos one by one
3. Use keyboard shortcuts to manage files

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **SPACE** | Move current file to `_trash` folder |
| **ENTER** | Skip and show next file |
| **BACKSPACE** | Go to previous file |
| **Ctrl+Z** | Undo last trash (restore from `_trash`) |
| **Ctrl+O** | Open folder picker |
| **ESC** | Quit application |

## How It Works

- Silenced files are moved to a `_trash` subfolder inside the selected folder
- No permanent deletion—you can manually restore or delete from `_trash`
- Videos show a thumbnail from the first second of playback

## License

MIT
