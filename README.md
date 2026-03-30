# brick-collection

Python scripts for managing a personal LEGO collection: label generation,
set and minifig lookups, part pricing, and BrickLink/Rebrickable/Brickset
API integrations. Intended for personal use by a LEGO collector who wants
printable labels and spreadsheet exports from their collection data.

## Quick start

```bash
brew bundle
pip3 install -r pip_requirements.txt
source source_me.sh
```

API keys for BrickLink, Brickset, and Rebrickable are required for most scripts.
See [docs/INSTALL.md](docs/INSTALL.md) for key file formats and placement.

## Documentation

- [docs/INSTALL.md](docs/INSTALL.md): dependencies, API key setup, and macOS install steps.
- [docs/USAGE.md](docs/USAGE.md): script reference, output directories, and usage examples.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): record of changes by date.

## Testing

```bash
source source_me.sh && python -m pytest tests/
```

## Maintainer

Neil Voss, https://bsky.app/profile/neilvosslab.bsky.social
