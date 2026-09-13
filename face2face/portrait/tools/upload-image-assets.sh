#!/usr/bin/env bash
# Run this file from the complete ZIP to upload the original PNG archive and current PNG exports.
# Uses an isolated worktree; never modifies an existing shared checkout or forces a branch.
set -euo pipefail
command -v gh >/dev/null || { echo 'GitHub CLI (gh) is required.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
gh auth status >/dev/null
source_dir="$(cd "$(dirname "$0")/.." && pwd)"
repo='flyrev/trio-prototypes'
tmp="$(mktemp -d)"
branch="assets/portrait-png-$(date -u +%Y%m%dT%H%M%SZ)"
trap 'rm -rf "$tmp"' EXIT
python3 - "$source_dir" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]); data=json.loads((root/'archive/manifest.json').read_text())
for item in data['sources']:
    p=root/'archive'/item['archive_path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
        raise SystemExit(f'Missing or changed source PNG: {p}')
print('All source PNG checksums verified.')
PY
gh repo clone "$repo" "$tmp/repo" -- --no-checkout
git -C "$tmp/repo" fetch origin main
git -C "$tmp/repo" worktree add -b "$branch" "$tmp/worktree" origin/main
python3 - "$source_dir" "$tmp/worktree/face2face/portrait" <<'PY'
import hashlib,json,shutil,sys
from pathlib import Path
src,dst=map(Path,sys.argv[1:])
for sub in ('archive/originals','mockups'):
    for p in (src/sub).glob('*.png'):
        target=dst/sub/p.name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes():
            raise SystemExit(f'Conflict; refusing to overwrite: {target}')
        shutil.copy2(p,target)
m=dst/'archive/manifest.json';data=json.loads(m.read_text());data['binary_delivery']='GitHub repository and complete ZIP';m.write_text(json.dumps(data,indent=2)+'\n')
a=dst/'archive/README.md'
a.write_text('# Historical image archive — superseded\n\nAll original PNGs listed in `manifest.json` are stored in `originals/`. Their SHA-256 hashes were verified before upload. Duplicate references share one physical file.\n\nThese images preserve the design exploration, including rejected generations. Use `../SPEC.md` and `../mockups/` for the current design. Historical images may contain mixed typography, removed controls, or opaque backgrounds; they are not acceptance criteria.\n')
r=dst/'README.md';text=r.read_text()
heading='## Source archive and delivery boundary'
start=text.find(heading)
if start<0: start=text.index('## Source archive\n')
end=text.index('## What is complete, and what remains')
text=text[:start]+'## Source archive\n\nThe original historical PNGs are in [`archive/originals/`](archive/originals/), with identities and verified SHA-256 hashes in [`archive/manifest.json`](archive/manifest.json). Current SVG and RGBA PNG mockups are in [`mockups/`](mockups/). Historical images are superseded and are not acceptance criteria.\n\n'+text[end:]
text=text.replace(' Historical PNG transfer is a separate packaging item, not a product implementation.','')
r.write_text(text)
PY
git -C "$tmp/worktree" add face2face/portrait
if git -C "$tmp/worktree" diff --cached --quiet; then echo 'Image assets are already uploaded.'; exit 0; fi
login="$(gh api user --jq .login)"
user_id="$(gh api user --jq .id)"
git -C "$tmp/worktree" -c user.name="$login" -c user.email="${user_id}+${login}@users.noreply.github.com" commit -m 'Archive portrait source PNGs and canonical PNG exports'
git -C "$tmp/worktree" push -u origin "$branch"
pr="$(gh pr create --repo "$repo" --base main --head "$branch" --title 'Archive portrait PNG assets' --body 'Upload the source-image archive and canonical PNG exports. Source SHA-256 hashes verified; isolated worktree; no production changes.')"
gh pr merge "$pr" --repo "$repo" --squash --delete-branch
echo 'Image assets merged into face2face/portrait/ on main.'
