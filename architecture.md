# ASI-ARCH Implementation Architecture

## Project Overview

We are implementing **ASI-ARCH** - an autonomous AI research system that can discover novel neural architectures through systematic experimentation. This is inspired by the breakthrough paper showing the first "AI for AI research" system that autonomously discovered 106 novel neural architectures over 20,000 GPU hours.

## Core Concept: AI Self-Evolution for Research

ASI-ARCH operates as a closed-loop system where AI agents autonomously:

1. **Research**: Generate novel architecture hypotheses based on literature and experimental history
2. **Engineer**: Implement and train architectures in real environments  
3. **Analyze**: Extract insights and learnings to inform future experiments
4. **Evolve**: Use evolutionary algorithms with LLM intelligence to explore design space

## System Architecture

### Multi-Agent Framework

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RESEARCHER    │───▶│    ENGINEER     │───▶│    ANALYST      │
│                 │    │                 │    │                 │
│ • Hypothesis    │    │ • Code Gen      │    │ • Performance   │
│ • Motivation    │    │ • Training      │    │ • Insights      │
│ • Design        │    │ • Validation    │    │ • Analysis      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                                      │
         │                                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIXELTABLE DATABASE                         │
│                                                                 │
│ • Experiments Table (with computed columns for AI agents)      │
│ • Architecture Evolution Tree                                  │
│ • Cognition Base (research paper insights)                     │
│ • Complete experimental lineage & snapshots                    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Innovation: Pixeltable as AI Research Platform

Unlike the original MongoDB approach, we use **Pixeltable** which provides:

- **Declarative AI Workflows**: AI agents ARE computed columns → automatic coordination
- **Native Multimodal Support**: Handle code, metrics, visualizations, research papers seamlessly  
- **Built-in Versioning**: Complete experimental lineage automatically maintained
- **Snapshot System**: Instant reproducibility of any research state

### Core Tables

1. **experiments**: Each row is an architecture experiment with computed columns for AI operations
2. **cognition_base**: Research paper insights extracted for retrieval
3. **architecture_lineage**: Parent-child relationships and evolution tracking

## Implementation Strategy

### Phase 1: Core MVP
- Basic experiments table with AI agent computed columns
- Simple Researcher → Engineer → Analyst workflow  
- Text + vision training pipeline with snapshots
- Web dashboard for monitoring

### Phase 2: Advanced Features
- Full multimedia research pipeline
- Collaborative snapshot sharing
- Meta-research analytics
- Cross-modal architecture discovery

## Technical Requirements

### Development Environment
- **Package Manager**: uv (stick to this for consistency)
- **Platform**: macOS (primary development target)
- **Infrastructure**: Pixeltable (NOT MongoDB)

### Key Dependencies
- Pixeltable for data/workflow management
- PyTorch for model training
- Transformers for base models
- Various ML evaluation libraries

## Pixeltable vs Traditional Database

**Critical Difference**: Pixeltable is NOT a traditional database. Key distinctions:

- **Computed Columns**: Functions that automatically execute when data changes
- **UDF (User Defined Functions)**: Python functions that become computed columns
- **Multimodal Native**: Images, videos, documents are first-class data types
- **Declarative**: Define relationships, let Pixeltable handle execution

Refer to Pixeltable documentation/repo for API details - it's quite different from SQL/MongoDB patterns.

## Research Workflow

1. **Evolution Loop**: Evolutionary algorithm selects top-50 architectures as candidates
2. **LLM Intelligence**: Rather than random mutations, use LLM agents for intelligent hypothesis generation
3. **Real Training**: Actually train and evaluate architectures (not just theoretical)
4. **Insight Extraction**: Learn from successes and failures to improve future designs
5. **Snapshot Preservation**: Capture breakthrough moments for instant reproducibility

## Success Metrics

The system discovers novel architectures that outperform human-designed baselines across:
- Training efficiency (loss curves)
- Reasoning tasks (ARC, HellaSwag, PIQA)
- Language understanding (BoolQ, LAMBADA)
- Specialized capabilities (various benchmarks)

## Expected Outcomes

- Novel neural architectures with state-of-the-art performance
- Complete research trails showing how breakthroughs emerged
- Snapshot-based instant reproducibility of 20K+ GPU hours of work
- Accelerated AI research through computational scaling