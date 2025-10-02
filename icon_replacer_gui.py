#!/usr/bin/env python3
"""
ICON - Desktop Icon Grid Replacer (GUI Wrapper)
Catches errors and keeps console open for debugging
"""

import sys
import traceback

def main():
    try:
        # Import and run the actual application
        import icon_replacer

        # Run normally
        import asyncio
        asyncio.run(icon_replacer.main())

    except Exception as e:
        print("\n" + "="*60)
        print("ERROR: ICON encountered an error")
        print("="*60)
        print(f"\n{type(e).__name__}: {e}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("\n" + "="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
