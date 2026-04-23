#!/usr/bin/env python3
"""
Template Download Automation Script

Downloads official LaTeX style files from authoritative sources for scientific
paper formatting across multiple conferences.

Usage:
    python download_templates.py --all
    python download_templates.py --conference neurips
    python download_templates.py --conference acl --force
    python download_templates.py --all --dry-run
"""

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional, Tuple

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)


class TemplateDownloader:
    """Manages downloading and extracting LaTeX conference templates."""

    # Download sources with expected file sizes (bytes) for verification
    SOURCES = {
        "neurips": {
            "url": "https://media.neurips.cc/Conferences/NeurIPS2024/Styles/neurips_2024.zip",
            "type": "zip",
            "min_size": 10_000,  # At least 10KB
            "description": "NeurIPS 2024 LaTeX style files",
        },
        "acl": {
            "url": "https://github.com/acl-org/acl-style-files.git",
            "type": "git",
            "description": "ACL LaTeX style files (official GitHub repo)",
        },
        "ieee": {
            "url": "https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip",
            "type": "zip",
            "min_size": 50_000,  # At least 50KB
            "description": "IEEE LaTeX style files (IEEEtran class)",
        },
        "acm": {
            "url": "https://www.acm.org/binaries/content/assets/publications/consolidated-tex-template/acmart-primary.zip",
            "type": "zip",
            "min_size": 100_000,  # At least 100KB
            "description": "ACM LaTeX style files (acmart class)",
        },
        "icml": {
            "url": None,
            "type": "manual",
            "description": "ICML style files (manual download required)",
            "instructions": """
ICML templates require manual download:
1. Visit: https://icml.cc/Conferences/2024/StyleAuthorInstructions
2. Download the LaTeX style package
3. Extract to: templates/icml/
4. Ensure icml2024.sty is present
""",
        },
    }

    def __init__(self, templates_dir: Path, dry_run: bool = False, force: bool = False):
        """
        Initialize the template downloader.

        Args:
            templates_dir: Base directory for storing templates
            dry_run: If True, show what would be downloaded without downloading
            force: If True, re-download even if files exist
        """
        self.templates_dir = templates_dir
        self.dry_run = dry_run
        self.force = force
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.

        Returns:
            Configured requests session
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _check_directory_exists(self, conference: str) -> bool:
        """
        Check if conference template directory already exists.

        Args:
            conference: Conference name

        Returns:
            True if directory exists and contains files
        """
        conf_dir = self.templates_dir / conference
        if conf_dir.exists() and any(conf_dir.iterdir()):
            return True
        return False

    def _download_file(
        self, url: str, output_path: Path, min_size: Optional[int] = None
    ) -> bool:
        """
        Download a file with progress indication.

        Args:
            url: URL to download from
            output_path: Where to save the file
            min_size: Minimum expected file size for verification

        Returns:
            True if download successful, False otherwise
        """
        try:
            print(f"Downloading from: {url}")
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            block_size = 8192
            downloaded = 0

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            print(
                                f"\rProgress: {downloaded}/{total_size} bytes ({percent:.1f}%)",
                                end="",
                            )
            print()  # New line after progress

            # Verify file size
            actual_size = output_path.stat().st_size
            if min_size and actual_size < min_size:
                print(
                    f"⚠️  Warning: Downloaded file is smaller than expected "
                    f"({actual_size} < {min_size} bytes)"
                )
                return False

            print(
                f"✅ Downloaded successfully: {output_path.name} ({actual_size} bytes)"
            )
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Download failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def _extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """
        Extract a ZIP file.

        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to

        Returns:
            True if extraction successful, False otherwise
        """
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"✅ Extracted to: {extract_to}")
            return True
        except zipfile.BadZipFile:
            print(f"❌ Error: {zip_path} is not a valid ZIP file")
            return False
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False

    def _clone_git_repo(self, url: str, target_dir: Path) -> bool:
        """
        Clone a Git repository.

        Args:
            url: Git repository URL
            target_dir: Where to clone the repository

        Returns:
            True if cloning successful, False otherwise
        """
        try:
            # Check if git is available
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
            )

            target_dir.mkdir(parents=True, exist_ok=True)

            print(f"Cloning from: {url}")
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✅ Cloned successfully to: {target_dir}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Git clone failed: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ Error: git command not found. Please install Git.")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def download_conference(self, conference: str) -> bool:
        """
        Download templates for a specific conference.

        Args:
            conference: Conference name (neurips, icml, acl, ieee, acm)

        Returns:
            True if download successful, False otherwise
        """
        if conference not in self.SOURCES:
            print(f"❌ Unknown conference: {conference}")
            print(f"Available: {', '.join(self.SOURCES.keys())}")
            return False

        source = self.SOURCES[conference]
        conf_dir = self.templates_dir / conference

        print(f"\n{'=' * 60}")
        print(f"Conference: {conference.upper()}")
        print(f"Description: {source['description']}")
        print(f"{'=' * 60}")

        # Check if already exists
        if self._check_directory_exists(conference) and not self.force:
            print(f"✓ Templates already exist in: {conf_dir}")
            print("  Use --force to re-download")
            return True

        # Handle dry-run mode
        if self.dry_run:
            print(f"[DRY RUN] Would download to: {conf_dir}")
            if source["type"] == "manual":
                print("[DRY RUN] Manual download required:")
                print(source["instructions"])
            else:
                print(f"[DRY RUN] Would download from: {source['url']}")
            return True

        # Handle manual download
        if source["type"] == "manual":
            print(source["instructions"])
            return False

        # Clean existing directory if force mode
        if self.force and conf_dir.exists():
            print(f"Removing existing directory: {conf_dir}")
            shutil.rmtree(conf_dir)

        # Download based on type
        if source["type"] == "zip":
            # Download ZIP file
            temp_zip = self.templates_dir / f"{conference}_temp.zip"
            if not self._download_file(source["url"], temp_zip, source.get("min_size")):
                return False

            # Extract
            if not self._extract_zip(temp_zip, conf_dir):
                return False

            # Clean up temp file
            temp_zip.unlink()

        elif source["type"] == "git":
            # Clone repository
            if not self._clone_git_repo(source["url"], conf_dir):
                return False

        print(f"✅ {conference.upper()} templates ready in: {conf_dir}")
        return True

    def download_all(self) -> Tuple[int, int]:
        """
        Download templates for all conferences.

        Returns:
            Tuple of (successful_count, total_count)
        """
        print("\n" + "=" * 60)
        print("DOWNLOADING ALL CONFERENCE TEMPLATES")
        print("=" * 60)

        successful = 0
        total = 0

        for conference in self.SOURCES.keys():
            total += 1
            if self.download_conference(conference):
                successful += 1

        print("\n" + "=" * 60)
        print(f"SUMMARY: {successful}/{total} conferences downloaded successfully")
        print("=" * 60)

        return successful, total


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Download LaTeX style files for scientific paper formatting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                      Download all available templates
  %(prog)s --conference neurips       Download NeurIPS templates only
  %(prog)s --conference acl --force   Re-download ACL templates
  %(prog)s --all --dry-run            Show what would be downloaded
        """,
    )

    parser.add_argument(
        "--conference",
        "-c",
        choices=["neurips", "icml", "acl", "ieee", "acm"],
        help="Download templates for a specific conference",
    )

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Download all available templates",
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Re-download even if files already exist",
    )

    parser.add_argument(
        "--templates-dir",
        "-d",
        type=Path,
        default=Path(__file__).parent.parent / "templates",
        help="Directory to store templates (default: ../templates)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.conference:
        parser.error("Must specify either --all or --conference")

    # Create downloader
    downloader = TemplateDownloader(
        templates_dir=args.templates_dir,
        dry_run=args.dry_run,
        force=args.force,
    )

    # Execute download
    success = True
    if args.all:
        successful, total = downloader.download_all()
        success = successful == total
    else:
        success = downloader.download_conference(args.conference)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
