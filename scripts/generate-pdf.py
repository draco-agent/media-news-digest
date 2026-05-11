#!/usr/bin/env python3
"""
Generate styled PDF from markdown digest report.

Converts a media-news-digest markdown report into a professional PDF
with Chinese font support, emoji icons, and clean typography.

Usage:
    python3 generate-pdf.py --input /tmp/md-report.md --output /tmp/md-digest.pdf [--verbose]

Requirements:
    - weasyprint (pip install weasyprint)
    - Noto Sans CJK SC font (apt install fonts-noto-cjk)
"""

import argparse
import html
import re
import sys
import logging
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Markdown → HTML conversion (with sanitization)
# ---------------------------------------------------------------------------

def escape(text: str) -> str:
    return html.escape(text, quote=True)


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ('http', 'https')
    except Exception:
        return False


def _process_inline(text: str) -> str:
    """Process inline markdown with HTML escaping."""
    result = escape(text)

    # Bold: **text**
    result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)

    # Inline code: `text`
    result = re.sub(
        r'`(.+?)`',
        r'<code>\1</code>',
        result
    )

    # Angle-bracket links: <https://...>
    def restore_link(m):
        url = html.unescape(m.group(1))
        if is_safe_url(url):
            escaped_url = escape(url)
            try:
                domain = urlparse(url).netloc
                return f'<a href="{escaped_url}">{escape(domain)}</a>'
            except Exception:
                return f'<a href="{escaped_url}">{escaped_url}</a>'
        return escape(url)

    result = re.sub(r'&lt;(https?://[^&]+?)&gt;', restore_link, result)

    # Markdown links: [text](url)
    def restore_md_link(m):
        label = html.unescape(m.group(1))
        url = html.unescape(m.group(2))
        if is_safe_url(url):
            return f'<a href="{escape(url)}">{escape(label)}</a>'
        return escape(label)

    result = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', restore_md_link, result)

    return result


def _render_table(rows):
    """Render markdown table rows for PDF output."""
    if not rows:
        return ''

    colgroup = ''
    if len(rows[0]) == 7:
        widths = ['5%', '24%', '14%', '14%', '10%', '15%', '18%']
        colgroup = '<colgroup>' + ''.join(f'<col style="width:{w}">' for w in widths) + '</colgroup>'

    html_rows = [f'<table class="box-office-table">{colgroup}<thead><tr>']
    for cell in rows[0]:
        html_rows.append(f'<th>{_process_inline(cell)}</th>')
    html_rows.append('</tr></thead><tbody>')

    for row in rows[1:]:
        html_rows.append('<tr>')
        for i, cell in enumerate(row):
            classes = []
            if i == 1:
                classes.append('film-title')
            if len(row) > 4 and i == 4:
                if any(x in cell for x in ['🔻', '-']) and 'NEW' not in cell:
                    classes.append('down')
                elif any(x in cell for x in ['🔺', '+']) or 'NEW' in cell:
                    classes.append('up')
            class_attr = f' class="{" ".join(classes)}"' if classes else ''
            html_rows.append(f'<td{class_attr}>{_process_inline(cell)}</td>')
        html_rows.append('</tr>')

    html_rows.append('</tbody></table>')
    return ''.join(html_rows)


def markdown_to_html(md_content: str) -> str:
    """Convert markdown digest to styled HTML for PDF rendering."""
    lines = md_content.strip().split('\n')
    html_parts = []
    in_list = False
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_table:
                html_parts.append(_render_table(table_rows))
                in_table = False
                table_rows = []
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            continue

        # H1
        if stripped.startswith('# '):
            if in_table:
                html_parts.append(_render_table(table_rows))
                in_table = False
                table_rows = []
            title = _process_inline(stripped[2:])
            html_parts.append(f'<h1>{title}</h1>')
            continue

        # H2
        if stripped.startswith('## '):
            if in_table:
                html_parts.append(_render_table(table_rows))
                in_table = False
                table_rows = []
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            section = _process_inline(stripped[3:])
            html_parts.append(f'<h2>{section}</h2>')
            continue

        # H3
        if stripped.startswith('### '):
            if in_table:
                html_parts.append(_render_table(table_rows))
                in_table = False
                table_rows = []
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            section = _process_inline(stripped[4:])
            html_parts.append(f'<h3>{section}</h3>')
            continue

        # Blockquote
        if stripped.startswith('> '):
            text = _process_inline(stripped[2:])
            html_parts.append(f'<blockquote>{text}</blockquote>')
            continue

        # Horizontal rule
        if stripped == '---':
            html_parts.append('<hr>')
            continue

        # Table row: | col | col |
        if stripped.startswith('|') and '|' in stripped[1:]:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if not in_table:
                in_table = True
                table_rows = []
            if re.match(r'^\|[\s\-|:]+\|$', stripped):
                continue
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            table_rows.append(cells)
            continue

        if in_table:
            html_parts.append(_render_table(table_rows))
            in_table = False
            table_rows = []

        # Bullet items
        if stripped.startswith('• ') or stripped.startswith('- '):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            item_text = stripped[2:]
            safe_item = _process_inline(item_text)
            html_parts.append(f'<li>{safe_item}</li>')
            continue

        # Angle-bracket link on its own line (often source URLs)
        if stripped.startswith('<http') and in_list:
            url = stripped.strip('<> ')
            if is_safe_url(url):
                escaped_url = escape(url)
                try:
                    domain = urlparse(url).netloc
                    label = escape(domain)
                except Exception:
                    label = escaped_url
                html_parts.append(f'<li class="source-link"><a href="{escaped_url}">{label}</a></li>')
            continue

        # Stats/footer
        if stripped.startswith('📊') or stripped.startswith('🤖'):
            text = _process_inline(stripped)
            html_parts.append(f'<p class="footer">{text}</p>')
            continue

        # Regular paragraph
        text = _process_inline(stripped)
        html_parts.append(f'<p>{text}</p>')

    if in_table:
        html_parts.append(_render_table(table_rows))

    if in_list:
        html_parts.append('</ul>')

    return '\n'.join(html_parts)


