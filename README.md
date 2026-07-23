<p align="center">
  <img src="https://avatars.githubusercontent.com/u/295873404?s=512" alt="ZNE Raid Bot" width="200" height="200">
</p>

<h1 align="center">ZNE Raid Bot</h1>

<p align="center">A powerful Discord bot built with discord.py for raiding, spamming, and managing servers.</p>

---

## Features

- **Raid** — Launch mass spam raids via interactive button panels
- **Interaction Raid** — Farm interactions automatically with smart clickers
- **Spam / File Spam** — Send custom messages or files on repeat
- **Thug** — Gay Porn spam cuz why not
- **Fake Nitro** — Deploy fake nitro giveaways and hoaxes
- **Fake Giveaway** — Host counterfeit giveaways
- **Ghost** — Ghost mention and ghost ping tools
- **DM Raid** — Direct message flooding tools
- **Ads** — Automatic advertisement posting
- **Leaderboard** — Track top raiders with LMDB-backed persistence
- **Admin Tools** — Reload cogs, set global messages, blacklist servers/users

---

## Installation

### Prerequisites

- [Python 3.10+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) — fast Python package manager

### Setup

```bash
# Clone the repo
git clone https://github.com/your-repo/ZNERaid.git
cd ZNERaid

# Create and activate a virtual environment with uv
uv venv

# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# On Linux / macOS
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Configuration

Copy the example config and fill in your values:

```bash
cp config.example.toml config.toml
```

Edit `config.toml`:

```toml
TOKEN = "your-bot-token-here"
owner_ids = [123456789012345678]

[server]
main_server = 0
verified_role_id = 0

[channels]
log_channel_id = 0

[messages]
og_msg = """your default raid message here"""

[api]
url = "your-api-url"
secret = "your-api-secret"
```

### Running

```bash
python main.py
```

---

## Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [uv](https://docs.astral.sh/uv/) — Package & venv management
- [LMDB](https://lmdb.readthedocs.io/) — High-performance leaderboard storage
- [aiohttp](https://docs.aiohttp.org/) — Async HTTP for API posting

---

## License

MIT
