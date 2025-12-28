# Install

## macOS
```bash
brew bundle
pip3 install -r pip_requirements.txt
```

## API keys
Place API key files in the repo root.

### BrickLink
File: `bricklink_api_private.yml`
```yaml
consumer_key: "YOUR_CONSUMER_KEY"
consumer_secret: "YOUR_CONSUMER_SECRET"
token_value: "YOUR_TOKEN_VALUE"
token_secret: "YOUR_TOKEN_SECRET"
```

### Brickset
File: `brickset_api_private.yml`
```yaml
web_services_key_2: "YOUR_BRICKSET_KEY"
```

### Rebrickable
File: `rebrick_api_key.yml`
```yaml
api_key: "YOUR_REBRICKABLE_KEY"
```

### Optional: Google Drive (test script)
Used by `test_google_image.py`.

File: `service_key.json` (service account JSON file from Google Cloud)