# ---------------------------------------------------------------------------
# PDF CSS
# ---------------------------------------------------------------------------

PDF_CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
    @top-center {
        content: "Tech Digest";
        font-size: 9px;
        color: #999;
        font-family: 'Noto Sans CJK SC', 'Noto Sans SC', sans-serif;
    }
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 9px;
        color: #999;
        font-family: 'Noto Sans CJK SC', 'Noto Sans SC', sans-serif;
    }
}

body {
    font-family: 'Noto Sans CJK SC', 'Noto Sans SC', 'PingFang SC',
                 'Microsoft YaHei', 'Segoe UI', Roboto, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
}

h1 {
    font-size: 22pt;
    color: #111;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-bottom: 20px;
    margin-top: 0;
}

h2 {
    font-size: 15pt;
    color: #1e40af;
    margin-top: 28px;
    margin-bottom: 12px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e5e7eb;
}

h3 {
    font-size: 13pt;
    color: #374151;
    margin-top: 20px;
    margin-bottom: 8px;
}

blockquote {
    background: #f0f4ff;
    border-left: 4px solid #2563eb;
    padding: 12px 16px;
    margin: 16px 0;
    color: #374151;
    font-size: 10.5pt;
    border-radius: 0 6px 6px 0;
}

ul {
    padding-left: 20px;
    margin: 8px 0;
}

li {
    margin-bottom: 10px;
    line-height: 1.6;
}

li.source-link {
    list-style: none;
    margin-bottom: 2px;
    margin-top: -6px;
}

li.source-link a {
    font-size: 9pt;
}

a {
    color: #2563eb;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

strong {
    color: #111;
}

code {
    font-family: 'Noto Sans Mono CJK SC', 'SF Mono', 'Fira Code', monospace;
    font-size: 9pt;
    background: #f3f4f6;
    padding: 2px 5px;
    border-radius: 3px;
    color: #6b7280;
}

hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 28px 0;
}

p.footer {
    font-size: 8.5pt;
    color: #9ca3af;
    margin-top: 4px;
}

.box-office-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin: 14px 0 18px;
    font-size: 8.2pt;
    line-height: 1.25;
    page-break-inside: avoid;
}

.box-office-table th {
    background: #1f4e79;
    color: #fff;
    font-weight: 700;
    text-align: center;
    border: 0.6pt solid #d1d5db;
    padding: 4pt 3pt;
    overflow-wrap: anywhere;
}

.box-office-table td {
    text-align: center;
    border: 0.5pt solid #e5e7eb;
    padding: 3.5pt 3pt;
    word-break: keep-all;
}

.box-office-table td.film-title {
    text-align: left;
    overflow-wrap: anywhere;
    word-break: normal;
}

.box-office-table td.up {
    color: #047857;
    background: #ecfdf5;
}

.box-office-table td.down {
    color: #b91c1c;
    background: #fef2f2;
}

/* First page title area */
h1 + blockquote {
    margin-top: 12px;
}

/* Emoji rendering */
body {
    -webkit-font-smoothing: antialiased;
}
"""


# ---------------------------------------------------------------------------
# HTML wrapper
# ---------------------------------------------------------------------------

def wrap_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
{PDF_CSS}
</style>
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate styled PDF from markdown digest report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
    python3 generate-pdf.py -i /tmp/md-report.md -o /tmp/md-digest.pdf
    python3 generate-pdf.py -i report.md -o digest.pdf --verbose

Requirements:
    pip install weasyprint
    apt install fonts-noto-cjk  (for Chinese support)
"""
    )
    parser.add_argument("--input", "-i", required=True, help="Input markdown or HTML file")
    parser.add_argument("--is-html", action="store_true", help="Input is pre-rendered HTML body (skip markdown conversion)")
    parser.add_argument("--output", "-o", required=True, help="Output PDF file")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    try:
        import weasyprint
    except ImportError:
        logging.error("weasyprint not installed. Run: pip install weasyprint")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        logging.error(f"Input file not found: {args.input}")
        sys.exit(1)

    content = input_path.read_text(encoding='utf-8')
    logging.info(f"Converting {args.input} ({len(content)} chars)")

    if args.is_html:
        # Input is already rendered HTML
        full_html = wrap_html(content)
    else:
        # Convert markdown → HTML → PDF
        body_html = markdown_to_html(content)
        full_html = wrap_html(body_html)

    # Optionally save intermediate HTML for debugging
    if args.verbose:
        html_debug = Path(args.output).with_suffix('.html')
        html_debug.write_text(full_html, encoding='utf-8')
        logging.debug(f"Debug HTML saved: {html_debug}")

    # Generate PDF
    logging.info("Generating PDF...")
    doc = weasyprint.HTML(string=full_html)
    doc.write_pdf(args.output)

    output_size = Path(args.output).stat().st_size
    logging.info(f"✅ PDF generated: {args.output} ({output_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
