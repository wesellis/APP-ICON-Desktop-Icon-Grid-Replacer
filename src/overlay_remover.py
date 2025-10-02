"""
Overlay Remover
Remove UAC shields and shortcut arrows from desktop icons
"""

import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger("ICON.OverlayRemover")


class OverlayRemover:
    """Handle removal of UAC shields and shortcut overlays"""

    def __init__(self):
        pass

    def remove_overlays(self) -> bool:
        """Remove UAC shields and shortcut overlays"""
        try:
            # Step 1: Create and import registry file
            if not self._create_registry_file():
                logger.error("Failed to create registry file")
                return False

            # Step 2: Restart Explorer
            print("\n  Restarting Windows Explorer to apply changes...")
            if not self._restart_explorer():
                logger.warning(
                    "Explorer restart may have failed - you may need to restart manually"
                )

            print("  ✅ Overlays removed successfully!")

            return True

        except Exception as e:
            logger.error(f"Error removing overlays: {e}")
            return False

    def _create_registry_file(self) -> bool:
        """Create and import registry file to remove overlays"""
        try:
            # Create temporary registry file
            # Using empty strings is safer than pointing to external .ico files
            reg_content = """Windows Registry Editor Version 5.00

; Remove shortcut arrow overlay
[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Icons]
"29"=""

; Remove UAC shield overlay
[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Icons]
"77"=""
"""

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".reg", delete=False) as f:
                f.write(reg_content)
                temp_reg_file = f.name

            logger.info(f"Created registry file: {temp_reg_file}")
            print(f"  ✓ Created registry configuration")

            # Import registry file with admin rights
            print("  ⚠️  Requesting administrator privileges to modify registry...")
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'Start-Process regedit -ArgumentList "/s {temp_reg_file}" -Verb RunAs -Wait',
                ],
                capture_output=True,
                text=True,
            )

            # Clean up temp file
            try:
                Path(temp_reg_file).unlink()
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not delete temp file {temp_reg_file}: {e}")

            if result.returncode == 0:
                logger.info("Registry updated successfully")
                print("  ✓ Registry updated")
                return True
            else:
                logger.error(f"Registry update failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error creating/importing registry file: {e}")
            return False

    def _restart_explorer(self) -> bool:
        """Restart Windows Explorer to apply changes"""
        try:
            # Kill Explorer
            subprocess.run(
                ["powershell", "-Command", "Stop-Process -Name explorer -Force"],
                capture_output=True,
                timeout=5,
            )

            # Wait a moment
            import time

            time.sleep(2)

            # Start Explorer
            subprocess.run(
                ["powershell", "-Command", "Start-Process explorer"], capture_output=True, timeout=5
            )

            logger.info("Explorer restarted")
            return True

        except Exception as e:
            logger.error(f"Error restarting Explorer: {e}")
            return False

    def restore_overlays(self) -> bool:
        """Restore UAC shields and shortcut overlays to default"""
        try:
            print("\n  Restoring overlay icons...")

            # Create registry file to delete the values
            reg_content = """Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Icons]
"29"=-

[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Icons]
"77"=-
"""

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".reg", delete=False) as f:
                f.write(reg_content)
                temp_reg_file = f.name

            logger.info(f"Created restore registry file: {temp_reg_file}")

            # Import registry file with admin rights
            print("  ⚠️  Requesting administrator privileges to modify registry...")
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'Start-Process regedit -ArgumentList "/s {temp_reg_file}" -Verb RunAs -Wait',
                ],
                capture_output=True,
                text=True,
            )

            # Clean up temp file
            try:
                Path(temp_reg_file).unlink()
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not delete temp file {temp_reg_file}: {e}")

            if result.returncode != 0:
                logger.error(f"Registry restore failed: {result.stderr}")
                return False

            # Restart Explorer
            print("  Restarting Windows Explorer...")
            self._restart_explorer()

            print("  ✅ Overlays restored to default!")
            return True

        except Exception as e:
            logger.error(f"Error restoring overlays: {e}")
            return False


def test_overlay_remover():
    """Test the overlay remover"""
    remover = OverlayRemover()

    print("Testing Overlay Remover")
    print("=" * 50)

    print("\n1. Testing overlay removal...")
    if remover.remove_overlays():
        print("✓ Removal test passed")
    else:
        print("✗ Removal test failed")

    input("\nPress Enter to test restoration...")

    print("\n2. Testing overlay restoration...")
    if remover.restore_overlays():
        print("✓ Restoration test passed")
    else:
        print("✗ Restoration test failed")


if __name__ == "__main__":
    test_overlay_remover()
