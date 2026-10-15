# Mapping Flux UI to your home

The dashboard ships with the original author's entity IDs (497 of them).
`entity-map.csv` lists every one, grouped by area, with the files that use it.

## Steps

1. Fill in the `your_entity` column of `entity-map.csv` with your real entity ID.
   Leave a row blank to keep the placeholder (for cards you have not wired up yet).
2. Preview, then apply:

   ```sh
   python3 tools/apply_entity_map.py           # shows which files would change
   python3 tools/apply_entity_map.py --write   # rewrites dashboard/*.yaml
   python3 tools/build_entity_map.py           # refresh the map after edits
   ```

3. Copy `dashboard/` and `www/` into `/config` and register the dashboards (see README).

## Things the map can't fix on its own

- **Helpers.** 44 `input_boolean`, 20 `input_text`, 2 `input_number`, 22 `group`,
  7 `timer`, 23 `automation` and 9 `script` entities are helpers the original
  author created. Map them to helpers you already have, or create them first.
- **User names.** The greeting cards check `user.name == "Rey"` and fall back to
  "Christina" (overview views). Change those names to your household's.
- **Room pictures and wallpapers** live in `www/` and are referenced by file name.
