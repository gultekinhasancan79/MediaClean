<h1 align="center">MediaClean</h1>

<p align="center">
  A keyboard-first desktop utility for reviewing and cleaning large image and video folders quickly — without permanently deleting files.
</p>

<p align="center">
  <a href="https://github.com/gultekinhasancan79/MediaClean/actions/workflows/ci.yml"><img src="https://github.com/gultekinhasancan79/MediaClean/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tkinter-Desktop%20UI-4B8BBE" alt="Tkinter">
  <img src="https://img.shields.io/badge/Pillow-Image%20Processing-6C5CE7" alt="Pillow">
  <img src="https://img.shields.io/badge/OpenCV-Video%20Preview-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/License-MIT-2ea44f" alt="MIT License">
</p>

---

## Overview

MediaClean is a lightweight Windows desktop application built for one specific workflow: **review a large media folder as quickly as possible and move unwanted files out of the way with minimal friction**.

Instead of permanently deleting files, MediaClean moves them into a local `_trash` directory. The most recent move can be restored instantly with `Ctrl+Z`, making the cleanup workflow fast while remaining recoverable.

## Why I Built It

Large WhatsApp, Telegram, download, screenshot, and camera folders are tedious to clean using a traditional file manager. MediaClean reduces the interaction to a simple review loop:

**preview → decide → press one key → continue**

The application prioritizes keyboard control, large previews, safe file handling, and quick recovery from accidental actions.

## Features

- **Keyboard-first workflow** for fast media review
- **Image preview** for JPG, JPEG, PNG, WEBP, BMP, and GIF files
- **Video thumbnail support** for MP4, AVI, MOV, MKV, WEBM, WMV, FLV, and M4V when OpenCV is installed
- **Video duration display** alongside the filename
- **Safe trash workflow** — files are moved into a `_trash` folder instead of being permanently deleted
- **Undo support** with an in-memory history stack
- **Filename conflict handling** when a file with the same name already exists in `_trash`
- **EXIF orientation correction** for rotated camera images
- **Responsive previews** that rescale when the application window changes size
- **Alphabetical media ordering** for predictable navigation

## Workflow

1. Launch MediaClean.
2. Select a folder from the file picker.
3. Review each image or video preview.
4. Press `Space` to move unwanted media into `_trash`.
5. Press `Enter` to keep the current file and continue.
6. Use `Ctrl+Z` if the last file was moved by mistake.

## Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `Space` | Move the current file to `_trash` |
| `Enter` | Keep the current file and show the next item |
| `Backspace` | Go to the previous item |
| `Ctrl+Z` | Restore the most recently trashed file |
| `Ctrl+O` | Select another folder |
| `Esc` | Quit the application |

## Safety Model

MediaClean deliberately avoids destructive deletion during the review flow.

```text
selected folder/
├── photo_001.jpg
├── video_001.mp4
└── _trash/
    └── photo_002.jpg
```

When `Space` is pressed, the current file is moved into `_trash`. If the destination filename already exists, MediaClean generates a conflict-safe name such as `photo_002_1.jpg` instead of overwriting the existing file.

`Ctrl+Z` moves the latest trashed file back to its original location.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/gultekinhasancan79/MediaClean.git
cd MediaClean
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python image_cleaner.py
```

## Dependencies

The media-processing dependencies are pinned to the versions exercised by CI:

- **Pillow 10.4.0** — image loading and resizing
- **OpenCV 4.14.0.94 (`opencv-python`)** — video thumbnail and duration support
- **Tkinter** — desktop interface, included with most standard Python installations on Windows

CI currently runs on Python 3.12. If OpenCV is unavailable in a manual installation, MediaClean can still operate on image formats only.

## Testing

MediaClean includes dependency-free `unittest` coverage for the file-safety behavior that matters most during cleanup:

- moving the selected file into `_trash`,
- preserving undo metadata,
- generating a conflict-safe destination instead of overwriting an existing trashed file,
- and restoring the most recently trashed file back to its original location.

The tests exercise the production `_move_to_trash` and `_undo_trash` methods without opening a Tk window.

Run them locally with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also installs the pinned dependencies, compiles the application and tests, verifies Pillow/OpenCV imports, imports the application module, and runs the file-operation test suite.

## Technical Notes

The application is intentionally small and local-first. There is no server, account system, cloud storage, or background upload. Media files are read directly from the selected folder and file operations happen on the local filesystem.

The main application state tracks:

- the selected folder,
- the sorted media list,
- the current index,
- the current rendered preview,
- and a stack of trash operations used for undo.

## Current Scope

MediaClean currently focuses on a fast single-folder desktop workflow. Potential future improvements include persistent undo history, recursive folder scanning, configurable keyboard bindings, packaging as a standalone executable, richer video previews, and broader image/video fixture coverage.

## License

MIT
