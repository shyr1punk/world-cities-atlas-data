"""Export a clearly incomplete Wikidata snapshot. Standard library only."""
import argparse
import gzip
import hashlib
import json
import sqlite3
from pathlib import Path
from world_entities import EntityCache, label, targets, rows_for


def export(root, output):
    output.mkdir(parents=True, exist_ok=True)
    world = set(json.loads((root / 'ids.json').read_text()))
    eurasia = set(json.loads((root / 'eurasia/ids.json').read_text()))
    cache = EntityCache(root)
    downloaded = world & cache.entities.keys()
    report = {'complete': False, 'worldCensus': len(world), 'downloadedCities': len(downloaded),
              'missingWorldCities': len(world - downloaded), 'eurasiaCensus': len(eurasia),
              'downloadedEurasiaCities': len(eurasia & downloaded), 'missingEurasiaCities': len(eurasia - downloaded),
              'census': json.loads((root / 'manifest.json').read_text()),
              'note': 'Partial snapshot. Raw claims retain revisions and references. Missing history is unknown. Eurasia selection includes transcontinental countries in full.'}
    db = output / 'cities.sqlite'
    if db.exists(): db.unlink()
    conn = sqlite3.connect(db)
    conn.execute('CREATE TABLE cities (qid TEXT PRIMARY KEY, name TEXT NOT NULL, country_ids TEXT NOT NULL, eurasia_priority INTEGER NOT NULL, entity_json TEXT NOT NULL, import_rows_json TEXT NOT NULL)')
    with gzip.GzipFile(filename=str(output / 'cities.jsonl.gz'), mode='wb', mtime=0) as stream:
        for q in sorted(downloaded, key=lambda q: int(q[1:])):
            entity = cache.entities[q]
            record = {'qid': q, 'name': label(entity, q), 'countryIds': targets(entity, 'P17', current=True),
                      'eurasiaPriority': q in eurasia, 'entity': entity, 'importRows': rows_for(q, entity, cache.entities)}
            stream.write((json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n').encode())
            conn.execute('INSERT INTO cities VALUES (?,?,?,?,?,?)', (q, record['name'], json.dumps(record['countryIds']), int(q in eurasia), json.dumps(entity, ensure_ascii=False), json.dumps(record['importRows'], ensure_ascii=False)))
    conn.commit()
    assert conn.execute('SELECT count(*) FROM cities').fetchone()[0] == len(downloaded)
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    conn.close()
    with gzip.GzipFile(filename=str(output / 'cities.sqlite.gz'), mode='wb', mtime=0) as stream:
        with db.open('rb') as source:
            while chunk := source.read(1024 * 1024): stream.write(chunk)
    db.unlink()
    for name, ids in [('missing-world.json', world - downloaded), ('missing-eurasia.json', eurasia - downloaded)]:
        (output / name).write_text(json.dumps(sorted(ids, key=lambda q: int(q[1:]))))
    (output / 'coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    paths = sorted(p for p in output.iterdir() if p.name != 'SHA256SUMS')
    (output / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in paths))
    print(json.dumps({k:v for k,v in report.items() if k != 'census'}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('data/raw/world'))
    parser.add_argument('--output', type=Path, default=Path('dist'))
    args = parser.parse_args()
    export(args.source, args.output)
