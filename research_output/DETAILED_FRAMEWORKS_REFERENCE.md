# Detailed Frameworks Reference

> **Source**: Direct web fetches from official repositories
> **Purpose**: Complete implementation details for Skills Fabric

---

## 1. BMAD Method (Complete Reference)

**Repository**: github.com/bmad-code-org/BMAD-METHOD (27.8k stars)

### Core Architecture: BMad Core (C.O.R.E.)

**C**ollaboration **O**ptimized **R**eflection **E**ngine - universal framework for human-AI collaboration.

### The Four Phases

| Phase | Purpose |
|-------|---------|
| 📊 **Analysis** | Brainstorming, research, exploration (optional) |
| 📝 **Planning** | PRDs, tech specs, design documents |
| 🏗️ **Solutioning** | Architecture, UX, technical approach |
| ⚡ **Implementation** | Story-driven development with validation |

### 12 Core Agents

| Development | Architecture | Product | Leadership |
|-------------|--------------|---------|------------|
| Developer | Architect | PM | Scrum Master |
| UX Designer | Test Architect | Analyst | BMad Master |
| | | Tech Writer | |

### Key Commands

```bash
# Initialize and analyze project
*workflow-init

# Install
npx bmad-method@alpha install
```

### Scale-Adaptive Intelligence

| Scope | Track | Time |
|-------|-------|------|
| Bug fixes/small features | Quick Flow | < 5 min |
| Products/platforms | BMad Method | < 15 min |
| Enterprise/compliance | Full governance | < 30 min |

### Key Features
- **34 workflows** across 4 phases (50+ total guided workflows)
- **Document sharding** reduces token usage by 90%
- **Web bundles** for ChatGPT, Claude Projects, Gemini Gems
- **Update-safe customization** - user configs persist through updates

---

## 2. Spec-Kit (Complete Reference)

**Repository**: github.com/github/spec-kit

### Core Philosophy

Spec-Driven Development: "Specifications become executable, directly generating working implementations."

### Slash Commands

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Establish project governing principles |
| `/speckit.specify` | Define requirements (what & why) |
| `/speckit.plan` | Create technical implementation strategy |
| `/speckit.tasks` | Generate actionable task lists |
| `/speckit.implement` | Execute all tasks to build features |
| `/speckit.clarify` | Resolve underspecified areas |
| `/speckit.analyze` | Cross-artifact consistency validation |
| `/speckit.checklist` | Generate quality validation checklists |

### Installation

```bash
# Persistent (recommended)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# One-time
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>

# Options
--ai [claude|gemini|copilot|cursor-agent|qwen|windsurf|etc]
--force  # Skip confirmation
--no-git # Skip git init
```

### Supported AI Agents (17+)

Claude Code, Gemini, GitHub Copilot, Cursor, Qwen, Windsurf, Qoder CLI, Amazon Q Developer, Amp, CodeBuddy, IBM Bob, Jules, and more.

### Development Phases

1. **0-to-1 (Greenfield)** - Generate from scratch
2. **Creative Exploration** - Parallel implementations
3. **Iterative Enhancement (Brownfield)** - Add to existing systems

---

## 3. Ralph's Loop (Complete Reference)

**Repository**: github.com/mikeyobrien/ralph-orchestrator

### Core Loop Structure

```
1. Read prompt from PROMPT.md or inline text
2. Execute AI agent with current context
3. Check for completion markers in output
4. Loop back if not complete and limits allow
5. Exit when completion or limits reached
```

### Configuration Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `max_iterations` | 100 | Maximum loop cycles |
| `max_runtime` | 14400s (4h) | Time limit |
| `max_tokens` | 1,000,000 | Total token budget |
| `max_cost` | $50 USD | Cost limit |
| `checkpoint_interval` | 5 | Git checkpoint frequency |

### Completion Detection

- Agent indicates completion in output
- Maximum iterations exceeded
- Runtime limit surpassed
- Cost limit reached
- Too many consecutive errors

### Git-Based Checkpointing

Each checkpoint captures:
- Current prompt state
- Agent progress markers
- Metrics and context
- Full iteration history

### ACP Agent Scratchpad

Agents persist context via `.agent/scratchpad.md`:
- Progress from previous iterations
- Decisions and context
- Current blockers
- Remaining work items

