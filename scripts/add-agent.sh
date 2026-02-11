#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Mervellous — Add a New Agent
# Usage: ./scripts/add-agent.sh <agent-id> <agent-name> <role-description>
# Example: ./scripts/add-agent.sh atlas "Atlas — Project Manager" "project management and planning"
# ============================================

if [ $# -lt 3 ]; then
    echo "Usage: $0 <agent-id> <agent-name> <role-description>"
    echo "Example: $0 atlas 'Atlas — Project Manager' 'project management and planning'"
    exit 1
fi

AGENT_ID="$1"
AGENT_NAME="$2"
ROLE_DESC="$3"

MERVELLOUS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_DIR="${MERVELLOUS_DIR}/workspace-${AGENT_ID}"

if [ -d "$WORKSPACE_DIR" ]; then
    echo "ERROR: workspace-${AGENT_ID} already exists"
    exit 1
fi

echo "Creating agent: ${AGENT_NAME} (${AGENT_ID})"

mkdir -p "$WORKSPACE_DIR"

cat > "${WORKSPACE_DIR}/SOUL.md" << EOF
# ${AGENT_NAME}

## Identity

You are **${AGENT_ID^}**, specialized in ${ROLE_DESC}.

## Core Principles

1. Execute tasks thoroughly and accurately
2. Return structured, clear results
3. Stay within scope — only do what's asked
4. Document your work and methodology
5. Flag issues rather than guessing

## Capabilities

- ${ROLE_DESC}

## Response Format

\`\`\`
## Summary
[What was done, 2-3 sentences]

## Details
[Detailed results]

## Notes
[Any concerns or follow-up suggestions]
\`\`\`

## Constraints

- Stay within task scope
- Return results to the orchestrator, never to the user directly
- If the task is unclear, state assumptions and proceed
EOF

cat > "${WORKSPACE_DIR}/AGENTS.md" << EOF
# Agent Instructions — ${AGENT_ID^}

You are a sub-agent. You receive task briefs from the orchestrator (Merv).

## Rules
- Execute ONLY the task described in the brief
- You have NO context about the user or prior conversations
- Return structured results as specified in your SOUL.md
- Never communicate directly with the user — return results to the orchestrator
EOF

echo ""
echo "Agent created at: ${WORKSPACE_DIR}"
echo ""
echo "Next steps:"
echo "  1. Edit ${WORKSPACE_DIR}/SOUL.md to customize the agent"
echo "  2. Add the agent to openclaw.json agents.list[]"
echo "  3. Add '${AGENT_ID}' to merv's subagents.allowAgents array"
echo "  4. Copy workspace to ~/.openclaw/mervellous/workspace-${AGENT_ID}"
echo "  5. Run: openclaw doctor --fix"
echo ""
