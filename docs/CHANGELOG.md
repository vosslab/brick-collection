# Changelog

## 2025-12-28
- Remove BrickLink price lines from minifig and set labels.
- Add MSRP from `CACHE/msrp_cache.yml` to set labels.
- Add minifig category and superset count to labels.
- Add rembg + trim processing with raw/processed image caching via `libbrick/image_cache.py`.
- Move core helpers into the `libbrick/` package and wrappers into `libbrick/wrappers/`.
- Add `libbrick/msrp_loader.py` and `libbrick/path_utils.py` for shared cache loading and git root resolution.
- Move legacy label scripts into `legacy/`.
- Add pytest coverage for cache helpers and label rendering, and clean up pyflakes issues.
- Default script outputs now go to `output/` to keep the repo root clean.
- Rename Python scripts to snake_case filenames for consistency.
- Add pytest conftest to ensure repo imports resolve in tests.
- Add `libbrick/minifig_sets.py` helper and split `find_set_for_minifig.py` into a thin CLI.
- Add `docs/USAGE.md` with updated snake_case script names.
- Update docs for output/cache locations and expand `pip_requirements.txt`.
- Add Brewfile for LaTeX tooling and replace ImageMagick trim with Pillow.
- Add setup snippet for `brew bundle` and `pip3 install -r pip_requirements.txt`.
- Add `docs/INSTALL.md` with API key setup details.
