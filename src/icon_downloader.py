"""
Icon Downloader and Converter
Handles downloading icons from URLs and converting them to ICO/PNG format
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger("ICON.Downloader")


class IconDownloader:
    """Download and convert icons to appropriate formats"""

    def __init__(self, icons_dir: Path, target_size: int = 1024):
        """
        Initialize icon downloader

        Args:
            icons_dir: Directory to save downloaded icons
            target_size: Target icon size (512 or 1024)
        """
        self.icons_dir = icons_dir
        self.target_size = target_size
        self.icons_dir.mkdir(parents=True, exist_ok=True)

        # Check if ImageMagick is available for better ICO support
        self.has_imagemagick = self._check_imagemagick()

    async def download_and_convert(self, api, url: str, name: str) -> Optional[Path]:
        """
        Download icon from URL and convert to ICO format

        Args:
            api: SteamGridAPI instance for downloading
            url: URL to download from
            name: Game name (used for filename)

        Returns:
            Path to converted ICO file, or None if failed
        """
        try:
            # Create safe filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
            temp_download = self.icons_dir / f"{safe_name}_temp_download"
            temp_png = self.icons_dir / f"{safe_name}_temp.png"
            ico_path = self.icons_dir / f"{safe_name}.ico"

            # Download (extension unknown - could be JPG, PNG, WebP, etc.)
            success = await api.download_icon(url, temp_download)
            if not success:
                return None

            # Convert to ICO format
            ico_path = self._convert_to_ico(temp_download, temp_png, ico_path, safe_name)

            # Clean up temp files
            if temp_download.exists():
                temp_download.unlink()
            if temp_png.exists():
                temp_png.unlink()

            if ico_path:
                logger.info(f"Converted icon saved to {ico_path}")
                return ico_path
            else:
                return None

        except Exception as e:
            logger.error(f"Error downloading/converting icon: {e}")
            # Clean up on error
            try:
                safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
                temp_download = self.icons_dir / f"{safe_name}_temp_download"
                temp_png = self.icons_dir / f"{safe_name}_temp.png"
                if temp_download.exists():
                    temp_download.unlink()
                if temp_png.exists():
                    temp_png.unlink()
            except (OSError, PermissionError) as cleanup_error:
                logger.debug(f"Could not clean up temp files: {cleanup_error}")
            return None

    def _convert_to_ico(
        self, temp_download: Path, temp_png: Path, ico_path: Path, safe_name: str
    ) -> Optional[Path]:
        """
        Convert downloaded image to ICO format

        Note: PIL/Pillow has a limitation where ICO files are capped at 256x256 even when
        requesting larger sizes. This is a known limitation of the ICO format handler.

        Args:
            temp_download: Path to downloaded file
            temp_png: Path for intermediate PNG
            ico_path: Output ICO path
            safe_name: Safe filename base

        Returns:
            Path to ICO file or None if failed
        """
        try:
            # Open and process image
            with Image.open(temp_download) as img:
                # Convert to RGBA immediately (fixes JPEG issues)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Ensure square
                if img.size[0] != img.size[1]:
                    # Crop to square
                    size = min(img.size)
                    left = (img.size[0] - size) // 2
                    top = (img.size[1] - size) // 2
                    img = img.crop((left, top, left + size, top + size))

                # Resize to target size if needed
                if img.size[0] != self.target_size:
                    img = img.resize((self.target_size, self.target_size), Image.Resampling.LANCZOS)

                # Save as high-quality PNG first (important for JPEG sources)
                img.save(temp_png, format="PNG", optimize=False, compress_level=0)

            # Save standalone PNG at full resolution (always)
            with Image.open(temp_png) as png_img:
                png_img.save(self.icons_dir / f"{safe_name}.png", format="PNG", optimize=True)

            # Convert PNG to ICO - use ImageMagick if available for large ICO support
            if self.has_imagemagick:
                success = self._convert_to_ico_imagemagick(temp_png, ico_path)
                if success:
                    return ico_path
                else:
                    logger.warning("ImageMagick conversion failed, falling back to PIL")

            # Fallback to PIL (will cap at 256x256)
            with Image.open(temp_png) as png_img:
                sizes = self._get_ico_sizes()
                png_img.save(ico_path, format="ICO", sizes=sizes, bitmap_format="png")
                logger.info(f"Saved ICO with PIL (capped at 256x256): {ico_path}")

            return ico_path

        except Exception as e:
            logger.error(f"Error converting image to ICO: {e}")
            return None

    def _get_ico_sizes(self) -> list:
        """
        Get list of sizes to include in ICO file based on target size

        Returns:
            List of (width, height) tuples
        """
        if self.target_size >= 1024:
            sizes = [
                (1024, 1024),
                (512, 512),
                (256, 256),
                (128, 128),
                (64, 64),
                (48, 48),
                (32, 32),
                (16, 16),
            ]
        elif self.target_size >= 512:
            sizes = [(512, 512), (256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        else:
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

        return sizes

    def _check_imagemagick(self) -> bool:
        """Check if ImageMagick is available"""
        try:
            result = subprocess.run(["magick", "--version"], capture_output=True, timeout=5)
            available = result.returncode == 0
            if available:
                logger.info(
                    "ImageMagick detected - will create 512x512 ICO files (2x larger than PIL)"
                )
            return available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug("ImageMagick not found - using PIL (256x256 max)")
            return False

    def _convert_to_ico_imagemagick(self, png_path: Path, ico_path: Path) -> bool:
        """
        Convert PNG to ICO using ImageMagick (supports up to 512x512)

        Note: ICO format spec doesn't officially support sizes > 256x256, but many
        modern tools support 512x512. ImageMagick can create 512x512 ICO files.

        Args:
            png_path: Input PNG path
            ico_path: Output ICO path

        Returns:
            True if successful
        """
        try:
            # ImageMagick can create ICO files up to 512x512
            # (1024x1024 fails with InvalidDimensions error)
            cmd = [
                "magick",
                str(png_path),
                "-define",
                "icon:auto-resize=512,256,128,64,48,32,16",
                str(ico_path),
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"Created ICO with 512x512 using ImageMagick: {ico_path}")
                return True
            else:
                logger.error(f"ImageMagick error: {result.stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error running ImageMagick: {e}")
            return False
