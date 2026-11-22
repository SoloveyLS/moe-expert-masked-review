from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import download_benchmark as target


class DownloaderTests(unittest.TestCase):
    def test_show_has_no_side_effects(self):
        out = io.StringIO()
        with patch.object(target, "_git") as git, redirect_stdout(out):
            target.main(["--show"])
        git.assert_not_called()
        self.assertIn(target.REVISION, out.getvalue())

    def test_requires_exact_fetched_commit(self):
        with patch.object(target, "_git", return_value=SimpleNamespace(stdout="0" * 40)) as git:
            with self.assertRaisesRegex(RuntimeError, "pinned revision"):
                target._snapshot("repo", "archive.tar")
        self.assertEqual(git.call_count, 3)
        self.assertEqual(git.call_args_list[1].args[-2:], (target.REPO, target.REVISION))

    def test_pinned_archive_and_existing_output(self):
        with patch.object(target, "_git", return_value=SimpleNamespace(stdout=target.REVISION)) as git:
            target._snapshot("repo", "archive.tar")
        self.assertEqual(git.call_args.args[-1], target.REVISION)
        with tempfile.TemporaryDirectory() as path:
            out = Path(path) / "snapshot.tar"
            out.write_text("existing")
            with patch.object(target, "_snapshot") as snapshot:
                with self.assertRaises(FileExistsError):
                    target.download(out)
            snapshot.assert_not_called()
            self.assertEqual(out.read_text(), "existing")

    def test_writes_only_copied_archive(self):
        with tempfile.TemporaryDirectory() as path:
            out = Path(path) / "snapshot.tar"
            with patch.object(target, "_snapshot", side_effect=lambda repo, tar: tar.write_bytes(b"fixture")):
                self.assertEqual(target.download(out), out)
            self.assertEqual(out.read_bytes(), b"fixture")
            self.assertEqual(list(out.parent.iterdir()), [out])


if __name__ == "__main__":
    unittest.main()
