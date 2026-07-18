# ComicVine Ambiguity Verification

Use this utility to review ambiguous ComicVine issue ids without changing the
local cache.

Script:

- `utilities/verify_comicvine_ambiguity.py`
- `scripts/verify_comicvine_ambiguity.sh`

What it does:

- reads ambiguous ComicVine issue ids from `data/cbl_lookup.sqlite3`
- queries ComicVine one id at a time
- compares the live issue metadata against a sample cache row
- writes a CSV report for manual review

Why it exists:

- the cache contains legitimate ambiguities caused by relaunches, renamed
  series, and reading-list overlaps
- the verifier helps confirm which rows deserve a human review pass before any
  cache correction is made

Safe usage:

```bash
./scripts/verify_comicvine_ambiguity.sh
```

With an explicit report path and slower pacing:

```bash
./scripts/verify_comicvine_ambiguity.sh \
  /home/rmleonard/Projects/cirrus/data/cbl_lookup.sqlite3 \
  report \
  /home/rmleonard/Projects/cirrus/data/reports/comicvine_ambiguity_review.csv \
  0 \
  3.0
```

Recommended workflow:

1. run the verifier against a small limit first
2. inspect the report for mismatched series, issue numbers, or years
3. review the highest-severity ids from the appendix
4. only then consider cache corrections or source-file corrections
