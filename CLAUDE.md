# Claude Code Collaboration Guide

## Project Context

We're implementing **ASI-ARCH** - the first autonomous AI research system that can discover novel neural architectures. Think of it as "AI for AI research" where the system continuously evolves better architectures through systematic experimentation.

This is inspired by a breakthrough paper showing AI autonomously discovering 106 novel neural architectures over 20,000 GPU hours. We're building this on Pixeltable to make it more powerful and collaborative.

## What You're Joining

**Current Status**: We have the conceptual framework and system design complete. We're now in the implementation phase, starting with setting up the core infrastructure and getting the basic research loop working.

**Your Role**: Help with filesystem operations, package management, code implementation, and debugging. You have the hands-on access needed to get things building and running.

## Critical Technical Constraints

### Package Management
- **MUST USE**: `uv` for all Python dependencies
- **DO NOT**: Mix pip, conda, or other package managers
- **WHY**: Keeps dependencies clean and consistent across the team

### Platform
- **Target**: macOS (primary development environment)
- **Considerations**: File paths, system dependencies, etc.

### Database/Infrastructure
- **MUST USE**: Pixeltable (this is non-negotiable)
- **DO NOT**: Fall back to MongoDB or traditional databases
- **WHY**: Pixeltable provides unique AI-native features we need

## Pixeltable API Important Notes

**This is NOT a traditional database!** Key differences you need to know:

### Core Concepts
```python
# Traditional DB thinking (DON'T do this)
cursor.execute("SELECT * FROM experiments WHERE status='complete'")

# Pixeltable thinking (DO this)  
table.select(table.column_name).where(table.status == 'complete')

# Computed columns (the magic part)
@pixeltable.udf
def researcher_agent(historical_data: JSON) -> dict:
    # AI agent logic here
    return {"motivation": "...", "code": "..."}

# This becomes a computed column that auto-executes
experiments.add_column(researcher_output=researcher_agent(experiments.historical))
```

### Key Features We're Using
- **Computed Columns**: Functions that auto-execute when data changes
- **UDFs**: Python functions that become database columns  
- **Multimodal**: Images, videos, documents are native data types
- **Snapshots**: Complete state preservation for reproducibility

### API Reference
Since Pixeltable is quite different, you should reference:
- Pixeltable GitHub repo for latest API
- Official documentation for examples
- The API patterns are more like: `table.select().where().limit()` 

## Current Implementation Focus

### Phase 1 MVP Components

1. **Core Tables Setup**
   - `experiments` table with computed columns for AI agents
   - `cognition_base` for research paper insights  
   - `architecture_lineage` for tracking evolution

2. **AI Agent UDFs**
   - Researcher agent (generates hypotheses)
   - Engineer agent (implements & trains)
   - Analyst agent (extracts insights)

3. **Training Pipeline Integration**
   - PyTorch model training
   - Evaluation on standard benchmarks
   - Results capture and storage

4. **Web Interface**
   - Live experiment monitoring
   - Evolution tree visualization
   - Research progress tracking

### Immediate Tasks
- [ ] Get Pixeltable installed and working with uv
- [ ] Set up basic project structure
- [ ] Create first table schemas
- [ ] Implement simple UDF examples
- [ ] Test basic workflow end-to-end

## File Structure
```
asi-arch/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── training/        # Model training pipeline  
│   ├── database/        # Pixeltable schema & operations
│   ├── evaluation/      # Benchmark evaluation
│   └── web/            # Dashboard interface
├── tests/
├── docs/
├── pyproject.toml      # uv configuration
└── README.md
```

## Key Context from Previous Work

**What We Know Works**: The conceptual framework is solid. The original ASI-ARCH paper proved this approach works for discovering novel architectures.

**Our Innovation**: Using Pixeltable instead of MongoDB gives us:
- Automatic AI workflow orchestration  
- Native multimodal support
- Built-in versioning and snapshots
- Declarative vs imperative programming

**Success Criteria**: System autonomously discovers neural architectures that outperform human-designed baselines, with complete reproducibility via snapshots.

## Collaboration Style

- **Be Direct**: Point out technical issues, suggest better approaches
- **Ask Questions**: Pixeltable is specialized, so clarify when unsure
- **Stay Focused**: We're building a research system, not optimizing for production scale yet
- **Document**: Good comments help since this is complex multi-agent orchestration

## Getting Started Checklist

1. Verify `uv` is working in the project
2. Get Pixeltable installed via uv
3. Create basic table and test connection
4. Implement simple UDF (like a "hello world" computed column)
5. Set up basic project structure per the file organization above

Let's build something amazing! The goal is autonomous AI research - this could genuinely accelerate AI progress by orders of magnitude.