# ReportLab Parallel Label Pipeline for Brick Collection

## Summary
Create two new scripts that run in parallel to the existing LaTeX scripts and do not modify their behavior:
- `/Users/vosslab/nsh/brick-collection/reportlab_make_set_labels.py`
- `/Users/vosslab/nsh/brick-collection/reportlab_make_minifig_labels.py`

These scripts will keep the same core data-fetch and image-cache flow as `super_make*.py`, but render directly to PDF with ReportLab using fixed Avery geometry constants (not template files), with optional debug calibration/outline flags, and default PDF-only output in `/Users/vosslab/nsh/brick-collection/output/super_make/`.

## Locked decisions
- Layout basis: measured hardcoded constants.
- CLI shape: same primary arg shape as existing scripts, plus optional flags.
- Output scope: PDF only by default.
- Template IDs: match current scripts.
	- Sets: Avery 5163.
	- Minifigs: Avery 18260.
- Calibration: optional debug flags, default off.

## Public interfaces and CLI behavior
- New script interfaces:
	- `reportlab_make_set_labels.py <set_id_input_file> [optional flags]`
	- `reportlab_make_minifig_labels.py <minifig_id_input_file> [optional flags]`
- Optional flags to add (both scripts):
	- `--draw-outlines` / `--no-draw-outlines` (default off).
	- `--calibration-page` / `--no-calibration-page` (default off).
- Output naming:
	- PDF path stays aligned with current convention:
		- `/Users/vosslab/nsh/brick-collection/output/super_make/labels-<input-stem>.pdf`
- Existing scripts unchanged:
	- `/Users/vosslab/nsh/brick-collection/super_make_set_labels.py`
	- `/Users/vosslab/nsh/brick-collection/super_make_minifig_labels.py`

## Implementation design
1. Add shared ReportLab helper module:
- New file: `/Users/vosslab/nsh/brick-collection/libbrick/reportlab_label_utils.py`
- Contents:
	- `ImpositionConfig` dataclass for sheet geometry and behavior.
	- Geometry helpers for slot placement and bounds checks.
	- Drawing helpers for outlines and optional calibration page.
	- Text fit helpers (font size fallback for long names).
	- Image drawing helper with aspect-preserving fit into target box.
- Keep this module generic so both new scripts call it.

2. Add fixed Avery geometry constants:
- In `/Users/vosslab/nsh/brick-collection/libbrick/reportlab_label_utils.py`, define two presets:
	- `AVERY_5163_SET_CONFIG`
	- `AVERY_18260_MINIFIG_CONFIG`
- Constants expressed in points and validated against letter page dimensions.

3. Build set ReportLab script:
- New file: `/Users/vosslab/nsh/brick-collection/reportlab_make_set_labels.py`
- Reuse existing data path from `super_make_set_labels.py`:
	- `libbrick.read_setIDs_from_file`
	- BrickLink + Rebrick wrappers
	- `libbrick.msrp_loader.load_msrp_cache`
	- `libbrick.image_cache.get_cached_image`
- Replace LaTeX string assembly with in-memory per-label drawing:
	- Left image panel.
	- Right text panel with dynamic set-name sizing.
	- Fields: LEGO ID, set name, category, release year, pieces, optional MSRP.

4. Build minifig ReportLab script:
- New file: `/Users/vosslab/nsh/brick-collection/reportlab_make_minifig_labels.py`
- Reuse existing data path from `super_make_minifig_labels.py`:
	- `libbrick.read_minifigIDpairs_from_file`
	- BrickLink wrapper calls for minifig/category/superset count
	- `libbrick.image_cache.get_cached_image`
- Replace LaTeX generation with direct draw:
	- ID header, name with shrink logic, release year, optional category, optional "appears in N sets".
	- Same filtering/guard behavior as current script (weight checks, sorting, cache saves).

5. Keep image pipeline unchanged:
- Continue using existing image normalization/background removal/crop pipeline in:
	- `/Users/vosslab/nsh/brick-collection/libbrick/image_cache.py`
- Render from cached processed PNG paths.

6. Optional debug rendering:
- `--draw-outlines`: draw slot borders and content bounding hints.
- `--calibration-page`: prepend one page with ruler and slot grid for print alignment checks.

7. Dependency and docs updates:
- Add `reportlab` to `/Users/vosslab/nsh/brick-collection/pip_requirements.txt`.
- Update `/Users/vosslab/nsh/brick-collection/docs/USAGE.md` with new scripts and optional flags.
- Update `/Users/vosslab/nsh/brick-collection/docs/INSTALL.md` to mention ReportLab dependency.
- Append entry to `/Users/vosslab/nsh/brick-collection/docs/CHANGELOG.md`.

## Testing plan
1. Unit tests for geometry and placement:
- New file: `/Users/vosslab/nsh/brick-collection/tests/test_reportlab_layout_geometry.py`
- Cases:
	- All slots are on-page for both Avery configs.
	- Adjacent slots do not overlap.
	- Label drawable area remains positive after insets.

2. Unit tests for label text composition:
- New file: `/Users/vosslab/nsh/brick-collection/tests/test_reportlab_set_label.py`
- New file: `/Users/vosslab/nsh/brick-collection/tests/test_reportlab_minifig_label.py`
- Cases:
	- MSRP appears only when available.
	- Long names trigger down-sizing path.
	- Optional fields render conditionally (category/superset count).

3. Smoke render tests:
- New file: `/Users/vosslab/nsh/brick-collection/tests/test_reportlab_render_smoke.py`
- Use mocked data + monkeypatched image cache path and generate tiny sample PDFs in temp dir.
- Assert:
	- PDF created and non-empty.
	- Page count is expected for N labels.
	- Calibration/outline flags alter output path behavior without exceptions.

4. Repo hygiene checks after implementation:
- Run with Python 3.12:
	- `/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/test_reportlab_layout_geometry.py tests/test_reportlab_set_label.py tests/test_reportlab_minifig_label.py tests/test_reportlab_render_smoke.py`
	- `/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/test_pyflakes_code_lint.py`
	- `/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/test_ascii_compliance.py`
	- `/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/test_shebangs.py`

## Compatibility and non-goals
- Compatibility:
	- No behavior change to existing `super_make*.py` scripts.
	- Keep existing API wrapper usage and cache semantics.
- Non-goals for v1:
	- No removal/refactor of LaTeX scripts.
	- No runtime-selectable Avery stock matrix beyond the two fixed targets.
	- No manifest JSON output by default.

## Assumptions and defaults
- ReportLab is acceptable as a new required dependency in this repo.
- Existing image cache artifacts in `/Users/vosslab/nsh/brick-collection/images/processed/` are valid inputs for PDF rendering.
- Default run should produce only final PDF under `/Users/vosslab/nsh/brick-collection/output/super_make/`.
- Optional debug flags exist only to aid alignment validation and remain off by default.
