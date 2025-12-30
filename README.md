# Kasa Smartplug Exporter

A Prometheus exporter for Kasa smart plugs that exposes power consumption metrics.

## Quick Start

### Option 1: Pre-built Docker Image (Recommended)

```bash
# Create environment file
cp .env.example .env
# Edit .env with your Kasa credentials

# Run with Docker Compose
docker compose up -d

# Or run directly
docker run -d \
  --name kasa-smartplug-exporter \
  --network host \
  -v $(pwd)/.env:/app/.env:ro \
  ghcr.io/vaibzzz123/kasa-smartplug-exporter:latest
```

### Option 2: Local Development

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run
python main.py
```

## Prometheus Metrics

Available at `http://localhost:4467/metrics`:

- `kasa_smartplug_milliwatts` - Current power consumption in milliwatts
- `kasa_smartplug_milliamperes` - Current consumption in milliamperes  
- `kasa_smartplug_millivolts` - Voltage in millivolts
- `kasa_smartplug_energy_wh` - Total energy consumption in watt-hours

All metrics include labels: `device_alias`, `device_model`

## Configuration

Environment variables (`.env` file):

```bash
# Required for newer devices (KP125M, etc.)
KASA_USERNAME=your_email@example.com
KASA_PASSWORD=your_password

# Optional: Filter by device models (comma-separated)
KASA_MODELS=KP125M,HS103

# Optional: Exporter settings
PORT=4467
POLL_INTERVAL=10
LOG_LEVEL=INFO
```

## Docker Deployment

### Using Docker Compose

The `docker-compose.yml` uses the pre-built image by default:

```bash
docker compose up -d
```

To build locally instead, edit `docker-compose.yml`:
```yaml
# Comment out image line and uncomment build line
# image: ghcr.io/vaibzzz123/kasa-smartplug-exporter:latest
build: .
```

### Using Docker Directly

```bash
docker run -d \
  --name kasa-smartplug-exporter \
  --network host \
  -v $(pwd)/.env:/app/.env:ro \
  ghcr.io/vaibzzz123/kasa-smartplug-exporter:latest
```

**Note:** Host networking is required for device discovery to work properly, as Docker's default network isolation prevents UDP broadcast discovery.

## Automated Docker Builds

This project uses GitHub Actions to automatically build and push Docker images to GitHub Container Registry (GHCR).

### Build Triggers

- **Push to `main`** → Builds `main-latest` and `latest` tags
- **Git tags** (`v1.0.0`) → Builds versioned tags  
- **Manual trigger** → Available in Actions tab

### Using Pre-built Images

```bash
# Pull latest
docker pull ghcr.io/vaibzzz123/kasa-smartplug-exporter:latest

# Pull specific version
docker pull ghcr.io/vaibzzz123/kasa-smartplug-exporter:v1.0.0
```

### Creating a Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically build and push the tagged image.

## Project Structure

- `main.py` - Main application entry point
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container build configuration
- `docker-compose.yml` - Docker Compose configuration
- `.github/workflows/docker.yml` - Automated build pipeline

## Security

This application requires Kasa cloud credentials for newer devices. Please ensure:

- Store credentials securely in `.env` file (excluded from git)
- Never commit actual credentials to version control
- Use a dedicated Kasa account if possible
- Credentials are only used for device discovery and Kasa service communication

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# Build Docker image locally
docker build -t kasa-smartplug-exporter .
```

## Troubleshooting

**Device discovery issues:**
- Ensure host networking (`--network host`) when using Docker
- Check KASA_USERNAME and KASA_PASSWORD are set correctly
- Verify devices are on the same network

**Permission errors:**
- Ensure `.env` file permissions are restrictive: `chmod 600 .env`

## License

MIT License

Copyright (c) 2025 Vab Kapoor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

