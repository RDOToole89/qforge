#!/usr/bin/env python3
"""Quick test of validation pipeline"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    repo_root = Path(__file__).parent
    print(f"Testing validation from: {repo_root}")
    
    # Test schema validation
    print("\n🔍 Testing schema validation...")
    code, out, err = run_command(
        f"python scripts/validate.py --schemas-only --path schemas/v1",
        cwd=repo_root
    )
    print(f"Exit code: {code}")
    if out:
        print("STDOUT:", out)
    if err:
        print("STDERR:", err)
    
    # Test example validation
    print("\n📄 Testing example validation...")
    code, out, err = run_command(
        f"python scripts/validate.py --examples-only --path .",
        cwd=repo_root
    )
    print(f"Exit code: {code}")
    if out:
        print("STDOUT:", out)
    if err:
        print("STDERR:", err)
    
    # Test full validation
    print("\n🎯 Testing full validation...")
    code, out, err = run_command(
        f"python scripts/validate.py --path .",
        cwd=repo_root
    )
    print(f"Exit code: {code}")
    if out:
        print("STDOUT:", out)
    if err:
        print("STDERR:", err)

if __name__ == "__main__":
    main()