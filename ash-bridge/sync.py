#!/usr/bin/env python3
"""Ash Bridge v1.2: the sync between Andy's Vibe stack and GitHub tiers.

Bridges three sources to two GitHub destinations:
  - custom skills (Andy-authored) -> public repo  vibe-stack/skills/
  - the bridge itself              -> public repo  ash-bridge/
  - Knowledge topics               -> private repo knowledge/ + checksum manifest

Selection is hybrid: deterministic rules (this script) tier each file
public/private, with a hard secret gate that quarantines anything matching
credential patterns. Phase 2 hook: a twinflame-hybrid classifier for
ambiguous items (see bridge_config.json).

Usage: GH_TOKEN=<github token with repo scope> python3 sync.py [--dry-run]
       GH_TOKEN=... python3 sync.py --tier public|private
       GH_TOKEN=... python3 sync.py --help
Fail-closed args since v1.2: unknown or malformed flags abort with a
usage error BEFORE any selection or push, instead of being silently
treated as a full run (failure mode 8, the 2026-11-19 --help near-miss).
Idempotent since v1.1: when content is byte-identical to the destination
tree, no commit is created and the run reports an honest no-op; receipts
are filed only when something actually changes.
Stdlib only. Zero credentials in code, config, or receipts.
"""

import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "bridge_config.json")


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def api(cfg, method, path, data=None, expect=(200, 201)):
    token = os.environ.get(cfg["github"]["token_env"])
    if not token:
        raise SystemExit(f"FATAL: env {cfg['github']['token_env']} not set")
    url = f"{cfg['github']['api_base']}{path}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ash-bridge",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def collect_rule(cfg, rule):
    """Return (carried, quarantined) as lists of {src, dest, content, sha256, size}."""
    root = rule["root"]
    include = rule["include"]
    exclude = set(rule.get("exclude") or [])
    carried, quarantined = [], []
    patterns = [re.compile(p) for p in cfg["secret_gate"]["patterns"]]
    max_bytes = cfg["limits"]["max_file_bytes"]
    include = list(include)  # copy; may expand the wildcard below
    if "*" in include:
        include = sorted(os.listdir(root))
    include = [n for n in include if not os.path.basename(n).startswith(".")]
    for name in include:
        base = os.path.join(root, name)
        if not os.path.exists(base):
            quarantined.append({"src": base, "reason": "missing"})
            continue
        walk = []
        if os.path.isdir(base):
            for dirpath, _, filenames in os.walk(base):
                for fn in filenames:
                    if fn.startswith("."):
                        continue
                    walk.append(os.path.join(dirpath, fn))
        else:
            walk.append(base)
        for abspath in sorted(walk):
            rel = os.path.relpath(abspath, root)
            if any(rel == ex or rel.startswith(ex + "/") for ex in exclude):
                continue
            with open(abspath, "rb") as f:
                content = f.read()
            size = len(content)
            if size > max_bytes:
                quarantined.append({"src": rel, "reason": f"oversize ({size}B)"})
                continue
            text = content.decode("utf-8", "replace")
            for pat in patterns:
                m = pat.search(text)
                if m:
                    quarantined.append(
                        {"src": rel, "reason": f"secret-gate: /{pat.pattern}/"}
                    )
                    break
            else:
                carried.append(
                    {
                        "src": rel,
                        "dest": f"{rule['dest_path']}/{rel}",
                        "content": content,
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "size": size,
                    }
                )
    return carried, quarantined


