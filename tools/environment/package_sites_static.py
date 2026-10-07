"""Portable fallback for this static Site if the installed Sites helper disappears.

Preserves the dist/.openai/hosting.json archive contract of the helper's earlier
validated archive. Never packages source trees or credentials.
"""
from pathlib import Path
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'web_demo'
OUT = ROOT / 'qa/demo_web_20260920/site.tar.gz'
config = json.loads((SITE / '.openai/hosting.json').read_text(encoding='utf8'))
assert config['static']['directory'] == 'dist'
assert config['project_id'] == 'appgprj_6aaf6f1d69608191adb8549f7568b146'
assert (SITE / 'dist/index.html').is_file()
# The installed official helper created this archive earlier in the same turn.
# Inspect its contract before substituting the now-missing cache helper.
with tarfile.open(OUT, 'r:gz') as previous:
    previous_config = json.load(previous.extractfile('dist/.openai/hosting.json'))
    assert previous_config == config
manifest = json.loads((SITE / 'dist/chunks.json').read_text())
for row in manifest.values():
    combined = hashlib.sha256()
    for chunk in row['chunks']:
        data = (SITE / 'dist' / chunk['url']).read_bytes()
        assert len(data) == chunk['bytes']
        assert hashlib.sha256(data).hexdigest() == chunk['sha256']
        combined.update(data)
    assert combined.hexdigest() == row['sha256']
temporary = OUT.with_name('site.next.tar.gz')
# All static paths fit USTAR. Avoid redundant per-file PAX timestamp records;
# the provider enforces the expanded TAR size, not only compressed payload size.
with tarfile.open(temporary, 'w:gz', compresslevel=6, format=tarfile.USTAR_FORMAT) as archive:
    for path in sorted((SITE / 'dist').rglob('*')):
        if path.is_file():
            assert path.stat().st_size <= 25 * 1024 * 1024
            archive.add(path, arcname='dist/' + path.relative_to(SITE / 'dist').as_posix())
    data = (json.dumps(config) + '\n').encode()
    info = tarfile.TarInfo('dist/.openai/hosting.json')
    info.size = len(data)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))
assert temporary.stat().st_size < 256 * 1024 * 1024
import gzip
expanded_bytes = 0
with gzip.open(temporary, 'rb') as stream:
    while block := stream.read(1024*1024):
        expanded_bytes += len(block)
assert expanded_bytes <= 256 * 1024 * 1024, 'Sites expanded TAR exceeds 256 MiB'
with tarfile.open(temporary, 'r:gz') as archive:
    names = archive.getnames()
    assert 'dist/index.html' in names and 'dist/.openai/hosting.json' in names
    assert all(name.startswith('dist/') and '..' not in name for name in names)
temporary.replace(OUT)
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,
                  'expanded_bytes':expanded_bytes,
                  'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'files':len(names)}))
