# Changelog

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
