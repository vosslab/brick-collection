# Changelog

## 2026-03-10

### Additions and New Features
- Add `libbrick/common.py` with all shared utility functions moved from `libbrick/__init__.py`.
- Add `libbrick/tui.py` with a reusable `TaskRunnerApp` base class for Textual TUI interfaces, plus `add_tui_args()` and `should_use_tui()` helpers.
- Add Textual TUI mode to `price_out_parts_in_set.py` with `--tui`/`--cli` flags and a `PartsInSetApp` subclass showing part pricing progress in a dashboard.

### Behavior or Interface Changes
- Replace `libbrick/__init__.py` with a docstring-only file to comply with the empty `__init__.py` convention enforced by `tests/test_init_files.py`.
- Update all 15+ caller scripts to use `libbrick.common.X()` instead of `libbrick.X()`.
- `price_out_parts_in_set.py` now defaults to TUI mode when Textual is available and stdout is a TTY; use `--cli` to force plain output.
- Rename shuffle flag from `-X` to `-S` in `price_out_parts_in_set.py`.
- Add `--limit-parts N` / `-L N` flag to `price_out_parts_in_set.py` for testing with a subset of parts.

### Fixes and Maintenance
- Remove unreachable dead code at end of `read_minifigIDpairs_from_file()` in the moved common module.
- Extract `parse_args()`, `clean_data_for_export()`, and `run_cli()` helper functions in `price_out_parts_in_set.py` for cleaner TUI/CLI mode switching.
- Fix `WorkerCancelled` crash in TUI mode by using `asyncio.to_thread` instead of Textual workers for inner task threads, and moving all widget updates out of `process_task` into the async `run_tasks` method. The root cause was accessing Textual widgets from a background thread.

## 2026-02-08
- Add `docs/REPORTLAB_LABELS_PLAN.md` with the full implementation plan for parallel ReportLab label scripts, shared geometry helpers, debug outline/calibration options, and required test coverage.
- Add `libbrick/reportlab_label_utils.py` with Avery geometry presets, slot calculations, debug outlines, and calibration-page helpers.
- Add `reportlab_make_set_labels.py` and `reportlab_make_minifig_labels.py` as ReportLab-based parallel label generators that keep existing `super_make_*` scripts unchanged.
- Add tests for ReportLab geometry, label-data behavior, and PDF smoke rendering.
- Add `reportlab` dependency and update install/usage docs for new scripts and debug flags.

## 2026-01-21
- Resolve merge conflicts in repo hygiene tests, AGENTS, and Markdown style docs.
- Keep report outputs ignored in .gitignore after merging repo hygiene updates.

## 2026-01-19
- Replace non-ASCII symbols in inventory and seller tool text with ASCII equivalents.
- Fix mixed indentation in set ID input and BrickLink wrapper initialization.
- Add request timeouts for image downloads in legacy label scripts and image cache.
- Mark md5 usage as non-security and remove SSL verify disabling in BrickLink image checks.
- Update tests to avoid hardcoded /tmp and to expect escaped MSRP in label output.

## 2026-01-01
- Allow set ID validation for 1000-99999 and BrickLink 910000-910999 ranges.
- Return image paths relative to the output directory when generating label TeX files.
- Split outputs into `output/super_make/`, `output/print_out/`, and `output/lookup/`.
- Compile label TeX files with `latexmk` in the `super_make_*` scripts.
- Save Rebrick cache at the end of `super_make_set_labels.py`.
- Use `-outdir=...` syntax for latexmk compatibility.
- Retry latexmk after cleaning when the previous run left errors behind.
- Close BrickLink wrapper in `seller_tools/set_query_to_listing.py`.
- Run latexmk with `-cd` so image paths resolve relative to the TeX file.
- Escape dollar signs in MSRP output to avoid LaTeX errors.
- Add `import_msrp_csv.py` to load retail prices into the MSRP cache.
- Remove MSRP cache overwrite option from the importer.
- Switch rembg processing to the `isnet-general-use` model for LEGO images.
- Put MSRP on the same line as piece count and bump the LEGO ID size on labels.
- Crop processed images up to 10 percent to better match label aspect ratio.
- Increase label image size and make set name size adapt to long titles.

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
