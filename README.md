# Mervellous

Framework multi-agent polyvalent pour [OpenClaw](https://openclaw.ai/) — orchestration hub-and-spoke avec 7 agents specialises.

## Architecture

```
         User (Telegram / Discord / Slack / WhatsApp / CLI)
                            |
                         [Merv]
                      Orchestrator
                     /   |   |   \
              [Linus] [Finch] [Otto] [Iris] [Nova] [Forge]
              Coder  Research Autom. Writer Analyst DevOps
```

**Merv** recoit toutes les requetes, analyse, decoupe en sous-taches, et delegue aux agents specialises via `sessions_spawn`. Chaque agent tourne dans un sandbox Docker isole.

## Agents

| Agent | Role | Modele | Specialite |
|-------|------|--------|------------|
| **Merv** | Orchestrateur | Claude Opus | Routing, coordination, synthese |
| **Linus** | Developpeur Senior | Claude Opus | Code, debug, tests, architecture |
| **Finch** | Chercheur | Claude Sonnet | Recherche web, analyse, veille |
| **Otto** | Automatisation | Claude Sonnet | Scripts, cron, pipelines |
| **Iris** | Redactrice | Claude Sonnet | Docs, articles, emails, traductions |
| **Nova** | Analyste | Claude Sonnet | Data, SQL, visualisations, KPIs |
| **Forge** | DevOps | Claude Sonnet | Docker, CI/CD, infra, deploiement |

## Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/numalias/Mervellous.git
cd Mervellous

# 2. Lancer le setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Ajouter votre cle API
openclaw auth add anthropic

# 4. Valider la config
openclaw doctor --fix

# 5. Demarrer
openclaw gateway start
```

## Structure du projet

```
Mervellous/
├── openclaw.example.json       # Config multi-agent complete
├── .env.example                # Variables d'environnement
├── .gitignore
├── scripts/
│   ├── setup.sh                # Installation automatique
│   └── add-agent.sh            # Ajouter un nouvel agent
├── skills/
│   └── shared/                 # Skills partages entre agents
├── workspace-merv/             # Orchestrateur
│   ├── SOUL.md                 # Personnalite + routing
│   ├── AGENTS.md               # Registre des agents
│   ├── TOOLS.md                # Reference outils
│   ├── IDENTITY.md             # Affichage
│   ├── USER.md                 # Profil utilisateur
│   └── HEARTBEAT.md            # Taches recurrentes
├── workspace-linus/            # Developpeur
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-finch/            # Chercheur
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-otto/             # Automatisation
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-iris/             # Redactrice
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-nova/             # Analyste
│   ├── SOUL.md
│   └── AGENTS.md
└── workspace-forge/            # DevOps
    ├── SOUL.md
    └── AGENTS.md
```

## Ajouter un agent

```bash
./scripts/add-agent.sh <id> <nom> <description>

# Exemple:
./scripts/add-agent.sh atlas "Atlas -- Project Manager" "project management and planning"
```

Puis ajouter l'agent dans `openclaw.example.json` et relancer `openclaw doctor --fix`.

## Canaux supportes

- Telegram
- Discord
- Slack
- WhatsApp
- CLI (`openclaw chat`)

Activer un canal dans `openclaw.json` > `channels` et configurer les tokens.

## Personnalisation

Chaque agent est entierement configurable via ses fichiers Markdown :

- **SOUL.md** — Personnalite, principes, format de reponse
- **AGENTS.md** — Instructions en tant que sub-agent
- **TOOLS.md** — Reference des outils disponibles (orchestrateur)
- **USER.md** — Preferences utilisateur (orchestrateur)

## Sources et references

- [OpenClaw Documentation](https://docs.openclaw.ai/)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)
- [OpenClaw Advanced Config (TheSethRose)](https://github.com/TheSethRose/OpenClaw-Advanced-Config)

## Licence

Open source — MIT
