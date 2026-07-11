"""system-cleanup CLI entry point. Usage: scl diagnose|scan|clean [options]"""
import sys
from . import diagnose, cleanup

def main():
    if len(sys.argv) < 2:
        print("Usage: scl diagnose|scan|clean [--dry-run] [--full] [--yes]")
        print("  diagnose  — read-only system diagnosis report")
        print("  scan      — scan junk paths, report sizes")
        print("  clean     — execute safe cleanup")
        print("  clean --full — includes admin-required operations")
        print("  clean --dry-run — preview without deleting")
        return
    cmd = sys.argv[1]
    # Remove the first arg (command) so argparse in sub-modules works
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    if cmd == "diagnose":
        diagnose.main()
    elif cmd in ("scan", "clean"):
        cleanup.main()
    else:
        print(f"Unknown command: {cmd}")
        main()

if __name__ == "__main__":
    main()