---

## 4. Fabric Patterns (Reference)

**Repository**: github.com/danielmiessler/fabric

### Pattern System

Modular AI prompts called "Patterns" organized by real-world tasks.

### Code-Related Patterns

| Pattern | Purpose |
|---------|---------|
| `code_review` | Evaluates code quality |
| `code2context` | Extracts code for analysis |
| `extract_wisdom` | Extracts key insights |
| `create_summary` | Generates summaries |

### Pattern Configuration

```bash
# Environment variable for per-pattern model
FABRIC_MODEL_PATTERN_NAME=vendor|model

# Direct invocation via aliases
summarize  # instead of: fabric --pattern summarize
```

### Categories
- Content extraction (YouTube, podcasts)
- Writing assistance
- Academic analysis
- Code-related tasks
- Technical documentation
- Visual knowledge representation

---

## 5. VoltAgent Subagents (100+ Agents)

**Repository**: github.com/VoltAgent/awesome-claude-code-subagents (7.1k stars)

### Complete Agent Catalog

#### 01. Core Development (11 agents)
API Designer, Backend Developer, Electron Pro, Frontend Developer, Fullstack Developer, GraphQL Architect, Microservices Architect, Mobile Developer, UI Designer, WebSocket Engineer, WordPress Master

#### 02. Language Specialists (26 agents)
TypeScript Pro, SQL Pro, Swift Expert, Vue Expert, Angular Architect, C++ Pro, C# Developer, Django Developer, .NET Core Expert, .NET Framework 4.8 Expert, Elixir Expert, Flutter Expert, Go Pro, Java Architect, JavaScript Pro, PowerShell 5.1 Expert, PowerShell 7 Expert, Kotlin Specialist, Laravel Specialist, Next.js Developer, PHP Pro, Python Pro, Rails Expert, React Specialist, Rust Engineer, Spring Boot Engineer

#### 03. Infrastructure (14 agents)
Azure Infra Engineer, Cloud Architect, Database Administrator, Deployment Engineer, DevOps Engineer, DevOps Incident Responder, Incident Responder, Kubernetes Specialist, Network Engineer, Platform Engineer, Security Engineer, SRE Engineer, Terraform Engineer, Windows Infra Admin

#### 04. Quality & Security (12 agents)
Accessibility Tester, Architect Reviewer, Chaos Engineer, Code Reviewer, Compliance Auditor, Debugger, Error Detective, Penetration Tester, Performance Engineer, QA Expert, Security Auditor, Test Automator

#### 05. Data & AI (12 agents)
AI Engineer, Data Analyst, Data Engineer, Data Scientist, Database Optimizer, LLM Architect, Machine Learning Engineer, ML Engineer, MLOps Engineer, NLP Engineer, PostgreSQL Pro, Prompt Engineer

#### 06. Developer Experience (13 agents)
Build Engineer, CLI Developer, Dependency Manager, Documentation Engineer, DX Optimizer, Git Workflow Manager, Legacy Modernizer, MCP Developer, PowerShell UI Architect, PowerShell Module Architect, Refactoring Specialist, Slack Expert, Tooling Engineer

#### 07. Specialized Domains (12 agents)
API Documenter, Blockchain Developer, Embedded Systems, FinTech Engineer, Game Developer, IoT Engineer, M365 Admin, Mobile App Developer, Payment Integration, Quant Analyst, Risk Manager, SEO Specialist

#### 08. Business & Product (10 agents)
Business Analyst, Content Marketer, Customer Success Manager, Legal Advisor, Product Manager, Project Manager, Sales Engineer, Scrum Master, Technical Writer, UX Researcher

#### 09. Meta & Orchestration (9 agents)
Agent Organizer, Context Manager, Error Coordinator, Knowledge Synthesizer, Multi-Agent Coordinator, Performance Monitor, Pied Piper, Task Distributor, Workflow Orchestrator

#### 10. Research & Analysis (6 agents)
Research Analyst, Search Specialist, Trend Analyst, Competitive Analyst, Market Researcher, Data Researcher

---

## 6. Anthropic Cookbook Patterns

**Repository**: github.com/anthropics/anthropic-cookbook (30.6k stars)

### Basic Building Blocks

