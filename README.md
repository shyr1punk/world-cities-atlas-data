# World Cities Atlas Data

English | [Русский](docs/ru/README.md)

Wikidata city snapshots for a historical atlas, with Europe and Asia prioritized for downloading.

**The first release is incomplete.** It contains source records and download tools, not a complete world gazetteer. See `coverage.json` in each release for exact coverage. An absent record does not mean a city does not exist.

## Downloads

[Release assets](https://github.com/shyr1punk/world-cities-atlas-data/releases):

- `cities.jsonl.gz` — one city record per line;
- `cities.sqlite.gz` — the same selection in SQLite;
- `coverage.json` — coverage report;
- `missing-world.json`, `missing-eurasia.json` — city QIDs still to be downloaded;
- `SHA256SUMS` — file checksums.

## Coverage

The global census dated September 12, 2026 contains 90,902 QIDs classified as city (Q515), city/town (Q7930989), or their subclasses, excluding records with a dissolution property (P576). There is no population threshold. Wikidata classifications may contain errors; inclusion does not establish legal city status.

The Eurasia queue intersects this census with Europe/Asia membership through the city itself, its immediate administrative territory, or its country. Transcontinental countries are included in full for downloading. This is not a final geographic classification; records with unresolved geography may be absent. The selection query is stored in `data/raw/world/eurasia/selection.json`.

Records were fetched at different times. Entity `lastrevid` and `modified` fields are retained when available. Verified historical additions from the original atlas are not included: this release contains Wikidata records only.

## Data format

JSONL fields: `qid`, `name`, `countryIds`, `eurasiaPriority`, `entity`, `importRows`.

`entity` retains selected source claims, qualifiers, and references: countries, continents, classes, administrative territories, foundation/first-mention dates, population, coordinates, and native names. `importRows` is an intermediate representation for further import, not a verified historical timeline. Unknown dates and coordinates remain unknown; an entity modification date is not a foundation or census date.

The initial dataset's display-name fallback is Russian, English, multilingual (`mul`), then an available native name. Source-language labels are preserved as data, independently of the documentation language. Countries use QIDs. SQLite stores arrays and source properties as JSON in TEXT columns.

```sql
SELECT qid, name FROM cities WHERE eurasia_priority = 1 LIMIT 100;
```

## Running the tools

Python 3.10 or later; no third-party dependencies. Run from the repository root:

```sh
python3 scripts/fetch-eurasia.py
python3 scripts/export_snapshot.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

The downloader uses the saved queue, fetches batches of 50 entities, caches progress in `data/raw/world/entities`, and respects Retry-After. Status is written to `data/raw/world/eurasia/status.json`. Rerunning after a network failure reuses the cache. To fetch the entire saved global census, run `python3 scripts/fetch-world-entities.py`.

Completing the regional queue does not mark the world catalog complete. Exporting does not modify the website. No API server or automatic update schedule is included yet.

## Sources and licensing

Wikidata structured data is available under [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing). Each city's source is `https://www.wikidata.org/wiki/<QID>`. Links to third-party references are retained without copying their texts. A separate code license has not yet been selected.
