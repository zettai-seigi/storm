# STORM UI

A modern, responsive web interface for the STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking) knowledge curation system. Built with Next.js 14, TypeScript, and Tailwind CSS.

![STORM UI Dashboard](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

STORM UI is a comprehensive web application that provides an intuitive interface for AI-powered article generation and collaborative knowledge curation. It serves as the frontend for the STORM system, enabling users to generate Wikipedia-quality articles through multi-perspective research and AI-driven content synthesis.

### Current Status

✅ **Production Ready**: Both frontend and backend are fully implemented and functional.
- **Frontend**: Next.js 14 application with complete UI components
- **Backend**: FastAPI server with file-based storage system
- **STORM Integration**: Version 1.1.0 integrated and working
- **Storage**: File-based project storage (no database required)
- **API**: RESTful endpoints at `http://localhost:8000/api`
- **UI**: Responsive web interface at `http://localhost:3000`

### Key Features

- 🚀 **Automated Article Generation** - Generate comprehensive articles from any topic
- 🔍 **Multi-Source Research** - Integrate multiple search engines and data sources
- 👥 **Collaborative Editing** (Co-STORM) - Real-time collaboration with AI experts
- 📊 **Pipeline Visualization** - Track progress through each generation stage
- 📝 **Rich Text Editing** - Full-featured editor with citation management
- 📈 **Analytics Dashboard** - Monitor usage, costs, and performance metrics
- 🎨 **Modern UI/UX** - Clean, responsive design with dark mode support
- 🔐 **Secure Configuration** - Safe API key management and storage

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Development](#development)
- [API Integration](#api-integration)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality

#### 1. Project Management
- Create, edit, and delete article generation projects
- Project templates for common use cases
- Batch processing for multiple articles
- Project search and filtering
- Export/import project configurations

#### 2. Article Generation Pipeline
The STORM pipeline consists of four main stages:

- **Research Phase**: Automated multi-perspective research using configured search engines
- **Outline Generation**: Hierarchical topic organization based on research
- **Article Writing**: Section-by-section content generation with citations
- **Polish & Review**: Final editing, summary generation, and quality checks

#### 3. Configuration System
- **LLM Configuration**: Support for multiple providers (OpenAI, Anthropic, Azure, etc.)
- **Retriever Setup**: Configure search engines (Bing, You.com, Tavily, DuckDuckGo)
- **Pipeline Customization**: Control which stages to run and their parameters
- **Template Management**: Save and reuse configurations

#### 4. Research Visualization
- View simulated expert conversations
- Browse and manage information sources
- Citation tracking and verification
- Source credibility indicators
- Research timeline and history

#### 5. Collaborative Features (Co-STORM)
- Real-time discourse with AI experts
- Interactive mind map visualization
- Dynamic question generation
- Shared knowledge base
- Session recording and playback

#### 6. Export & Integration
- Multiple export formats (Markdown, HTML, PDF, DOCX)
- API access for programmatic usage
- Webhook notifications
- Integration with external knowledge bases

### User Interface

#### Dashboard
- Project overview with status indicators
- Recent activity feed
- Quick actions toolbar
- Usage statistics
- System health monitoring

#### Editor Features
- Rich text editing with TipTap
- Real-time preview
- Citation management
- Table of contents generation
- Version history
- Collaborative editing indicators

#### Visualization Components
- Pipeline progress tracking
- Mind map for knowledge organization
- Analytics charts and graphs
- Source relationship diagrams

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/zettai-seigi/storm.git
cd storm

# Start the backend (Terminal 1)
cd backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Start the frontend (Terminal 2)
cd frontend/storm-ui
npm install
cp .env.example .env.local
npm run dev  # Runs on http://localhost:3000
```

For detailed installation instructions, see [INSTALL.md](./INSTALL.md).

## Usage

### Creating Your First Article

1. **Start the Application**
   ```bash
   npm run dev
   # Navigate to http://localhost:3000
   ```

2. **Configure API Keys**
   - Go to Settings → API Configuration
   - Add your OpenAI API key
   - Add at least one search API key (Bing, Tavily, etc.)

3. **Create a New Project**
   - Click "New Project" on the dashboard
   - Enter your topic and description
   - Select a configuration template or customize settings
   - Click "Create Project"

4. **Run the Pipeline**
   - Open your project from the dashboard
   - Click "Start Pipeline" to begin generation
   - Monitor progress in real-time
   - Review and edit the generated article

5. **Export Your Article**
   - Click "Export" in the article editor
   - Choose your format (Markdown, HTML, PDF)
   - Download or share your article

### Advanced Usage

#### Using Co-STORM for Collaboration

```typescript
// Example: Starting a Co-STORM session
const session = await createCoStormSession({
  topic: "Quantum Computing",
  experts: ["Physics Professor", "Tech Industry Expert"],
  humanModerator: true
});
```

#### Batch Processing

```bash
# Process multiple topics from a CSV file
npm run batch -- --input topics.csv --template academic --output ./articles
```

#### API Integration

```typescript
// Example: Using the STORM API
import { StormClient } from '@/services/api';

const client = new StormClient({
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  apiKey: process.env.API_KEY
});

const project = await client.createProject({
  title: "Climate Change Impacts",
  config: {
    llm: { model: "gpt-4", temperature: 0.7 },
    retriever: { type: "bing", maxResults: 20 }
  }
});

await client.runPipeline(project.id);
```

## Architecture

### Technology Stack

#### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.0
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **Rich Text**: TipTap Editor
- **Charts**: Recharts
- **Visualizations**: D3.js

#### Backend Integration
- **API**: RESTful endpoints via Axios
- **WebSocket**: Real-time updates for pipeline progress
- **File Storage**: Local file system or cloud storage
- **Authentication**: JWT tokens (optional)

### Project Structure

```
storm/
├── backend/                 # FastAPI backend (IMPLEMENTED)
│   ├── main.py             # FastAPI application entry
│   ├── routers/            # API endpoints
│   │   ├── projects.py     # Project CRUD operations
│   │   ├── pipeline.py     # Pipeline execution
│   │   ├── settings.py     # Configuration management
│   │   ├── models.py       # LLM model management
│   │   └── docs.py         # Documentation endpoints
│   ├── services/           # Business logic
│   │   ├── file_service.py # File-based storage
│   │   ├── storm_runner.py # STORM integration
│   │   └── config_service.py # Configuration handling
│   └── storm-projects/     # File storage directory
│       ├── projects.json   # Project index
│       └── projects/       # Individual project files
├── frontend/
│   └── storm-ui/           # Next.js frontend (IMPLEMENTED)
│       ├── app/            # App Router pages
│       │   ├── projects/   # Project management UI
│       │   ├── settings/   # Settings UI
│       │   ├── analytics/  # Analytics dashboard
│       │   ├── activity/   # Activity feed
│       │   ├── knowledge-base/ # Knowledge browser
│       │   └── help/       # Help documentation
│       ├── src/
│       │   ├── components/ # React components
│       │   ├── services/   # API client services
│       │   ├── store/      # Zustand state management
│       │   ├── hooks/      # Custom React hooks
│       │   └── types/      # TypeScript definitions
│       └── public/         # Static assets
└── knowledge_storm/        # Core STORM library

### Component Architecture

```typescript
// Example: Component composition pattern
<DashboardLayout>
  <ProjectList>
    <ProjectCard />
    <ProjectCard />
  </ProjectList>
  <Sidebar>
    <QuickActions />
    <RecentActivity />
  </Sidebar>
</DashboardLayout>
```

### State Management

The application uses Zustand for state management with the following stores:

- **projectStore**: Project CRUD operations and caching
- **pipelineStore**: Pipeline execution and progress tracking
- **configStore**: User preferences and API configurations
- **uiStore**: UI state (modals, sidebars, themes)
- **analyticsStore**: Usage metrics and statistics

```typescript
// Example: Using Zustand store
import { useProjectStore } from '@/store/projectStore';

function ProjectList() {
  const { projects, loading, fetchProjects } = useProjectStore();

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div>
      {projects.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
```

## Development

### Setup Development Environment

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run with debug logging
DEBUG=storm:* npm run dev
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
npm run format       # Format with Prettier
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:e2e     # Run E2E tests
npm run storybook    # Start Storybook
npm run analyze      # Analyze bundle size
```

### Code Style Guide

#### TypeScript Conventions

```typescript
// Use interface for object types
interface ProjectConfig {
  llm: LLMConfig;
  retriever: RetrieverConfig;
}

// Use type for unions and primitives
type ProjectStatus = 'draft' | 'running' | 'completed' | 'failed';

// Use const assertions for constants
const PIPELINE_STAGES = ['research', 'outline', 'write', 'polish'] as const;

// Prefer nullish coalescing over logical OR
const value = config.temperature ?? 0.7; // Not: config.temperature || 0.7
```

#### Component Patterns

```typescript
// Functional component with TypeScript
interface ProjectCardProps {
  project: Project;
  onSelect?: (id: string) => void;
  className?: string;
}

export function ProjectCard({
  project,
  onSelect,
  className
}: ProjectCardProps) {
  return (
    <Card className={cn("cursor-pointer", className)}>
      {/* Component content */}
    </Card>
  );
}
```

#### File Naming Conventions

- Components: PascalCase (e.g., `ProjectCard.tsx`)
- Utilities: camelCase (e.g., `formatDate.ts`)
- Types: PascalCase with `.types.ts` extension
- Tests: Same name with `.test.ts` or `.spec.ts`
- Stories: Same name with `.stories.tsx`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: Add new feature"

# Push and create PR
git push origin feature/your-feature
```

#### Commit Message Convention

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/config changes

## API Integration

### Backend Requirements

The STORM UI backend is fully implemented and provides:

- ✅ Project CRUD operations with file-based storage
- ✅ Pipeline execution with STORM integration
- ✅ Real-time status updates
- ✅ Configuration management
- ✅ Model provider integration (OpenAI, Ollama, LMStudio)
- ✅ Export functionality

### Available API Endpoints

```typescript
// Project Management
GET    /api/projects/                    // List all projects
POST   /api/projects/                    // Create new project
GET    /api/projects/{id}                // Get project details
PUT    /api/projects/{id}                // Update project
DELETE /api/projects/{id}                // Delete project
POST   /api/projects/{id}/duplicate      // Duplicate project
GET    /api/projects/{id}/export         // Export article
GET    /api/projects/{id}/conversations  // Get research conversations
GET    /api/projects/stats/summary      // Get project statistics

// Pipeline Execution
POST   /api/pipeline/{id}/run            // Start pipeline
GET    /api/pipeline/{id}/status         // Get pipeline status
POST   /api/pipeline/{id}/cancel         // Cancel running pipeline
GET    /api/pipeline/{id}/logs           // Get pipeline logs
GET    /api/pipeline/running             // Get all running pipelines

// Model Management
GET    /api/models/providers             // List available providers
GET    /api/models/providers/{provider}/models  // Get models for provider
GET    /api/models/ollama/models         // Get Ollama models
GET    /api/models/lmstudio/models       // Get LMStudio models
POST   /api/models/test-connection       // Test model connection

// Configuration
GET    /api/pipeline/config/models       // Get available LLM models
GET    /api/pipeline/config/retrievers   // Get available retrievers
GET    /api/settings/                    // Get user settings
POST   /api/settings/                    // Save settings

// Documentation
GET    /api/docs/                        // API documentation
GET    /api/docs/config-schema           // Configuration schema
GET    /api/docs/pipeline-stages         // Pipeline stage definitions
```

### WebSocket Events

```typescript
// WebSocket event types
interface PipelineEvent {
  type: 'progress' | 'stage_complete' | 'error' | 'complete';
  projectId: string;
  data: {
    stage: string;
    progress: number;
    message?: string;
    error?: string;
  };
}

// Subscribe to pipeline events
ws.on('pipeline:progress', (event: PipelineEvent) => {
  updateProgress(event.data);
});
```

## Configuration

### Environment Variables

```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Optional
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_COSTORM=true
NEXT_PUBLIC_MAX_FILE_SIZE=10485760
NEXT_PUBLIC_ALLOWED_FILE_TYPES=.txt,.pdf,.md
NEXT_PUBLIC_SESSION_TIMEOUT=3600000
```

### Feature Flags

```typescript
// config/features.ts
export const features = {
  coStorm: process.env.NEXT_PUBLIC_ENABLE_COSTORM === 'true',
  analytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  export: {
    pdf: true,
    docx: true,
    markdown: true,
    html: true
  },
  collaboration: {
    enabled: false,
    maxUsers: 10
  }
};
```

### API Configuration

```typescript
// config/api.ts
export const apiConfig = {
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  maxConcurrent: 5,

  endpoints: {
    base: process.env.NEXT_PUBLIC_API_URL,
    ws: process.env.NEXT_PUBLIC_WS_URL
  },

  headers: {
    'Content-Type': 'application/json',
    'X-Client-Version': '0.1.0'
  }
};
```

## Testing

### Unit Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test ProjectCard.test.tsx

# Run in watch mode
npm run test:watch
```

### E2E Tests

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Run specific browser
npm run test:e2e -- --project=chromium
```

### Test Structure

```typescript
// Example test file
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from './ProjectCard';

describe('ProjectCard', () => {
  it('should render project title', () => {
    const project = {
      id: '1',
      title: 'Test Project',
      status: 'draft'
    };

    render(<ProjectCard project={project} />);
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });

  it('should call onSelect when clicked', () => {
    const onSelect = jest.fn();
    const project = { id: '1', title: 'Test' };

    render(<ProjectCard project={project} onSelect={onSelect} />);
    fireEvent.click(screen.getByRole('article'));

    expect(onSelect).toHaveBeenCalledWith('1');
  });
});
```

## Deployment

### Production Build

```bash
# Backend production setup
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend production build
cd frontend/storm-ui
npm install
npm run build
npm start  # Runs on port 3000
```

### Docker Deployment

```bash
# Build Docker image
docker build -t storm-ui:latest .

# Run container
docker run -p 3000:3000 storm-ui:latest
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Environment-Specific Configuration

```javascript
// next.config.js
module.exports = {
  env: {
    API_URL: process.env.VERCEL_ENV === 'production'
      ? 'https://api.storm.example.com'
      : 'http://localhost:8000'
  }
};
```

### Performance Optimization

1. **Image Optimization**
   - Use Next.js Image component
   - Implement lazy loading
   - Optimize image formats (WebP, AVIF)

2. **Code Splitting**
   - Dynamic imports for large components
   - Route-based code splitting
   - Lazy load heavy dependencies

3. **Caching Strategy**
   - Implement SWR for data fetching
   - Use React Query for server state
   - Configure proper cache headers

4. **Bundle Optimization**
   - Tree shaking unused code
   - Minimize and compress assets
   - Use CDN for static assets

## Contributing

We welcome contributions! Please see our [Contributing Guide](../../CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Review Process

1. All code must pass CI checks
2. Requires at least one approval
3. Must include tests for new features
4. Documentation updates required for API changes

## Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Build errors**
   ```bash
   rm -rf .next
   npm run build
   ```

3. **API connection issues**
   - Check backend is running on correct port
   - Verify CORS configuration
   - Check network tab for error details

4. **Performance issues**
   - Enable production mode
   - Check for memory leaks
   - Profile with React DevTools

For more troubleshooting tips, see [INSTALL.md](./INSTALL.md#troubleshooting).

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Acknowledgments

- Stanford OVAL team for the original STORM research
- The open-source community for amazing tools and libraries
- Contributors and testers who helped improve the project

## Support

- **Documentation**: [STORM Documentation](https://github.com/stanford-oval/storm)
- **Issues**: [GitHub Issues](https://github.com/zettai-seigi/storm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/zettai-seigi/storm/discussions)

## Implementation Status

### ✅ Completed Features
- **Backend API**: Full FastAPI implementation with file-based storage
- **Frontend Application**: Complete Next.js 14 app with all pages
- **Project Management**: CRUD operations for projects
- **Pipeline Integration**: Working STORM pipeline execution
- **Configuration System**: API key and model configuration
- **UI Components**: Complete component library (100+ components)
- **State Management**: Zustand stores for all features
- **Real-time Updates**: WebSocket support for pipeline progress
- **File Storage**: Working file-based project storage
- **Authentication**: API key management

### 🚧 In Progress
- **Co-STORM**: Collaborative features being refined
- **Export System**: Additional export formats
- **Analytics**: Enhanced metrics and reporting

### 📋 Planned Features
- **Batch Processing**: Process multiple articles
- **Version Control**: Article versioning system
- **Team Collaboration**: Multi-user support
- **Advanced Search**: Full-text search across projects
- **Plugin System**: Extensibility framework

### Future Considerations
- GraphQL API support
- Offline mode with service workers
- Browser extension
- Native mobile apps

---

Built with ❤️ by the STORM community


