import tempfile
import unittest
from pathlib import Path

from image_cleaner import ImageCleaner


class MediaCleanFileOperationTests(unittest.TestCase):
    def make_app(self, folder: Path, files: list[Path]) -> ImageCleaner:
        # File operations do not require a live Tk window. Build a minimal
        # instance so the tests exercise the production move/undo methods
        # without opening a GUI in CI.
        app = object.__new__(ImageCleaner)
        app.folder_path = str(folder)
        app.images = [str(path) for path in files]
        app.current_index = 0
        app.trash_history = []
        app._display_current_image = lambda: None
        return app

    def test_move_to_trash_moves_file_and_records_undo_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "photo.jpg"
            source.write_bytes(b"image-data")
            app = self.make_app(folder, [source])

            app._move_to_trash()

            trashed = folder / "_trash" / "photo.jpg"
            self.assertFalse(source.exists())
            self.assertTrue(trashed.exists())
            self.assertEqual(app.images, [])
            self.assertEqual(len(app.trash_history), 1)
            original, destination, original_index = app.trash_history[-1]
            self.assertEqual(Path(original), source)
            self.assertEqual(Path(destination), trashed)
            self.assertEqual(original_index, 0)

    def test_move_to_trash_never_overwrites_existing_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "photo.jpg"
            source.write_bytes(b"new-file")
            trash = folder / "_trash"
            trash.mkdir()
            existing = trash / "photo.jpg"
            existing.write_bytes(b"existing-file")
            app = self.make_app(folder, [source])

            app._move_to_trash()

            conflict_safe = trash / "photo_1.jpg"
            self.assertEqual(existing.read_bytes(), b"existing-file")
            self.assertEqual(conflict_safe.read_bytes(), b"new-file")
            self.assertFalse(source.exists())

    def test_undo_restores_last_trashed_file_to_original_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "photo.jpg"
            source.write_bytes(b"restore-me")
            app = self.make_app(folder, [source])

            app._move_to_trash()
            app._undo_trash()

            self.assertTrue(source.exists())
            self.assertEqual(source.read_bytes(), b"restore-me")
            self.assertEqual(app.images, [str(source)])
            self.assertEqual(app.current_index, 0)
            self.assertEqual(app.trash_history, [])


if __name__ == "__main__":
    unittest.main()
