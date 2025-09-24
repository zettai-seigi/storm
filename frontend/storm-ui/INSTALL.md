# STORM UI Installation Guide

This guide provides detailed instructions for installing and setting up the STORM UI frontend application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Installation](#docker-installation)
- [Troubleshooting](#troubleshooting)
- [Common Issues](#common-issues)

## Prerequisites

### Required Software
- **Node.js**: Version 18.17.0 or higher (LTS recommended)
- **npm**: Version 9.0.0 or higher (comes with Node.js)
- **Git**: For cloning the repository

### Optional Software
- **Docker**: For containerized deployment
- **Python**: Version 3.11+ (for running the backend API)

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB, 8GB recommended
- **Disk Space**: At least 2GB free space
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/zettai-seigi/storm.git
cd storm/frontend/storm-ui

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env.local

# Run development server
npm run dev

# Open http://localhost:3000
```

## Detailed Installation

### Step 1: Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/zettai-seigi/storm.git

# OR clone via SSH
git clone git@github.com:zettai-seigi/storm.git

# Navigate to the frontend directory
cd storm/frontend/storm-ui
```

### Step 2: Install Node.js Dependencies

```bash
# Install all dependencies
npm install

# If you encounter issues, try:
npm install --legacy-peer-deps

# For a clean installation
rm -rf node_modules package-lock.json
npm install
```

### Step 3: Environment Configuration

Create a `.env.local` file in the `storm-ui` directory:

```bash
# Copy the example environment file
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Optional: External Services
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_SENTRY_DSN=

# Optional: Feature Flags
NEXT_PUBLIC_ENABLE_COSTORM=true
NEXT_PUBLIC_ENABLE_EXPORT=true
NEXT_PUBLIC_ENABLE_COLLABORATION=false
```

### Step 4: Backend Setup (Required)

The STORM UI requires both the core STORM library and backend API to be installed. Follow these steps:

```bash
# Navigate to STORM root directory
cd ../..

# Create Python virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# IMPORTANT: Install BOTH requirements files

# 1. First, install core STORM dependencies (from root)
pip install -r requirements.txt

# 2. Then, install backend API dependencies
cd backend
pip install -r requirements.txt

# Create API keys configuration
cat > .env << EOF
OPENAI_API_KEY=your_openai_key_here
BING_SEARCH_API_KEY=your_bing_key_here
EOF

# Run the backend server
python main.py
```

The backend API will start on `http://localhost:8000`

**Note:** Both requirements files are necessary:
- Root `requirements.txt`: Core STORM library (knowledge_storm, litellm, dspy, etc.)
- Backend `requirements.txt`: API server (FastAPI, uvicorn, etc.)

## Configuration

### API Keys Configuration

Create a `secrets.toml` file in the backend directory for API keys:

```toml
# Language Model APIs
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."

# Search APIs (at least one required)
BING_SEARCH_API_KEY = "..."
TAVILY_API_KEY = "tvly-..."
YDC_API_KEY = "..."  # You.com

# Optional: Vector Database
QDRANT_API_KEY = "..."
```

### Port Configuration

If you need to change the default ports:

```bash
# Frontend (change in package.json)
"dev": "next dev -p 3001"  # Changes frontend to port 3001

# Backend (change in backend/main.py)
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changes backend to port 8001

# Update .env.local accordingly
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

## Running the Application

### Development Mode

```bash
# Start the frontend development server
npm run dev

# The application will be available at:
# http://localhost:3000
```

### Production Build

```bash
# Create production build
npm run build

# Start production server
npm start

# Or using PM2 for process management
npm install -g pm2
pm2 start npm --name "storm-ui" -- start
```

### Running Tests

```bash
# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Code Quality Checks

```bash
# Run ESLint
npm run lint

# Run TypeScript type checking
npm run type-check

# Format code with Prettier
npm run format

# Run all checks
npm run check-all
```

## Docker Installation

### Using Docker Compose

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Docker Image Manually

```bash
# Build the Docker image
docker build -t storm-ui:latest .

# Run the container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api \
  storm-ui:latest
```

### Docker Compose Configuration

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  storm-ui:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://storm-api:8000/api
      - NEXT_PUBLIC_WS_URL=ws://storm-api:8000
    depends_on:
      - storm-api
    networks:
      - storm-network

  storm-api:
    build: ../../backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BING_SEARCH_API_KEY=${BING_SEARCH_API_KEY}
    volumes:
      - ../../storm-projects:/app/storm-projects
    networks:
      - storm-network

networks:
  storm-network:
    driver: bridge
```

## Troubleshooting

### Common Issues

#### 1. npm install fails

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Try installing with legacy peer deps
npm install --legacy-peer-deps
```

#### 2. "Cannot find module" errors

```bash
# Ensure you're in the correct directory
pwd  # Should show .../storm/frontend/storm-ui

# Reinstall dependencies
npm ci
```

#### 3. Backend connection issues

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Ensure backend allows frontend origin

# Verify .env.local configuration
cat .env.local
```

#### 4. Port already in use

```bash
# Find process using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or use different port
npm run dev -- -p 3001
```

#### 5. Build errors

```bash
# Check Node.js version
node --version  # Should be 18.17.0 or higher

# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

#### 6. TypeScript errors

```bash
# Run type checking
npm run type-check

# Generate TypeScript declarations
npm run build:types
```

### Environment-Specific Issues

#### macOS
- If you encounter certificate errors, try: `export NODE_TLS_REJECT_UNAUTHORIZED=0` (development only)
- For M1/M2 Macs, ensure you're using ARM64 compatible packages

#### Windows
- Use PowerShell or Git Bash instead of Command Prompt
- Path separators: Use forward slashes in configuration files
- Line endings: Configure Git to use LF: `git config --global core.autocrlf false`

#### Linux
- Ensure you have build essentials: `sudo apt-get install build-essential`
- For permission issues: Use `npm` without `sudo` by fixing npm permissions

### Performance Optimization

#### Development Performance
```bash
# Disable source maps for faster builds
GENERATE_SOURCEMAP=false npm run dev

# Use SWC instead of Babel (already configured)
# Ensure no .babelrc file exists in the project
```

#### Production Optimization
```bash
# Analyze bundle size
npm run analyze

# Enable compression
npm install compression
# Add to next.config.js

# Use CDN for static assets
# Configure in next.config.js
```

### Getting Help

If you continue to experience issues:

1. Check existing issues: https://github.com/zettai-seigi/storm/issues
2. Review logs:
   - Frontend: Browser console and terminal output
   - Backend: `backend/logs/` directory
3. Enable debug mode:
   ```bash
   DEBUG=* npm run dev
   ```
4. Contact support or create an issue with:
   - Error messages
   - Steps to reproduce
   - System information (OS, Node version, etc.)

## Next Steps

After successful installation:

1. **Configure API Keys**: Set up your OpenAI and search API keys in the backend
2. **Create Your First Project**: Navigate to http://localhost:3000/projects/new
3. **Explore Features**:
   - Article generation pipeline
   - Research view
   - Collaborative editing (Co-STORM)
4. **Read Documentation**: Check the README.md for feature documentation

## Additional Resources

- [Main README](./README.md) - Feature documentation and usage guide
- [API Documentation](http://localhost:8000/docs) - Backend API reference
- [Component Storybook](http://localhost:6006) - UI component documentation
- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute to the project