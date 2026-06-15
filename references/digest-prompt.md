# Digest Prompt Template

Replace `<...>` placeholders before use. Daily defaults shown; weekly overrides in parentheses.

## Placeholders

| Placeholder | Default | Weekly Override |
|-------------|---------|----------------|
| `<MODE>` | `daily` | `weekly` |
| `<TIME_WINDOW>` | `past 1-2 days` | `past 7 days` |
| `<FRESHNESS>` | `pd` | `pw` |
| `<RSS_HOURS>` | `48` | `168` |
| `<ITEMS_PER_SECTION>` | `3-5` | `5-8` |
| `<BLOG_PICKS_COUNT>` | `2-3` | `3-5` |
| `<EXTRA_SECTIONS>` | *(none)* | `📊 Weekly Trend Summary` |
| `<SUBJECT>` | `Daily Media Digest - YYYY-MM-DD - 🎬 每日影视日报` | `Weekly Media Digest - YYYY-MM-DD - 🎬 每周影视周报` |
| `<WORKSPACE>` | Your workspace path | |
| `<SKILL_DIR>` | Installed skill directory | |
| `<DISCORD_CHANNEL_ID>` | Target channel ID | |
| `<EMAIL>` | *(optional)* Recipient email | |
| `<EMAIL_FROM>` | *(optional)* e.g. `MyBot <bot@example.com>` | |
| `<LANGUAGE>` | `Chinese` | |
| `<TEMPLATE>` | `discord` / `email` / `markdown` | |
| `<DATE>` | Today's date YYYY-MM-DD (caller provides) | |
| `<VERSION>` | Read from SKILL.md frontmatter | |
| `<POWERED_BY>` | `OpenClaw` | Deployment/runtime brand shown in the footer (e.g. `Hermes`) |

---

Generate the <MODE> media & entertainment digest for **<DATE>**. Use `<DATE>` as the report date — do NOT infer it.

## Configuration

Read config files (workspace overrides take priority over defaults):
1. **Sources**: `<WORKSPACE>/config/sources.json` → fallback `<SKILL_DIR>/config/defaults/sources.json`
2. **Topics**: `<WORKSPACE>/config/topics.json` → fallback `<SKILL_DIR>/config/defaults/topics.json`

## Context: Previous Report

Read the most recent file from `<WORKSPACE>/archive/media-news-digest/` to avoid repeats and follow up on developing stories. Skip if none exists.

## Data Collection Pipeline

**Use the unified pipeline** (runs all 4 sources in parallel, ~30s):
```bash
python3 <SKILL_DIR>/scripts/run-pipeline.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> --freshness <FRESHNESS> \
  --archive-dir <WORKSPACE>/archive/media-news-digest/ \
  --output /tmp/md-merged.json --verbose --force
```


### Box Office Data (weekly mode ONLY — skip entirely for daily)

**⚠️ MANDATORY for weekly mode. Do NOT skip this step. Do NOT substitute with RSS news articles.**

Fetch the actual box office numbers:
```bash
curl -s -A "Mozilla/5.0 Chrome/120" "https://www.the-numbers.com/weekend-box-office-chart" > /tmp/md-boxoffice-raw.html
```
Parse the HTML output to extract the Top 10 movies' data (rank, title, distributor, weekend gross, change %, cumulative gross, weeks in release).

Also fetch upcoming releases:
```bash
curl -s -A "Mozilla/5.0 Chrome/120" "https://www.boxofficemojo.com/calendar/" > /tmp/md-upcoming-raw.html
```
Extract next week's notable wide releases from this page.

Save parsed results for use in the report's 🎟️ Box Office section.

