# Media News Digest 🎬

> Automated media & entertainment industry news digest — 76 total sources (75 enabled), 4-source pipeline, one chat message to install.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 💬 Install in One Message

Tell your [OpenClaw](https://openclaw.ai) AI assistant:

> **"Install media-news-digest and send a daily digest to #news-media every morning at 7am"**

That's it. Your bot handles installation, configuration, scheduling, and delivery — all through conversation.

## 📊 What You Get

A quality-scored, deduplicated entertainment industry digest built from **76 total sources (75 enabled)**:

| Layer | Sources | What |
|-------|---------|------|
| 📡 RSS | RSS 46 enabled feeds | THR, Deadline, Variety, IndieWire, The Wrap, Collider, YouTube RSS mirrors, and more |
| 🐦 Twitter/X | Twitter/X 18 KOLs | @THR, @DEADLINE, @Variety, @BoxOfficeMojo, @MattBelloni, @A24, and more |
| 🗣️ Reddit | Reddit 11 subreddits | r/movies, r/boxoffice, r/television, r/Oscars, r/anime, and more |
| 🔍 Web Search | 9 topic sections | Brave Search / Tavily with freshness filters |

### Pipeline

```text
RSS + Twitter/X + Reddit + Web Search
              ↓
      run-pipeline.py (parallel)
              ↓
Quality scoring → content topic classification → deduplication → domain limits
              ↓
      Discord / Email / PDF output
```

## 🎯 9 topic sections

| # | Section | Covers |
|---|---------|--------|
| 🎟️ | Box Office / 票房 | NA/global box office, opening weekends |
| 💰 | Deals & Business / 行业交易 | M&A, rights, talent deals, restructuring |
| 🇨🇳 | China / 中国影视 | Mainland China box office, Chinese films, Chinese streaming |
| 🎬 | Production / 制作动态 | New projects, casting, filming updates |
| 🎞️ | Upcoming Releases / 北美近期上映 | Theater openings, release dates, trailers |
| 📺 | Streaming / 流媒体 | Netflix, Disney+, Apple TV+, HBO/Max, viewership |
| 🏆 | Awards / 颁奖季 | Oscars, Golden Globes, Emmys, BAFTAs |
| 🎪 | Film Festivals / 电影节 | Cannes, Venice, TIFF, Sundance, Berlin |
| ⭐ | Reviews & Buzz / 影评口碑 | Critical reception, RT/Metacritic scores |

## ⚙️ Configuration

- `config/defaults/sources.json` — 76 total sources, 75 enabled by default
- `config/defaults/topics.json` — 9 topic sections with search and classification hints
- User overrides live in `workspace/config/` as `media-news-digest-sources.json` and `media-news-digest-topics.json`

## 🔧 Environment

```bash
export X_BEARER_TOKEN="***"      # Twitter API (recommended)
export TWITTERAPI_IO_KEY="..."   # twitterapi.io fallback backend
export BRAVE_API_KEY="***"       # Web search (optional)
export BRAVE_API_KEYS="k1,k2"    # Preferred: multiple Brave keys with rotation
export TAVILY_API_KEY="***"      # Tavily fallback backend
```

## 📦 Dependencies

```bash
pip install -r requirements.txt
```

Python 3.8+ is required. `feedparser` and `jsonschema` are listed in `requirements.txt`; RSS parsing and config validation are best run with them installed.

## 🚀 Quick Start

```bash
python3 scripts/run-pipeline.py   --defaults config/defaults   --hours 48 --freshness pd   --output /tmp/md-merged.json --verbose --force
```

## 📂 Repository

**GitHub**: [github.com/draco-agent/media-news-digest](https://github.com/draco-agent/media-news-digest)

## License

MIT
