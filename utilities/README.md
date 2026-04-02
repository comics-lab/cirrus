# Cirrus Utilities

This directory contains Cirrus-native utility scripts for the current
post-download pipeline.

These utilities should prefer:

- current Cirrus paths over legacy `grackle` / `fearless` assumptions
- explicit staging and report paths
- dry-run support where practical
- simple, inspectable behavior over hidden automation

Current utilities:

- `cbr_to_cbz.py`: convert `.cbr` archives under intake roots into `.cbz`,
  verify the new archive, and stage originals separately after success
