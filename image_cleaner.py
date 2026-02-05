"""
Media Folder Cleaner - A lightweight Windows desktop application
for quickly cleaning image and video folders using keyboard controls.
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Try to import cv2 for video support
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ImageCleaner:
    """Main application class for the media folder cleaner."""

    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')
    VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.m4v')
    TRASH_FOLDER = '_trash'

    @property
    def SUPPORTED_EXTENSIONS(self):
        """Return all supported extensions (images + videos if cv2 available)."""
        if CV2_AVAILABLE:
            return self.IMAGE_EXTENSIONS + self.VIDEO_EXTENSIONS
        return self.IMAGE_EXTENSIONS

    def __init__(self, root):
        self.root = root
        self.root.title("Media Folder Cleaner")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')

        # State variables
        self.folder_path = None
        self.images = []
        self.current_index = 0
        self.current_photo = None  # Keep reference to prevent garbage collection
        self.trash_history = []  # Stack of (original_path, trash_path, original_index) for undo

        # Setup UI
        self._setup_ui()
        self._bind_keys()

        # Start by selecting a folder
        self.root.after(100, self.select_folder)

    def _setup_ui(self):
        """Setup the user interface components."""
        # Top frame for info and controls
        self.top_frame = tk.Frame(self.root, bg='#2d2d2d', pady=10)
        self.top_frame.pack(fill=tk.X)

        # Folder label
        self.folder_label = tk.Label(
            self.top_frame,
            text="No folder selected",
            fg='#cccccc',
            bg='#2d2d2d',
            font=('Segoe UI', 10)
        )
        self.folder_label.pack(side=tk.LEFT, padx=20)

        # Counter label
        self.counter_label = tk.Label(
            self.top_frame,
            text="0 / 0",
            fg='#ffffff',
            bg='#2d2d2d',
            font=('Segoe UI', 12, 'bold')
        )
        self.counter_label.pack(side=tk.RIGHT, padx=20)

        # Image display area
        self.image_frame = tk.Frame(self.root, bg='#1e1e1e')
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image_label = tk.Label(
            self.image_frame,
            bg='#1e1e1e',
            anchor='center'
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Filename label
        self.filename_label = tk.Label(
            self.root,
            text="",
            fg='#888888',
            bg='#1e1e1e',
            font=('Segoe UI', 9)
        )
        self.filename_label.pack(pady=(0, 5))

        # Bottom frame for instructions
        self.bottom_frame = tk.Frame(self.root, bg='#2d2d2d', pady=8)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        instructions = "SPACE → Trash  |  ENTER → Next  |  BACKSPACE → Previous  |  Ctrl+Z → Undo  |  Ctrl+O → Open folder"
        self.instructions_label = tk.Label(
            self.bottom_frame,
            text=instructions,
            fg='#888888',
            bg='#2d2d2d',
            font=('Segoe UI', 9)
        )
        self.instructions_label.pack()

        # Bind resize event
        self.image_frame.bind('<Configure>', self._on_resize)

    def _bind_keys(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<space>', self._move_to_trash)
        self.root.bind('<Return>', self._next_image)
        self.root.bind('<BackSpace>', self._previous_image)
        self.root.bind('<Control-z>', self._undo_trash)
        self.root.bind('<Control-o>', lambda e: self.select_folder())
        self.root.bind('<Escape>', lambda e: self.root.quit())

    def select_folder(self):
        """Open folder picker dialog and load images."""
        folder = filedialog.askdirectory(title="Select Media Folder")
        if not folder:
            if not self.folder_path:
                # No folder was ever selected, show message
                self._show_no_folder_message()
            return

        self.folder_path = folder
        self._load_images()

    def _load_images(self):
        """Load all supported images from the selected folder."""
        self.images = []
        self.current_index = 0
        self.trash_history = []  # Clear undo history for new folder

        if not self.folder_path or not os.path.isdir(self.folder_path):
            return

        # Get all image files
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(self.SUPPORTED_EXTENSIONS):
                full_path = os.path.join(self.folder_path, filename)
                if os.path.isfile(full_path):
                    self.images.append(full_path)

        # Sort images alphabetically
        self.images.sort(key=lambda x: os.path.basename(x).lower())

        # Update folder label
        folder_name = os.path.basename(self.folder_path)
        self.folder_label.config(text=f"📁 {folder_name}")

        if self.images:
            self._display_current_image()
        else:
            self._show_empty_folder_message()

    def _ensure_trash_folder(self):
        """Create the _trash subfolder if it doesn't exist."""
        if not self.folder_path:
            return None

        trash_path = os.path.join(self.folder_path, self.TRASH_FOLDER)
        if not os.path.exists(trash_path):
            os.makedirs(trash_path)
        return trash_path

    def _display_current_image(self):
        """Display the current image/video scaled to fit the window."""
        if not self.images or self.current_index >= len(self.images):
            self._show_complete_message()
            return

        file_path = self.images[self.current_index]

        # Update counter
        self.counter_label.config(text=f"{self.current_index + 1} / {len(self.images)}")

        # Update filename with video indicator if applicable
        filename = os.path.basename(file_path)
        if self._is_video(file_path) and CV2_AVAILABLE:
            duration = self._get_video_duration(file_path)
            if duration:
                filename = f"[VIDEO {duration}] {filename}"
            else:
                filename = f"[VIDEO] {filename}"
        self.filename_label.config(text=filename)

        try:
            # Load and display image/video thumbnail
            self._load_and_display_image(file_path)
        except Exception as e:
            self.image_label.config(image='', text=f"Error loading file:\n{str(e)}")
            self.current_photo = None

    def _is_video(self, file_path):
        """Check if the file is a video."""
        return file_path.lower().endswith(self.VIDEO_EXTENSIONS)

    def _load_video_thumbnail(self, video_path):
        """Extract a frame from video as thumbnail using OpenCV."""
        cap = cv2.VideoCapture(video_path)
        
        # Try to get a frame from 1 second in, or first frame if video is short
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if fps > 0 and total_frames > fps:
            # Go to 1 second mark
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps))
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise Exception("Could not read video frame")
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        return Image.fromarray(frame_rgb)

    def _get_video_duration(self, video_path):
        """Get video duration as formatted string."""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if fps > 0:
                duration_sec = frame_count / fps
                minutes = int(duration_sec // 60)
                seconds = int(duration_sec % 60)
                return f"{minutes:02d}:{seconds:02d}"
        except:
            pass
        return ""

    def _load_and_display_image(self, file_path):
        """Load an image or video thumbnail and display it scaled to fit."""
        # Get available space
        self.image_frame.update_idletasks()
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        if frame_width < 10 or frame_height < 10:
            frame_width = 900
            frame_height = 500

        # Load image or video thumbnail
        is_video = self._is_video(file_path)
        
        if is_video and CV2_AVAILABLE:
            image = self._load_video_thumbnail(file_path)
        else:
            image = Image.open(file_path)
            
            # Handle EXIF orientation for images
            try:
                from PIL import ExifTags
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = image._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation)
                    if orientation_value == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation_value == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation_value == 8:
                        image = image.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass

        # Calculate scaling
        img_width, img_height = image.size
        scale = min(frame_width / img_width, frame_height / img_height)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # Resize image
        if new_width > 0 and new_height > 0:
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        self.current_photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.current_photo, text='')

    def _on_resize(self, event):
        """Handle window resize by redisplaying the current image."""
        if self.images and self.current_index < len(self.images):
            self._display_current_image()

    def _move_to_trash(self, event=None):
        """Move current image to the _trash folder."""
        if not self.images or self.current_index >= len(self.images):
            return

        trash_path = self._ensure_trash_folder()
        if not trash_path:
            return

        image_path = self.images[self.current_index]
        filename = os.path.basename(image_path)
        destination = os.path.join(trash_path, filename)

        # Handle filename conflicts
        if os.path.exists(destination):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination):
                destination = os.path.join(trash_path, f"{base}_{counter}{ext}")
                counter += 1

        try:
            shutil.move(image_path, destination)
            
            # Save to history for undo
            self.trash_history.append((image_path, destination, self.current_index))
            
            # Remove from list
            self.images.pop(self.current_index)

            # Adjust index if needed
            if self.current_index >= len(self.images):
                self.current_index = max(0, len(self.images) - 1)

            self._display_current_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file:\n{str(e)}")

    def _undo_trash(self, event=None):
        """Restore the last trashed image back to the folder."""
        if not self.trash_history:
            return

        original_path, trash_path, original_index = self.trash_history.pop()

        # Check if file still exists in trash
        if not os.path.exists(trash_path):
            messagebox.showwarning("Undo Failed", "File no longer exists in trash.")
            return

        try:
            shutil.move(trash_path, original_path)
            
            # Re-insert into list at original position
            self.images.insert(original_index, original_path)
            self.current_index = original_index
            
            self._display_current_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore file:\n{str(e)}")

    def _next_image(self, event=None):
        """Show the next image."""
        if not self.images:
            return

        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self._display_current_image()
        else:
            self._show_complete_message()

    def _previous_image(self, event=None):
        """Show the previous image."""
        if not self.images:
            return

        if self.current_index > 0:
            self.current_index -= 1
            self._display_current_image()

    def _show_no_folder_message(self):
        """Show message when no folder is selected."""
        self.image_label.config(
            image='',
            text="No folder selected.\n\nPress Ctrl+O to open a folder.",
            fg='#888888',
            font=('Segoe UI', 14)
        )
        self.current_photo = None
        self.counter_label.config(text="0 / 0")
        self.filename_label.config(text="")

    def _show_empty_folder_message(self):
        """Show message when folder has no media files."""
        if CV2_AVAILABLE:
            formats = "Images: JPG, PNG, WEBP, BMP, GIF\nVideos: MP4, AVI, MOV, MKV, WEBM"
        else:
            formats = "Images: JPG, PNG, WEBP, BMP, GIF\n(Install opencv-python for video support)"
        
        self.image_label.config(
            image='',
            text=f"No media files found in this folder.\n\nSupported formats:\n{formats}\n\nPress Ctrl+O to select another folder.",
            fg='#888888',
            font=('Segoe UI', 14)
        )
        self.current_photo = None
        self.counter_label.config(text="0 / 0")
        self.filename_label.config(text="")

    def _show_complete_message(self):
        """Show message when all files have been processed."""
        self.image_label.config(
            image='',
            text="All files reviewed!\n\nPress Ctrl+O to select another folder\nor BACKSPACE to go back.",
            fg='#888888',
            font=('Segoe UI', 14)
        )
        self.current_photo = None
        self.counter_label.config(text=f"{len(self.images)} / {len(self.images)}" if self.images else "0 / 0")
        self.filename_label.config(text="")


def main():
    """Application entry point."""
    root = tk.Tk()

    # Set app icon (if available)
    try:
        root.iconbitmap(default='')
    except:
        pass

    # Center window on screen
    root.update_idletasks()
    width = 1000
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Create application
    app = ImageCleaner(root)

    # Run main loop
    root.mainloop()


if __name__ == "__main__":
    main()
