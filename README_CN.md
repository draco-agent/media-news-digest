# Media News Digest 🎬

> 自动化影视娱乐资讯汇总 — 76 total sources（75 enabled），4 源并行管道，一句话安装。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 💬 一句话安装

跟你的 [OpenClaw](https://openclaw.ai) AI 助手说：

> **"安装 media-news-digest，每天早上 7 点发影视日报到 #news-media 频道"**

Bot 会自动安装、配置、定时、推送。

## 📊 你会得到什么

基于 **76 total sources（75 enabled）** 的质量评分、内容分类、去重影视行业日报：

| 层级 | 数量 | 内容 |
|------|------|------|
| 📡 RSS | RSS 46 enabled feeds | THR、Deadline、Variety、IndieWire、The Wrap、Collider、YouTube RSS mirrors 等 |
| 🐦 Twitter/X | Twitter/X 18 KOLs | @THR、@DEADLINE、@Variety、@BoxOfficeMojo、@MattBelloni、@A24 等 |
| 🗣️ Reddit | Reddit 11 subreddits | r/movies、r/boxoffice、r/television、r/Oscars、r/anime 等 |
| 🔍 Web 搜索 | 9 topic sections | Brave Search / Tavily + 时效过滤 |

### 数据管道

```text
RSS + Twitter/X + Reddit + Web Search
              ↓
      run-pipeline.py（并行）
              ↓
质量评分 → 内容主题分类 → 去重 → 域名限额
              ↓
      Discord / 邮件 / PDF 输出
```

## 🎯 9 topic sections

| # | 板块 | 覆盖内容 |
|---|------|----------|
| 🎟️ | Box Office / 票房 | 北美/全球票房、首周末数据 |
| 💰 | Deals & Business / 行业交易 | 并购、版权交易、人才签约、重组裁员 |
| 🇨🇳 | China / 中国影视 | 中国内地票房、华语电影、中国流媒体 |
| 🎬 | Production / 制作动态 | 新项目、选角、拍摄进展 |
| 🎞️ | Upcoming Releases / 北美近期上映 | 院线上映、定档、预告片 |
| 📺 | Streaming / 流媒体 | Netflix、Disney+、Apple TV+、HBO/Max、收视数据 |
| 🏆 | Awards / 颁奖季 | 奥斯卡、金球奖、艾美奖、BAFTA |
| 🎪 | Film Festivals / 电影节 | 戛纳、威尼斯、多伦多、圣丹斯、柏林 |
| ⭐ | Reviews & Buzz / 影评口碑 | 专业评价、RT/Metacritic 评分 |

## ⚙️ 配置

- `config/defaults/sources.json` — 76 total sources，默认 75 enabled
- `config/defaults/topics.json` — 9 topic sections，含搜索查询和分类提示
- 用户自定义配置放 `workspace/config/`：`media-news-digest-sources.json` / `media-news-digest-topics.json`

## 🔧 环境要求

```bash
export X_BEARER_TOKEN="***"      # Twitter API（推荐）
export TWITTERAPI_IO_KEY="..."   # twitterapi.io 备选后端
export BRAVE_API_KEY="***"       # Web 搜索（可选）
export BRAVE_API_KEYS="k1,k2"    # 推荐：多 Brave key 轮换
export TAVILY_API_KEY="***"      # Tavily 备选后端
```

## 📦 依赖

```bash
pip install -r requirements.txt
```

要求 Python 3.8+。`feedparser` 与 `jsonschema` 已列在 `requirements.txt`；安装后 RSS 解析和配置校验更稳定。

## 🚀 快速开始

```bash
python3 scripts/run-pipeline.py   --defaults config/defaults   --hours 48 --freshness pd   --output /tmp/md-merged.json --verbose --force
```

## 📂 仓库地址

**GitHub**: [github.com/draco-agent/media-news-digest](https://github.com/draco-agent/media-news-digest)

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE)
