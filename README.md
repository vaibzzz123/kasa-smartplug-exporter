# Kasa Smartplug Exporter

A basic Python project for exporting data from Kasa smart plugs.

## Setup

1. Create and activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate, on fish shell: source venv/bin/activate.fish
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (copy .env.example to .env and update values)

4. Run the application:
```bash
python main.py
```

## Project Structure

- `main.py` - Main entry point
- `requirements.txt` - Python dependencies
- `venv/` - Virtual environment (gitignored)


## Docker Deployment

### Using Docker Compose (Recommended)

1. Copy the environment file and configure your credentials:
```bash
cp .env.example .env
```

2. Edit `.env` with your Kasa credentials and desired settings

3. Run with Docker Compose:
```bash
docker compose up -d
```
Or if you're on older Docker composeversions:
```bash
docker-compose up -d
```

### Using Docker directly

1. Build the image:
```bash
docker build -t kasa-smartplug-exporter .
```

2. Run the container with host networking (required for device discovery):
```bash
docker run -d \
  --name kasa-smartplug-exporter \
  --network host \
  -v $(pwd)/.env:/app/.env:ro \
  kasa-smartplug-exporter
```

The Prometheus metrics will be available at `http://localhost:4467/metrics`

**Note:** Host networking is required for device discovery to work properly, as Docker's default network isolation prevents UDP broadcast discovery.

## Development

Add new dependencies to `requirements.txt` and install them with:
```bash
pip install -r requirements.txt
```
