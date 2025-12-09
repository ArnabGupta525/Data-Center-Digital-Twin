# Data Center Digital Twin - Docker Installation Guide

This guide details the procedure for deploying the Data Center Digital Twin using Docker on **Windows**, **macOS**, or **Linux**.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Platform-Specific Setup](#platform-specific-setup)
  - [Linux](#linux-setup)
  - [macOS](#macos-setup)
  - [Windows](#windows-setup)
- [Using Custom Datasets](#using-custom-datasets)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Prerequisites

### All Platforms

1. **Docker Desktop** (or Docker Engine on Linux)
   - Download from: https://www.docker.com/products/docker-desktop
   - Minimum version: 20.10+
   - Ensure Docker Compose is included (v2.0+)

2. **System Requirements**
   - RAM: 4GB minimum, 8GB recommended
   - Disk Space: 2GB for Docker image + your dataset
   - CPU: 2+ cores recommended

### Platform-Specific Requirements

#### Linux
- X11 server (usually pre-installed)
- User must be in `docker` group

#### macOS
- **XQuartz** (X11 server for macOS)
  - Download: https://www.xquartz.org/
  - Version 2.8.0 or later

#### Windows
- **VcXsrv** or **Xming** (X11 server for Windows)
  - VcXsrv Download: https://sourceforge.net/projects/vcxsrv/
  - Xming Download: https://sourceforge.net/projects/xming/

---

## Quick Start

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/Data-Center-Digital-Twin.git
cd Data-Center-Digital-Twin
```

### 2. Build the Docker Image

```bash
docker compose build
```

> **Note**: The initial build may take 5-10 minutes as it trains the ML optimizer models.

### 3. Run the Application

Choose the command appropriate for your platform:

**Linux:**
```bash
# Allow Docker to access X server
xhost +local:docker

# Run the application
docker compose up
```

**macOS:**
```bash
# Start XQuartz first, then:
docker compose -f docker-compose.yml -f docker-compose.mac.yml up
```

**Windows:**
```bash
# Start VcXsrv first (see Windows setup below), then:
docker compose -f docker-compose.yml -f docker-compose.windows.yml up
```

### 4. Stop the Application

Press `Ctrl+C` in the terminal, or run:

```bash
docker compose down
```

---

## Platform-Specific Setup

### Linux Setup

#### 1. Install Docker

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Allow X11 Access

```bash
# Allow Docker containers to access X server
xhost +local:docker
```

> **Tip**: Add this command to your `~/.bashrc` to make it permanent:
> ```bash
> echo "xhost +local:docker > /dev/null 2>&1" >> ~/.bashrc
> ```

#### 3. Run the Application

```bash
docker compose up
```

#### 4. (Optional) Run in Background

```bash
docker compose up -d
docker compose logs -f  # View logs
```

---

### macOS Setup

#### 1. Install Prerequisites

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Install XQuartz**
   ```bash
   # Using Homebrew
   brew install --cask xquartz
   
   # Or download from https://www.xquartz.org/
   ```

#### 2. Configure XQuartz

1. **Start XQuartz**
   - Open XQuartz from Applications/Utilities
   - Or run: `open -a XQuartz`

2. **Configure XQuartz Settings**
   - Go to **XQuartz → Preferences**
   - **Security** tab:
     - Check "Allow connections from network clients"
   - **Restart XQuartz** after changing settings

3. **Allow Network Connections**
   ```bash
   # In a terminal
   xhost + 127.0.0.1
   # Or for broader access (less secure):
   xhost +local:
   ```

#### 3. Run the Application

```bash
# Make sure XQuartz is running first
docker compose -f docker-compose.yml -f docker-compose.mac.yml up
```

#### 4. Troubleshooting macOS

If the GUI doesn't appear:

```bash
# Check if XQuartz is running
ps aux | grep XQuartz

# Verify DISPLAY variable
echo $DISPLAY  # Should show something like /private/tmp/com.apple.launchd.xxx/org.xquartz:0

# Reset XQuartz permissions
xhost +
```

---

### Windows Setup

#### 1. Install Prerequisites

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Enable WSL2 backend (recommended)

2. **Install VcXsrv (X Server)**
   - Download from https://sourceforge.net/projects/vcxsrv/
   - Install with default settings

#### 2. Configure VcXsrv

1. **Launch XLaunch** (VcXsrv configuration wizard)

2. **Configuration Steps:**
   - **Display settings**: Select "Multiple windows", Display number: `0`
   - **Client startup**: Select "Start no client"
   - **Extra settings**: 
     - Check "Disable access control"
     - Check "Native opengl" (optional, may improve performance)
   - **Finish**: Save configuration (optional)

3. **Start VcXsrv**
   - Verify the "X" icon appears in the system tray
   - Keep VcXsrv running while using the application

#### 3. Configure Windows Firewall

VcXsrv needs to accept connections:

1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Find **VcXsrv** and ensure both Private and Public are checked
4. If not listed, click **Allow another app** and browse to VcXsrv

#### 4. Run the Application

```powershell
# In PowerShell or Command Prompt
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up
```

#### 5. Troubleshooting Windows

**GUI doesn't appear:**

1. **Check VcXsrv is running**
   - Look for "X" icon in system tray

2. **Verify firewall settings**
   ```powershell
   # In PowerShell (as Administrator)
   New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
   ```

3. **Check Docker networking**
   ```powershell
   # Verify host.docker.internal resolves
   docker run --rm alpine ping -c 1 host.docker.internal
   ```

4. **Alternative: Use Xming**
   - If VcXsrv doesn't work, try Xming
   - Download: https://sourceforge.net/projects/xming/
   - Launch with: `Xming :0 -clipboard -multiwindow -ac`

---

## Using Custom Datasets

### Dataset Format

Your dataset must be in JSON format matching this structure:

```json
[
  {
    "meta_data": {
      "entityId": "server-001"
    },
    "payload": {
      "ambient_temp_c": 25.0,
      "inlet_temp_c": 22.0,
      "server_workload_percent": 65.0
    }
  }
]
```

### Loading Your Dataset

1. **Place your dataset in the `data/` directory:**
   ```
   Data-Center-Digital-Twin/
   ├── data/
   │   └── datacenter_full_state_list.json  # Your custom dataset
   ```

2. **Run with your dataset:**
   ```bash
   docker compose up
   ```

The entrypoint script automatically detects and loads files from the `data/` directory.

### Dataset Requirements

- **File name**: `datacenter_full_state_list.json`
- **Format**: JSON array of objects
- **Required fields**:
  - `meta_data.entityId` (string): Unique server/rack identifier
  - `payload.ambient_temp_c` (number): Ambient temperature in Celsius
  - `payload.inlet_temp_c` (number): Inlet temperature in Celsius
  - `payload.server_workload_percent` (number): Workload percentage (0-100)

### Multiple Scenarios

For realistic simulation, provide **multiple scenarios per machine**:

```json
[
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {"ambient_temp_c": 20, "inlet_temp_c": 18, "server_workload_percent": 30}
  },
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {"ambient_temp_c": 25, "inlet_temp_c": 22, "server_workload_percent": 70}
  },
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {"ambient_temp_c": 30, "inlet_temp_c": 26, "server_workload_percent": 90}
  }
]
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Display settings
DISPLAY=:0

# Qt settings
QT_X11_NO_MITSHM=1
QT_DEBUG_PLUGINS=0

# Application settings
PYTHONUNBUFFERED=1
```

### Volume Mounts

The docker-compose configuration mounts these directories:

- `./data` → `/data` (read-only): Your custom datasets
- `./db` → `/app/db`: SQLite database (persistent)
- `./models` → `/app/models`: Trained ML models (persistent)
- `./logs` → `/app/logs`: Application logs

### Customizing the Build

Edit `Dockerfile` to:
- Change Python version
- Add additional dependencies
- Modify optimizer training parameters

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to X server"

**Linux:**
```bash
xhost +local:docker
export DISPLAY=:0
```

**macOS:**
```bash
# Make sure XQuartz is running
open -a XQuartz
xhost + 127.0.0.1
```

**Windows:**
- Ensure VcXsrv is running (check system tray)
- Check firewall settings
- Try restarting VcXsrv with `-ac` flag

#### 2. "Permission denied" errors

```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER ./data ./db ./models ./logs
```

#### 3. GUI appears but is blank/frozen

```bash
# Try disabling shared memory
export QT_X11_NO_MITSHM=1

# Or add to docker-compose.yml:
environment:
  - QT_X11_NO_MITSHM=1
```

#### 4. "Optimizer models not found"

The models are trained during the first build. If training failed:

```bash
# Rebuild with verbose output
docker compose build --no-cache --progress=plain

# Or train manually after starting container
docker compose run datacenter-twin python train_optimizer.py
```

#### 5. High CPU/Memory usage

```bash
# Limit resources in docker-compose.yml
services:
  datacenter-twin:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

### Viewing Logs

```bash
# View container logs
docker compose logs -f

# View application logs
docker compose exec datacenter-twin tail -f /app/logs/app.log

# Debug mode
docker compose run -e QT_DEBUG_PLUGINS=1 datacenter-twin
```

### Cleaning Up

```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes database and models)
docker compose down -v

# Remove images
docker rmi datacenter-digital-twin:latest

# Complete cleanup
docker system prune -a
```

---

## Advanced Usage

### Running in Headless Mode (No GUI)

For server deployments or automated testing:

```bash
# Override the command
docker compose run datacenter-twin python -c "
from data_pipeline import DataIngestor
ingestor = DataIngestor()
print(f'Loaded {len(ingestor.machine_ids)} machines')
"
```

### Building for Different Architectures

```bash
# Build for ARM64 (e.g., Apple Silicon, Raspberry Pi)
docker buildx build --platform linux/arm64 -t datacenter-twin:arm64 .

# Build for AMD64 (standard x86_64)
docker buildx build --platform linux/amd64 -t datacenter-twin:amd64 .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t datacenter-twin:latest .
```

### Pushing to Docker Hub

```bash
# Tag the image
docker tag datacenter-digital-twin:latest yourusername/datacenter-twin:latest

# Login to Docker Hub
docker login

# Push
docker push yourusername/datacenter-twin:latest
```

### Using Pre-built Image

If you publish to Docker Hub, users can run directly:

```bash
# Pull and run
docker pull yourusername/datacenter-twin:latest
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/data:/data:ro \
  yourusername/datacenter-twin:latest
```

### Development Mode

Mount source code for live development:

```yaml
# docker-compose.dev.yml
services:
  datacenter-twin:
    volumes:
      - .:/app  # Mount entire project
      - /app/__pycache__  # Exclude cache
    command: python what_if_engine.py
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Additional Resources

- **Dataset Format Specification**: See `DATASET-FORMAT.md`
- **Project Documentation**: See main `README.md`
- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/Data-Center-Digital-Twin/issues)
- **Docker Documentation**: https://docs.docker.com/

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker-compose logs`
3. Search existing [GitHub Issues](https://github.com/yourusername/Data-Center-Digital-Twin/issues)
4. Create a new issue with:
   - Your OS and version
   - Docker version (`docker --version`)
   - Complete error message
   - Steps to reproduce

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
