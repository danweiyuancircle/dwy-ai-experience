"""Tests for extracting the current version section from changelog files."""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("extract_changelog_section.py")


class ExtractChangelogSectionTests(unittest.TestCase):
    """Covers the release-note markdown extracted for a single version."""

    def run_script(self, changelog_text: str, version: str, release_name: str) -> str:
        """Writes a temporary changelog, runs the script, and returns stdout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "CHANGELOG.md"
            changelog_path.write_text(changelog_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(changelog_path), version, release_name],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout

    def test_extracts_only_requested_version_section(self) -> None:
        """Keeps the requested version content and excludes older versions."""
        output = self.run_script(
            textwrap.dedent(
                """\
                # create-dwy

                ## 0.13.7

                ### Patch Changes

                - fix current release

                ## 0.13.6

                ### Patch Changes

                - old release
                """
            ),
            "0.13.7",
            "create-dwy@0.13.7",
        )

        self.assertEqual(
            output,
            textwrap.dedent(
                """\
                ## create-dwy@0.13.7

                ### Patch Changes

                - fix current release
                """
            ),
        )

    def test_fails_when_version_section_is_missing(self) -> None:
        """Returns a non-zero exit code when the changelog lacks the version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "CHANGELOG.md"
            changelog_path.write_text("# pkg\n\n## 0.1.0\n\n- item\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(changelog_path), "0.2.0", "pkg@0.2.0"],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version section not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