| Pattern | Description |
|---------|-------------|
| **Prompt Chaining** | Sequential prompts, output flows to next |
| **Routing** | Direct tasks to appropriate handlers |
| **Multi-LLM Parallelization** | Run multiple models simultaneously |

### Advanced Workflows

| Pattern | Description |
|---------|-------------|
| **Orchestrator-Subagents** | Coordinator delegates to specialists |
| **Evaluator-Optimizer** | Iterative improvement through assessment |

### Available Notebooks

1. Basic Workflows
2. Evaluator-Optimizer Workflow
3. Orchestrator-Workers Workflow

### Cookbook Categories

- `tool_use` - Tool integration examples
- `multimodal` - Vision and image processing
- `capabilities` - Classification, RAG, summarization
- `third_party` - Vector DBs, Wikipedia, web scraping
- `finetuning` - Model customization
- `observability` - Monitoring and tracing
- `coding` - Code generation examples
- `extended_thinking` - Advanced reasoning
- `skills` - Agent skills

---

## 7. Claude Resources Summary

### Official SDKs

| SDK | Stars | Status |
|-----|-------|--------|
| anthropic-sdk-python | 2.6k | Stable |
| anthropic-sdk-typescript | 1.5k | Stable |
| claude-agent-sdk-python | 3.9k | Stable |
| claude-agent-sdk-typescript | 554 | Stable |
| anthropic-cookbook | 30.6k | Reference |
| claude-quickstarts | 13.3k | Examples |

### Community Resources

| Resource | Stars | Purpose |
|----------|-------|---------|
| awesome-claude-code | 19.5k | Commands, workflows, CLAUDE.md |
| awesome-claude-skills | 4.2k | Skills customization |
| awesome-mcp-servers | 78.2k | MCP servers |
| awesome-claude-code-subagents | 7.1k | 100+ specialized agents |

### Claude 4.5 Family (2025)

| Model | Best For |
|-------|----------|
| **Opus 4.5** | Coding, agents, computer use, complex enterprise |
| **Sonnet 4.5** | Balance of intelligence, speed, cost |
| **Haiku 4.5** | Fastest, most cost-effective |

---

## 8. Integration with Skills Fabric

### Recommended Adoption

| Framework | Use In Our Skill |
|-----------|------------------|
| **BMAD** | Structure internal agents (QA, Dev, Architect) |
| **Spec-Kit** | `/specify` for feature planning |
| **Ralph's Loop** | Iterate until documentation complete |
| **Fabric** | `extract_wisdom` for code insights |
| **VoltAgent** | Documentation Engineer, Code Reviewer subagents |
| **Cookbook** | Orchestrator-Subagents pattern |

### Implementation Pattern

```python
class SkillsFabric:
    """Integration of all frameworks."""

    def __init__(self):
        # BMAD-style agents
        self.qa_agent = QAAgent()
        self.dev_agent = DevAgent()
        self.architect = ArchitectAgent()

        # Ralph's Loop config
        self.loop_config = {
            "max_iterations": 50,
            "max_cost": 10.0,
            "checkpoint_interval": 5,
        }

        # VoltAgent subagents
        self.subagents = {
            "doc_engineer": DocumentationEngineer(),
            "code_reviewer": CodeReviewer(),
        }

    async def generate_skill(self, library: str, level: int):
        # Spec-Kit style specification
        spec = await self._specify(library, level)

        # Ralph's Loop execution
        while not self._is_complete():
            result = await self._iterate(spec)
            if self._should_checkpoint():
                await self._checkpoint()

        # BMAD QA review
        return await self.qa_agent.review(result)
```

---

## Quick Reference

### Key Numbers

- **BMAD**: 12 agents, 34 workflows, 4 phases
- **Spec-Kit**: 7 commands, 17+ AI agents
- **Ralph's Loop**: 5 config params, git checkpoints
- **VoltAgent**: 100+ subagents, 10 categories
- **Cookbook**: 30.6k stars, 475 commits

### Essential Commands

```bash
# BMAD
npx bmad-method@alpha install
*workflow-init

# Spec-Kit
specify init <project>
/speckit.specify
/speckit.plan
/speckit.implement

# Fabric
fabric --pattern extract_wisdom
fabric --pattern code_review
```
