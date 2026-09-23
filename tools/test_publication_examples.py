#!/usr/bin/env python3
"""Real Quarto smoke test; run after provisioning the pinned runtime."""
import json
from pathlib import Path
import shutil
import tempfile
from publication_outputs import build_local, digest
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    for name in ('static', 'quarto'):
        checkout = Path(tmp) / name
        shutil.copytree(ROOT / 'templates/publication-examples' / name, checkout)
        spec = json.loads((checkout / 'publication.json').read_text())
        # The demo is deliberately unregistered and has no real upstream.
        (checkout / 'private.txt').write_text('not published')
        first = build_local(checkout, spec)
        assert 'private.txt' not in first
        if name == 'quarto':
            chapter = checkout / 'chapters/chapter.qmd'
            chapter.write_text(chapter.read_text() + '\nA changed chapter.\n\n![Figure](figure.svg)\n')
            (checkout / 'chapters/figure.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="10"/></svg>')
            second = build_local(checkout, spec)
            assert digest(first) != digest(second)
            assert any(path.endswith('figure.svg') for path in second)
            assert b'A changed chapter' in second['chapters/chapter.html']
            assert 'private.txt' not in second
        print('PASS: real complete output and private-source exclusion:', name)