def build_tree(cfg, repo, files):
    """Stage blobs and build the tree against HEAD.
    Returns (parent, base_tree, parents, tree, n_entries)."""
    st, ref = api(cfg, "GET", f"/repos/{repo}/git/ref/heads/main")
    if st == 200:
        parent = ref["object"]["sha"]
        st, commit = api(cfg, "GET", f"/repos/{repo}/git/commits/{parent}")
        base_tree = commit["tree"]["sha"]
        parents = [parent]
    else:
        parent, base_tree, parents = None, None, []

    tree_entries = []
    for f in files:
        try:
            text = f["content"].decode("utf-8")
            enc, payload = "utf-8", {"content": text, "encoding": "utf-8"}
        except UnicodeDecodeError:
            enc = "base64"
            payload = {
                "content": base64.b64encode(f["content"]).decode(),
                "encoding": "base64",
            }
        st, blob = api(cfg, "POST", f"/repos/{repo}/git/blobs", payload)
        if st != 201:
            raise SystemExit(f"blob POST failed for {f['dest']}: {blob}")
        tree_entries.append(
            {"path": f["dest"], "mode": "100644", "type": "blob", "sha": blob["sha"]}
        )
        print(f"  blob[{enc}] {f['dest']} ({f['size']}B)")

    tree_payload = {"tree": tree_entries}
    if base_tree:
        tree_payload["base_tree"] = base_tree
    st, tree = api(cfg, "POST", f"/repos/{repo}/git/trees", tree_payload)
    if st != 201:
        raise SystemExit(f"tree POST failed: {tree}")
    return parent, base_tree, parents, tree, len(tree_entries)


def push_tree(cfg, repo, parent, parents, tree, message):
    """Commit the tree and advance main. Returns the new commit SHA."""
    st, new_commit = api(
        cfg,
        "POST",
        f"/repos/{repo}/git/commits",
        {"message": message, "tree": tree["sha"], "parents": parents},
    )
    if st != 201:
        raise SystemExit(f"commit POST failed: {new_commit}")

    if parent:
        st, _ = api(
            cfg,
            "PATCH",
            f"/repos/{repo}/git/refs/heads/main",
            {"sha": new_commit["sha"], "force": True},
        )
    else:
        st, _ = api(
            cfg,
            "POST",
            f"/repos/{repo}/git/refs",
            {"ref": "refs/heads/main", "sha": new_commit["sha"]},
        )
    if st not in (200, 201):
        raise SystemExit(f"ref update failed for {repo}")
    return new_commit["sha"]


def push_files(cfg, repo, files, message):
    """files: list from collect_rule. Returns (commit_sha|None, pushed_count).
    Idempotent: when the resulting tree is byte-identical to HEAD's tree,
    nothing is committed and (None, 0) is returned (honest no-op)."""
    parent, base_tree, parents, tree, n = build_tree(cfg, repo, files)
    if base_tree and tree["sha"] == base_tree:
        print(f"  [no-op] {repo}: content identical, nothing pushed")
        return None, 0
    return push_tree(cfg, repo, parent, parents, tree, message), n


USAGE = (
    "usage: GH_TOKEN=<token> python3 sync.py [--dry-run] [--tier public|private]\n"
    "       GH_TOKEN=<token> python3 sync.py --help\n"
    "\n"
    "Fail-closed args (v1.2): unknown or malformed flags abort before any\n"
    "selection or push. v1.1 silently treated unknown flags as a full run.\n"
)


def parse_args(argv):
    """v1.2 fail-closed CLI container: unknown flags abort BEFORE any
    selection or push; --help prints usage and exits 0. Closes failure
    mode 8 (2026-11-19 --help near-miss: an unknown flag fired a full
    sync and timed out at the bash wall; nothing pushed only by luck)."""
    dry, want_tier = False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run":
            dry = True
        elif a in ("-h", "--help"):
            print(USAGE, end="")
            sys.exit(0)
        elif a == "--tier":
            i += 1
            if i >= len(argv) or argv[i] not in ("public", "private"):
                got = argv[i] if i < len(argv) else "nothing"
                sys.stderr.write(f"error: --tier needs 'public' or 'private' (got {got})\n{USAGE}")
                sys.exit(2)
            want_tier = argv[i]
        else:
            sys.stderr.write(f"error: unknown argument: {a}\n{USAGE}")
            sys.exit(2)
        i += 1
    return dry, want_tier


