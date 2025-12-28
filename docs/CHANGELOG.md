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