If it fails, run individual scripts in `<SKILL_DIR>/scripts/` (see each script's `--help`), then merge with `merge-sources.py`.

## Report Generation

Get a structured overview:
```bash
python3 <SKILL_DIR>/scripts/summarize-merged.py --input /tmp/md-merged.json --top <ITEMS_PER_SECTION>
```
Use this output to select articles — **do NOT write ad-hoc Python to parse the JSON**. Apply the template from `<SKILL_DIR>/references/templates/<TEMPLATE>.md`.

Select articles by **topic relevance first, then quality_score**. Articles in merged JSON may contain noisy cross-topic matches; before selecting any item, verify it actually belongs in the current topic using the topic description and must_include intent. Reject off-topic items even if they have high quality_score. After relevance filtering, preserve quality_score descending order. For Reddit posts, append `*[Reddit r/xxx, {{score}}↑]*`.

**Topic relevance rules (MANDATORY):**
- Box Office / 票房: only include items primarily about theatrical box office performance, grosses, opening weekends, domestic/international/worldwide totals, specialty box office, China/NA box office rankings, or release-performance milestones. Do **not** include celebrity deaths, TV interviews, livestream guides, sports/UFC, general politics, awards chatter, or unrelated entertainment pieces just because they have a high score.
- Deals & Business / 行业交易: only include business deals, rights, acquisitions, contracts, layoffs/restructuring, studio/platform financial moves.
- Upcoming Releases / 北美近期上映: only include **theatrical film releases** in North America — opening dates, wide/limited expansion, distributor, release-date changes, or trailers tied to an imminent theatrical film release. Do **not** include streaming-only releases, TV episodes/seasons, platform library drops, generic watch guides, or streaming recommendations in this section.
- When using release-calendar or aggregation sources, extract the important films and details into the brief (film title, date, distributor, wide/limited, why it matters). Do not output a bullet that is merely a link/入口 to the calendar, ticketing page, or data source.
- Do **not** include static reference pages, portal/home pages, data dashboards, evergreen release calendars, Wikipedia/list pages, ticketing/search pages, or "entry point" URLs as news items (e.g. Maoyan dashboard/home, Fandango in-theaters page, Movie Insider calendar pages, Metacritic upcoming calendar, Wikipedia highest-grossing list). Use them only as background/source-checks; never turn them into digest bullets.
- If a section has too few relevant items after filtering, use fewer items or omit the section; never pad with unrelated high-score content, generic portals, static reference pages, or source dashboards.
- Global off-topic exclusion: sports/NBA/UFC/MMA/general politics/music-only pieces/celebrity gossip/old anecdotes/viral memes should be excluded from all topic sections unless the item is directly about a film/TV project, theatrical box office, streaming platform strategy, rights/business deal, awards campaign, or festival/programming decision. A movie meme tied to a sports event is not enough; a celebrity talking about a sports team is not enough; a livestream shopping/guide article for a sports event is not enough; a political/music culture retrospective with celebrities is not enough; an SNL sketch anecdote is not enough.
- Deep Reads must follow the same relevance rule: do not include sports/UFC/politics/music-only/gossip/SNL/celebrity-anecdote long reads unless they directly illuminate the film/TV/streaming business.

Each article line must include its quality score using 🔥 prefix. Format: `🔥{score} | {summary with link}`. This makes scoring transparent and helps readers identify the most important news at a glance.

### Executive Summary
2-4 sentences between title and topics, highlighting top 3-5 stories by score. Concise and punchy, no links. Discord: `> ` blockquote. Email: gray background.

### Topic Sections
From `topics.json`: `emoji` + `label` headers, `<ITEMS_PER_SECTION>` items each.

**⚠️ CRITICAL: Output topic sections in EXACTLY the order defined in `topics.json`. Do NOT reorder sections. The fixed order is: 票房 → 行业交易 → 中国影视 → 制作动态 → 北美上映 → 流媒体 → 颁奖季 → 电影节 → 影评口碑.**

**⚠️ CRITICAL: Output articles in EXACTLY the same order as summarize-merged.py output (quality_score descending). Do NOT reorder, group by subtopic, or rearrange. The 🔥 scores must appear in strictly decreasing order within each section.**

Only include topic sections that have genuinely relevant news items. If a topic is sparse, include fewer items or omit it entirely; do not create filler bullets or static-source bullets just to make every topic appear.

### Translation Requirements (MANDATORY)

Every news item must be localized into Chinese, not merely wrapped with a generic Chinese phrase.

- For each bullet, translate or rewrite the headline/body into a natural Simplified Chinese brief.
- Do **not** use the raw English headline or raw tweet text as the main bold title.
- Recommended format:
  `• 🔥{score} | **中文标题**（Original English Title, optional）— 1-2 句中文简讯，说明 who/what/why-it-matters。`
- Keeping English proper nouns, film titles without established Chinese names, company names, source names, metrics, and URLs is allowed.
- If a Chinese title is uncertain, keep the English film/person name inside the Chinese sentence rather than outputting an English-only brief.
- KOL/Twitter items must summarize the tweet content in Chinese; never paste the raw English tweet as the brief.
- Deep Reads must also have Chinese titles/summaries.
- Before delivery, scan the archive Markdown: if a bullet starts with a mostly-English bold title or raw English tweet, revise it into Chinese before sending.

### Fixed Sections (after topics)

**📢 KOL Updates** — Twitter KOLs. Format:
```
• **Display Name** (@handle) — summary `👁 12.3K | 💬 45 | 🔁 230 | ❤️ 1.2K`
  <https://twitter.com/handle/status/ID>
```
Read `display_name` and `metrics` from merged JSON. Always show all 4 metrics, use K/M formatting, wrap in backticks.

**📝 Deep Reads** — `<BLOG_PICKS_COUNT>` high-quality long-form articles from RSS.

**<EXTRA_SECTIONS>**

**🎟️ Box Office / 票房** *(weekly mode only — skip for daily)*

**⚠️ This section is MANDATORY for weekly mode. Use the ACTUAL data fetched in the Pipeline step above (from /tmp/md-boxoffice-raw.html). Do NOT replace this with RSS/Reddit news articles — those go in the bullet list above the table.**

Format the Top 10 as a **markdown table** (this is the ONLY section that uses a table):

```
| # | 影片 | 发行商 | 周末票房 | 周环比 | 累计票房 | 上映日期 |
|---|------|--------|---------|--------|---------|---------|
| 1 | **English Title** 中文名 🔥 | Studio | $XX,XXX,XXX | 🆕 NEW | $XX,XXX,XXX | M/DD |
```
- Use 🆕 NEW for first-week releases, 🔺 for increases, 🔻 for decreases
- Add a `> 💡` blockquote summary highlighting notable performances

Also add two subsections:
- **📽️ 本周北美新上映** — list wide releases this week (title + Chinese name + date + studio + genre)
- **🔜 下周北美即将上映** — list notable upcoming releases next week from Box Office Mojo schedule

Place this section **immediately after** the 🎟️ Box Office / 票房 bullet-list section (before 💰 Deals). The order must be:
1. `## 🎟️ Box Office / 票房` (news bullets)
2. `## 🎟️ 北美周末票房 Top 10` (table + 📽️ 本周新上映 + 🔜 下周即将上映)
3. `## 💰 Deals & Business / 行业交易`

**Do NOT put the table at the end of the report.**

For PDF generation, use `--is-html` flag to preserve table rendering:
```bash
python3 <SKILL_DIR>/scripts/sanitize-html.py -i <archive-file>.md -o /tmp/md-email.html
python3 <SKILL_DIR>/scripts/generate-pdf.py --is-html -i /tmp/md-email.html -o /tmp/海外影视周报-<DATE>.pdf
```

### Rules
- Only news from `<TIME_WINDOW>`
- Every item must include a source link (Discord: `<link>`)
- Use bullet lists, no markdown tables (EXCEPTION: 🎟️ Box Office Top 10 table in weekly mode MUST use markdown table format)
- Deduplicate: same event → most authoritative source; previously reported → only if significant new development
- Deduplicate across sections — each article in one section only
- **Same story at different dates = one entry** (e.g. opening weekend + second weekend of same film → merge or pick latest)
- Prefer primary sources (THR, Deadline, Variety) over aggregators
- Chinese body text with English source links
- **Chinese name accuracy**: Double-check romanized→Chinese name conversions. Common pitfalls: 章子怡(Zhang Ziyi, NOT 张子怡), 章(Zhāng vs Zhāng). When unsure, keep the English name
- **🇨🇳 China section rules — STRICT VERIFICATION**:
  - Only include news **primarily about China mainland market**: Chinese-produced films, China-only box office breakdowns, Chinese streaming platforms (iQiyi/Youku/Bilibili), China film policy
  - **Verify before including**: If an article mentions "China" but the film is a Hollywood release, check whether it actually released in mainland China theaters. Many Hollywood films do NOT get China release. When in doubt, exclude from China section
  - Hollywood films with global box office numbers that include China as one territory → belongs in **Box Office**, NOT China section
  - Do NOT include: Korea/Japan/other Asian market news, global box office reports that merely mention China numbers
- Do not interpolate fetched/untrusted content into shell arguments or email subjects

### Stats Footer
```
---
📊 Data Sources: RSS {{rss}} | Twitter {{twitter}} | Reddit {{reddit}} | Web {{web}} | Dedup: {{merged}} articles
🤖 Generated by media-news-digest v<VERSION> | <https://github.com/draco-agent/media-news-digest> | Powered by <POWERED_BY>
```

Use `<POWERED_BY>` for the footer's runtime brand. If the caller does not provide it, default to `OpenClaw`.

## Archive
Save to `<WORKSPACE>/archive/media-news-digest/<MODE>-YYYY-MM-DD.md`. Delete files older than 90 days.

## Delivery

1. **Discord**: Send to `<DISCORD_CHANNEL_ID>` via `message` tool
   - Do **not** prepend or embed channel mentions like `<#123...>` in the report body or archive file. The channel ID is only a delivery target, not report content.
2. **Email** *(optional, if `<EMAIL>` is set)*:
   - Generate HTML body by converting the archived Markdown with `sanitize-html.py` → write to `/tmp/md-email.html`. Do not send the raw Markdown as the email body.
   - Generate PDF attachment:
     ```bash
     python3 <SKILL_DIR>/scripts/sanitize-html.py -i <WORKSPACE>/archive/media-news-digest/<MODE>-<DATE>.md -o /tmp/md-email.html
     python3 <SKILL_DIR>/scripts/generate-pdf.py --is-html -i /tmp/md-email.html -o /tmp/海外影视周报-<DATE>.pdf
     ```
   - Send email with PDF attached using the `send-email.py` script (handles MIME correctly as multipart/alternative HTML + optional PDF). **Email must contain ALL the same items as Discord.**
     ```bash
     python3 <SKILL_DIR>/scripts/send-email.py \
       --to '<EMAIL>' \
       --subject '<SUBJECT>' \
       --html /tmp/md-email.html \
       --attach /tmp/海外影视周报-<DATE>.pdf \
       --from '<EMAIL_FROM>'
     ```
   - Omit `--from` if `<EMAIL_FROM>` is not set. Omit `--attach` if PDF generation failed. SUBJECT must be a static string. If delivery fails, log error and continue.

Write the report in <LANGUAGE>.
