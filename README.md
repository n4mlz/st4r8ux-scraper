# st4r8ux Job Scraper

Minimal job scraper for Discord notifications.

## Setup

1. Copy environment file:

```bash
cp .env.example .env
```

2. Edit `.env` with your Discord webhook URL

3. Run:

```bash
docker compose up
```

## Usage

- Run once: `python main.py`
- Reset data: `rm data/data.json`
- Run with Docker: `docker compose up`
- Run with cron: `docker compose run --rm scraper`

### Cron Setup

Add to crontab for every 30 minutes:

```bash
*/30 * * * * cd /path/to/st4r8ux-scraper && docker compose up -d
```
