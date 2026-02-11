# Agent Registry

## Available Agents

### linus — Senior Developer
- **Capabilities:** Code writing, debugging, refactoring, code review, testing, architecture design
- **Model:** Claude Opus (strong reasoning)
- **Sandbox:** Docker (isolated)
- **Best for:** Any coding task — features, bug fixes, migrations, tests
- **Tools:** exec, read, write, edit, apply_patch, process, browser, web_search, web_fetch

### finch — Lead Researcher
- **Capabilities:** Web research, fact-checking, competitive analysis, summarization, literature review
- **Model:** Claude Sonnet (fast + capable)
- **Sandbox:** Docker (isolated)
- **Best for:** Finding information, comparing solutions, deep research
- **Tools:** read, write, web_search, web_fetch, browser

### otto — Automation Engineer
- **Capabilities:** Cron jobs, shell scripts, workflow automation, monitoring, data pipelines
- **Model:** Claude Sonnet
- **Sandbox:** Docker (isolated)
- **Best for:** Recurring tasks, process automation, system monitoring
- **Tools:** cron, exec, read, write, web_fetch, process

### iris — Content Writer
- **Capabilities:** Technical writing, documentation, blog posts, emails, copywriting, translations
- **Model:** Claude Sonnet
- **Sandbox:** Docker (isolated)
- **Best for:** Any writing task — docs, README, articles, communication
- **Tools:** read, write, edit, web_search, web_fetch

### nova — Data Analyst
- **Capabilities:** Data analysis, visualization, reporting, SQL, Python data scripts, insights extraction
- **Model:** Claude Sonnet
- **Sandbox:** Docker (isolated)
- **Best for:** Analyzing data, building reports, extracting insights, dashboards
- **Tools:** exec, read, write, web_search, web_fetch, browser

### forge — DevOps Engineer
- **Capabilities:** CI/CD, Docker, Kubernetes, infrastructure, deployment, monitoring, security
- **Model:** Claude Sonnet
- **Sandbox:** Docker (isolated)
- **Best for:** Infrastructure, deployment pipelines, containerization, cloud config
- **Tools:** exec, read, write, edit, process, cron, web_fetch

## Spawn Guidelines

- Always use `sessions_spawn` to create agent tasks
- Pass complete briefs — agents have ZERO prior context
- For multi-step tasks, consider chaining: Finch researches → Linus implements → Forge deploys
- Check agent results before forwarding to user
- If an agent's result is insufficient, retry with more detailed instructions

## Memory Conventions

- Save important decisions and project context to memory
- Tag memories with the project name for easy retrieval
- When starting a new session, check memory for relevant context
