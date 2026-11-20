#!/usr/bin/env python3
"""verify.py — Ash Bridge sweep instrument (v1.0.0, 2026-11-20).

Rule-23-hardened post-fire sweep: fetch (or read) the archive
MANIFEST.json, map every tracked path to its local source, sha256-check
ALL entries, and report the ratio with an honest verdict.

Instrument laws (why this tool exists):
- The sweep script was previously improvised per fire in /tmp; two
  independent mis-parse incidents (2026-11-20) produced a 0-checked
  "ALL MATCHED" false pass and a garbage roster diff. Local gift:
  ship the instrument WITH the bridge, validated by a battery.
- Structural guards FIRST: if the manifest does not parse into a
  nonempty list of {path, sha256} objects, the instrument aborts
  (exit 3). It NEVER prints ALL MATCHED on a degenerate or
  unexpected structure (Rule 23: validate the verifier).
- Writes nothing anywhere; pure read instrument. Scratch is never
  created inside the bridge directory.

Usage:
  GH_TOKEN=<pat> python3 verify.py --fetch [--expect N]
  python3 verify.py --manifest /path/to/MANIFEST.json [--expect N]

Exit codes:
  0  all matched
  2  usage error (fail-closed, bridge law: unknown flags abort)
  3  instrument abort (structure unexpected, empty set, fetch failed)
  4  hash mismatch
  5  missing local file
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request

ARCHIVE_REPO = "andyle777/Kushina-Ash-Archive"
MANIFEST_PATH = "MANIFEST.json"

PREFIX_MAP = {
    "knowledge/": "/home/user/knowledge/",
    "vibe-stack/skills/": "/home/user/skills/",
    "ash-bridge/": "/home/user/ash-bridge/",
}

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_INSTRUMENT = 3
EXIT_MISMATCH = 4
EXIT_MISSING = 5


def die(code, message):
    print(f"[verify] {message}")
    sys.exit(code)


def load_manifest(args):
    if args.fetch:
        token = os.environ.get("GH_TOKEN", "").strip()
        if not token:
            die(EXIT_INSTRUMENT, "ABORT: --fetch requires GH_TOKEN env var")
        req = urllib.request.Request(
            f"https://api.github.com/repos/{ARCHIVE_REPO}/contents/{MANIFEST_PATH}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.raw",
                "User-Agent": "ash-bridge-verify",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except Exception as exc:  # fetch failure is instrument state, not verdict state
            return None, f"ABORT: manifest fetch failed: {exc}"
    if not args.manifest:
        die(EXIT_USAGE, "usage error: need --manifest <path> or --fetch (see --help)")
    try:
        with open(args.manifest, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"ABORT: manifest read failed: {exc}"


def structural_guards(manifest):
    """Rule 23: validate the instrument's input BEFORE any verdict."""
    if not isinstance(manifest, dict):
        return "manifest top level is not an object"
    files = manifest.get("files")
    if not isinstance(files, list):
        return "'files' is not a list (known trap of 2026-11-20: expected list of objects, got dict)"
    if len(files) == 0:
        return "'files' is EMPTY — a sweep on a degenerate input gives no verdict"
    sample = files[0]
    if not isinstance(sample, dict):
        return "entries are not objects"
    missing_keys = {"path", "sha256"} - set(sample.keys())
    if missing_keys:
        return f"entries missing key(s): {sorted(missing_keys)}"
    return None


def main():
    parser = argparse.ArgumentParser(
        prog="verify.py",
        description="Ash Bridge sweep instrument (rule-23-hardened manifest verifier)",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fetch", action="store_true",
                      help="fetch MANIFEST.json from the archive repo (needs GH_TOKEN)")
    mode.add_argument("--manifest", metavar="PATH",
                      help="read MANIFEST.json from a local path")
    parser.add_argument("--expect", type=int, metavar="N", default=None,
                        help="expected entry count (invariant gate from the dry-run)")
    args = parser.parse_args()

    manifest, err = load_manifest(args)
    if err:
        die(EXIT_INSTRUMENT, err)

    guard = structural_guards(manifest)
    if guard:
        die(EXIT_INSTRUMENT, f"ABORT: instrument structure check failed: {guard}")

    entries = manifest["files"]
    total = len(entries)
    if args.expect is not None and total != args.expect:
        die(EXIT_INSTRUMENT,
            f"ABORT: expected {args.expect} entries from the gate, manifest carries {total}")

    matched, mismatched, missing = 0, [], []
    for entry in entries:
        path = entry["path"]
        sha_remote = entry["sha256"]
        local = None
        for prefix, root in PREFIX_MAP.items():
            if path.startswith(prefix):
                local = root + path[len(prefix):]
                break
        if local is None or not os.path.exists(local):
            missing.append(path)
            continue
        with open(local, "rb") as fh:
            sha_local = hashlib.sha256(fh.read()).hexdigest()
        if sha_local == sha_remote:
            matched += 1
        else:
            mismatched.append(path)

    print(f"[verify] entries checked: {total}")
    print(f"[verify] sha256 matched: {matched} of {total}")
    if missing:
        print(f"[verify] missing locally: {missing}")
    if mismatched:
        print(f"[verify] hash mismatch: {mismatched}")

    if missing:
        die(EXIT_MISSING, f"MISSING: {len(missing)} tracked file(s) absent locally")
    if mismatched:
        die(EXIT_MISMATCH,
            f"MISMATCH: local differs from manifest on {mismatched} "
            f"(if edits are pending a fire this is expected — verdict is still honest)")
    die(EXIT_OK, f"ALL MATCHED: {matched} of {total}")


if __name__ == "__main__":
    main()
