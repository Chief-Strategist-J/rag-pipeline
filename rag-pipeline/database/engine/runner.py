import hashlib
import os
import sys
import yaml
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_schema_lock(base_path: Path) -> bool:
    lock_file = base_path / "database" / "schema.lock"
    if not lock_file.exists():
        sys.stderr.write(f"ERROR: Lock file not found: {lock_file}\n")
        return False

    with open(lock_file, "r", encoding="utf-8") as f:
        lock_data = yaml.safe_load(f)

    migrations = lock_data.get("migrations", [])
    for entry in migrations:
        rel_file = entry.get("file")
        expected_hash = entry.get("checksum")
        actual_file = base_path / rel_file
        if not actual_file.exists():
            sys.stderr.write(f"ERROR: Migration file missing: {actual_file}\n")
            return False

        computed_hash = calculate_sha256(actual_file)
        if computed_hash != expected_hash:
            sys.stderr.write(
                f"ERROR: Checksum mismatch for {rel_file}: expected {expected_hash}, got {computed_hash}\n"
            )
            return False

        rollback_rel = entry.get("rollback_file")
        if rollback_rel:
            rollback_file = base_path / rollback_rel
            if not rollback_file.exists():
                sys.stderr.write(f"ERROR: Rollback file missing: {rollback_file}\n")
                return False
            expected_rb_hash = entry.get("rollback_checksum")
            if expected_rb_hash:
                computed_rb_hash = calculate_sha256(rollback_file)
                if computed_rb_hash != expected_rb_hash:
                    sys.stderr.write(
                        f"ERROR: Rollback checksum mismatch for {rollback_rel}: expected {expected_rb_hash}, got {computed_rb_hash}\n"
                    )
                    return False

    return True


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    if not verify_schema_lock(root):
        sys.exit(1)
    print("Schema lock verification passed: all migration files match cryptographic hashes.")
    sys.exit(0)