def main():
    dry, want_tier = parse_args(sys.argv[1:])
    cfg = load_config()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    all_files, quarantined = [], []
    for rule in cfg["sources"]:
        if want_tier and rule["tier"] != want_tier:
            continue
        carried, q = collect_rule(cfg, rule)
        print(f"[select] {rule['name']}: {len(carried)} files -> {rule['tier']} ({rule['dest_path']}/)")
        for item in q:
            print(f"  QUARANTINED {item['src']}: {item['reason']}")
        all_files.extend(({"tier": rule["tier"], **f} for f in carried))
        quarantined.extend({"rule": rule["name"], **item} for item in q)

    public_files = [f for f in all_files if f["tier"] == "public"]
    private_files = [f for f in all_files if f["tier"] == "private"]

    # Build the manifest (covers BOTH tiers) and add it to the private push set.
    # v1.1: no volatile timestamp — the manifest is a pure function of the
    # synced content, so identical state hashes identically (idempotence).
    manifest = {
        "tool": "ash-bridge",
        "version": cfg["version"],
        "files": [
            {
                "path": f["dest"],
                "tier": f["tier"],
                "bytes": f["size"],
                "sha256": f["sha256"],
            }
            for f in all_files
        ],
        "quarantined": quarantined,
    }
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True).encode()
    private_files = private_files + [
        {
            "src": "<manifest>",
            "dest": "MANIFEST.json",
            "content": manifest_json,
            "sha256": hashlib.sha256(manifest_json).hexdigest(),
            "size": len(manifest_json),
        }
    ]

    print(f"\n[gate] {len(all_files)} carried, {len(quarantined)} quarantined")
    if dry:
        print("[dry-run] no pushes. Manifest summary above.")
        return

    results = {}
    if public_files:
        sha, n = push_files(
            cfg,
            cfg["public_repo"],
            public_files,
            f"ash-bridge v{cfg['version']}: bridge + custom skills sync ({stamp})",
        )
        if sha:
            results["public"] = {"repo": cfg["public_repo"], "commit": sha, "files": n}
            print(f"[push] public -> {sha[:9]} ({n} files)")
        else:
            results["public"] = {
                "repo": cfg["public_repo"],
                "status": "no-op (content identical)",
            }
            print("[skip] public: no changes (idempotent no-op)")
    if private_files:
        # Idempotence probe: a receipt is filed only when the private tree
        # would actually change, so the archive never gains ceremony commits.
        _, base_tree, _, probe_tree, _ = build_tree(
            cfg, cfg["private_repo"], private_files
        )
        if base_tree and probe_tree["sha"] == base_tree:
            results["private"] = {
                "repo": cfg["private_repo"],
                "status": "no-op (content identical)",
            }
            print("[skip] private: no changes (idempotent no-op)")
        else:
            pub = results.get("public", {})
            pub_desc = (
                f"pushed {pub['commit'][:9]} ({pub['files']} files)"
                if pub.get("commit")
                else pub.get("status", "not part of this run")
            )
            manifest_md = (
                f"# Ash Bridge Sync Receipt\n\n"
                f"Run {stamp} by ash-bridge v{cfg['version']}. Receipts are filed "
                f"only when content changes (idempotent sync since v1.1).\n\n"
                f"- Files carried: {len(all_files)} (public {len(public_files)}, "
                f"private {len(private_files) - 1})\n"
                f"- Quarantined: {len(quarantined)}\n"
                f"- Public tier: {pub_desc}\n\n"
                f"Per-file sha256 checksums live in `MANIFEST.json`. Integrity "
                f"check: re-hash any restored file and compare.\n"
            ).encode()
            private_files.append(
                {
                    "src": "<manifest>",
                    "dest": f"receipts/SYNC-{stamp.replace(':', '')}.md",
                    "content": manifest_md,
                    "sha256": hashlib.sha256(manifest_md).hexdigest(),
                    "size": len(manifest_md),
                }
            )
            sha, n = push_files(
                cfg,
                cfg["private_repo"],
                private_files,
                f"ash-bridge v{cfg['version']}: knowledge + save-state archive ({stamp})",
            )
            results["private"] = {"repo": cfg["private_repo"], "commit": sha, "files": n}
            print(f"[push] private -> {sha[:9]} ({n} files)")

    print("\n[receipt]")
    print(json.dumps(results, indent=2))
    pushed = sum(1 for v in results.values() if v.get("commit"))
    if pushed:
        print(
            f"\nDONE {stamp}: {len(all_files)} files, "
            f"{len(quarantined)} quarantined, {pushed} tier(s) pushed."
        )
    else:
        print(
            f"\nDONE {stamp}: NO CHANGES. {len(all_files)} files inspected, "
            f"{len(quarantined)} quarantined; all tiers already current."
        )


if __name__ == "__main__":
    main()
