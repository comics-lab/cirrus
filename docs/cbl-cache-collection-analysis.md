# CBL Cache Collection Analysis

This report summarizes the local `cbl_issue_lookup` cache in collector terms.
The table is a flattened reading-list cache, so it intentionally contains many
repeated rows. The goal here is to distinguish:

- rows in the table
- unique comic books represented
- repeated issue placements across lists
- ambiguous records that deserve review

## Raw Table Size

- total rows: `336,312`
- distinct ComicVine issue ids: `76,691`
- distinct `(series, issue)` pairs: `63,778`
- distinct `(series, issue, year)` triples: `76,723`
- distinct series ids: `9,015`

## Unique Books By Publisher

Publisher is derived from the leading bracketed label in `list_name` when
present. Entries without a bracketed label are grouped as `Unlabeled`.

| Publisher | Unique books | Rows |
| --- | ---: | ---: |
| Marvel | 42,375 | 210,662 |
| Unlabeled | 38,979 | 49,764 |
| DC Comics | 15,634 | 42,679 |
| DC | 7,732 | 10,117 |
| Spider-Man | 2,877 | 5,755 |
| Image | 1,330 | 1,442 |
| Dark Horse | 1,318 | 1,319 |
| IDW | 888 | 1,268 |
| Valiant | 626 | 741 |
| X-Men Krakoa | 624 | 624 |

Notes:

- `Unlabeled` is large because many source lists are structured as master or
  chronology lists rather than publisher-tagged lists.
- The publisher labels are source-label conventions, not a normalized publisher
  field from the cache schema.

## Unique Books By List Type

List type is inferred from `list_name`.

| List type | Unique books | Rows |
| --- | ---: | ---: |
| other | 57,872 | 125,550 |
| reading order | 43,513 | 113,085 |
| master reading order | 27,043 | 45,524 |
| event order | 20,903 | 49,220 |
| chronology | 2,877 | 2,877 |
| master list | 56 | 56 |

Interpretation:

- `reading order` and `master reading order` make up a large share of the cache.
- `event order` is another large overlapping family.
- `chronology` is much smaller but tends to be highly curated.

## Series With Multiple Volumes

Collector-wise, the most useful duplication pattern is a series name that spans
multiple volume values.

- series with multiple volumes: `590`

Top examples:

| Series | Volumes | Unique books | Rows |
| --- | ---: | ---: | ---: |
| Captain America | 13 | 632 | 4,929 |
| Captain Marvel | 13 | 243 | 1,691 |
| The Punisher | 10 | 307 | 1,823 |
| Deadpool | 10 | 278 | 2,004 |
| Ghost Rider | 10 | 272 | 1,419 |
| The Amazing Spider-Man | 9 | 982 | 9,737 |
| Fantastic Four | 9 | 722 | 5,290 |
| Aquaman | 9 | 336 | 1,525 |
| Black Panther | 9 | 209 | 1,738 |
| Daredevil | 8 | 695 | 4,904 |
| Wolverine | 8 | 399 | 3,381 |
| Green Arrow | 8 | 372 | 1,945 |
| Avengers | 8 | 315 | 3,501 |
| Guardians of the Galaxy | 8 | 180 | 1,772 |
| Spider-Woman | 8 | 137 | 722 |

Why this matters:

- a series name alone is not enough to identify a comic
- volume or start year is often required to separate relaunches
- a collector’s library should treat `Captain America`, `Avengers`, and
  `Amazing Spider-Man` as families of runs, not single series labels

## Repeated Issue Placements

Repeated rows are normal in this cache because the same issue can appear in many
reading lists.

- unique `(series, issue)` pairs: `63,778`
- pairs repeated at least once: `50,118`
- repeated rows beyond the first occurrence: `272,534`

Repeat frequency is heavy:

- `2x`: 14,267 pairs
- `3x`: 6,805 pairs
- `4x`: 4,992 pairs
- `5x`: 3,971 pairs
- `6x`: 3,689 pairs
- `7x`: 2,817 pairs
- `8x`: 2,358 pairs
- `9x`: 2,229 pairs
- `10x`: 1,940 pairs

The most repeated `(series, issue)` pair is:

- `Avengers #1` at `88` rows

## Ambiguous Records

This is the part that matters most for error checking.

There are `137` ComicVine issue ids that map to multiple `(series, issue,
year)` triples in the cache.

That means a ComicVine id is usually stable, but not always represented by a
single series label in the source data.

Examples:

- `959000` appears as `Dark Web #1` in both `2022` and `2023`
- `824449` appears under both `King in Black: Gwenom vs. Carnage` and `King In
  Black: Gwenom vs. Carnage`
- `1033199` appears under both `The Amazing Spider-Man` and `Amazing Spider-Man`
- `108582` appears under multiple Justice League / Justice Society label
  combinations

Recommended unique-issue rule:

1. use `comicvine_issue_id` when present
2. otherwise use normalized `publisher + series + issue + year + volume/start_year`
3. if still ambiguous, add `title` and `list_name`

For manual review, flag records when:

- the same ComicVine id appears under multiple series labels
- the same series/issue/year appears with multiple ComicVine ids
- a series has multiple volume values and no clear start-year separator
- the source label contains relaunch noise or source-site suffixes

For the ordered review list, see [Appendix A: Ambiguous ComicVine Issue IDs](./cbl-cache-ambiguous-comicvine-ids.md).

## Practical Conclusion

For this cache:

- total rows describe reading-list placements
- `76,691` is the best single count for unique comic books represented
- `590` series span multiple volumes
- `137` ComicVine issue ids are ambiguous enough to merit review

That combination gives a collector a useful view of:

- how large the library really is
- where the duplicated reads are
- which runs need volume-aware disambiguation
- where the cache is strong enough to automate and where it needs human review

## Appendices

- [Appendix A: Ambiguous ComicVine Issue IDs](./cbl-cache-ambiguous-comicvine-ids.md)
