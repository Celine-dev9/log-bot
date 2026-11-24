"""
Unit tests and verification for the Human Code Reader Bot components.
Tests file scanning, asset filtering, VS Code binary discovery, and mouse math.
"""

import os
import shutil
import tempfile
import unittest

import config
import file_scanner
import human_mouse
import vscode_manager


class TestCodeScanner(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_code_reader_")

        # Create code files
        self.code_files = [
            "main.py",
            "server.js",
            "types.ts",
            "style.css",
            "config.json",
            "Dockerfile",
            os.path.join("src", "component.tsx"),
            os.path.join("src", "utils", "math.py"),
        ]
        for rel in self.code_files:
            p = os.path.join(self.test_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write("print('Hello test world')\n" * 15)

        # Create asset / image / binary files (MUST BE FILTERED OUT)
        self.asset_files = [
            "image.png",
            "photo.jpg",
            "favicon.ico",
            "graphic.svg",
            "sound.mp3",
            "movie.mp4",
            "manual.pdf",
            "archive.zip",
            "app.exe",
            "package-lock.json",
        ]
        for rel in self.asset_files:
            p = os.path.join(self.test_dir, rel)
            with open(p, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 20)

        # Create ignored directory files (MUST BE SKIPPED)
        self.ignored_files = [
            os.path.join("node_modules", "lib", "index.js"),
            os.path.join(".git", "hooks", "pre-commit.sh"),
            os.path.join("venv", "lib", "site.py"),
            os.path.join("dist", "bundle.js"),
        ]
        for rel in self.ignored_files:
            p = os.path.join(self.test_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write("console.log('ignored');\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scanner_includes_code_and_excludes_assets(self):
        scanned = file_scanner.scan_code_files(self.test_dir)
        scanned_rel_paths = {f["relative_path"].replace("\\", "/") for f in scanned}

        # 1. Check all valid code files are present
        for expected in self.code_files:
            norm_expected = expected.replace("\\", "/")
            self.assertIn(norm_expected, scanned_rel_paths, f"Missing code file: {expected}")

        # 2. Check that NO asset files are present
        for asset in self.asset_files:
            self.assertNotIn(asset, scanned_rel_paths, f"Asset was not excluded: {asset}")

        # 3. Check that ignored directories were skipped
        for ignored in self.ignored_files:
            norm_ignored = ignored.replace("\\", "/")
            self.assertNotIn(norm_ignored, scanned_rel_paths, f"Ignored directory file included: {ignored}")

        self.assertEqual(len(scanned), len(self.code_files))


class TestVSCodeDiscovery(unittest.TestCase):
    def test_find_vscode_binary(self):
        binary = vscode_manager.find_vscode_binary()
        self.assertTrue(os.path.exists(binary), f"Found binary does not exist: {binary}")
        self.assertTrue("code" in binary.lower(), f"Unexpected binary path: {binary}")


class TestHumanMouseMath(unittest.TestCase):
    def test_bezier_interpolation(self):
        # At t=0, should be p0
        self.assertAlmostEqual(human_mouse.cubic_bezier(10, 20, 30, 40, 0.0), 10.0)
        # At t=1, should be p3
        self.assertAlmostEqual(human_mouse.cubic_bezier(10, 20, 30, 40, 1.0), 40.0)
        # At t=0.5, midpoint
        mid = human_mouse.cubic_bezier(0, 50, 50, 100, 0.5)
        self.assertAlmostEqual(mid, 50.0)

    def test_cursor_pos(self):
        x, y = human_mouse.get_cursor_pos()
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)


if __name__ == "__main__":
    unittest.main()
