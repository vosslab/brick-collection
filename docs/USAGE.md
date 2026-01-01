# Usage

## Output directory
- Scripts write output files under `output/` by default.
- `super_make_*` scripts use `output/super_make/`.
- `price_out_*` scripts use `output/print_out/`.
- `lookup_*` scripts use `output/lookup/`.

## Setup
- See [docs/INSTALL.md](docs/INSTALL.md) for API keys and installation steps.

## macOS setup
- Install tools and Python deps:
```bash
brew bundle
pip3 install -r pip_requirements.txt
```
- `brew bundle` installs `mactex-no-gui` for LaTeX.

## Caches and images
- MSRP cache lives at `CACHE/msrp_cache.yml`.
- Label image cache uses `images/raw/` and `images/processed/` with `rembg` + Pillow trim.
- Default rembg model is `isnet-general-use` for LEGO set images.
- Processed images may be cropped up to 10 percent to better fit the label aspect ratio.

## MSRP cache import
- `import_msrp_csv.py`: add retail prices to `CACHE/msrp_cache.yml`.
- CSV needs `Number` and `Retail` columns (comma, tab, or whitespace).
- Example input:
```csv
Number,Retail
10294-1,679.99
```
- Example run:
```bash
./import_msrp_csv.py path/to/msrp.csv
```
- Use `--assume-cents` if prices are already in cents.

## Label scripts
- `super_make_minifig_labels.py`: generate minifig labels from a minifig ID list.
- `super_make_set_labels.py`: generate set labels from a set ID list.

## Lookups and exports
- `lookup_minifig_bricklink.py`: BrickLink minifig lookup to CSV.
- `lookup_set_bricklink.py`: BrickLink set lookup to CSV.
- `lookup_set_rebrick.py`: Rebrickable set lookup to CSV.
- `gimme_set_data.py`: combined set data output to CSV.
- `get_minifig_from_set_bricklink.py`: list minifigs per set to CSV.
- `price_out_elements.py`: element price output to CSV.
- `price_out_parts_in_set.py`: part price output to CSV.
- `quick_set_info.py`: summary set info to CSV.
- `lego_set_csv_to_bricklink_xml.py`: convert set CSV to BrickLink XML.
- `inventory_xml_csv_tool.py`: convert BrickLink inventory XML and CSV.

## Helpers
- `find_set_for_minifig.py`: interactive minifig to set matching.

## Legacy scripts
- `legacy/make_minifig_labels.py`
- `legacy/make_set_labels.py`
- `legacy/citizen_brick_calc.py`
