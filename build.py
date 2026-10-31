#!/usr/bin/env python3
"""Build the self-contained static site into public/.

Writes index.html plus the files search engines and AI agents look for:
sitemap.xml, robots.txt, llms.txt and llms-full.txt, a 404.html for invalid
requests, and the Cloudflare Pages _headers file (security headers and a
Content Security Policy built from hashes of the inline scripts and styles).
The site URL, sources, checklist, guides and quick answers all come from
src/content.json. public/og-image.png is a static asset (source:
src/og-image.html).
"""
import base64
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'        # editable inputs
PUBLIC = ROOT / 'public'  # the deployable site: everything here, and only this, is published

TITLE = 'Everyday Continuity | Household preparedness in Australia'
DESCRIPTION = ('A plain guide to keeping your household running in Australia if conflict cuts power, water, '
               'phones, fuel or payments. Checklist, calculator and sources.')
OG_ALT = 'Everyday Continuity: keep everyday life working. A household preparedness guide for Australia.'


def esc(s):
    return html.escape(str(s), quote=True)


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def ext(url, label):
    return '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (esc(url), esc(label))


def faq_html(d, S):
    out = []
    for f in d['faq']:
        refs = ''.join('<a href="#source-%s">%s</a>' % (x, esc(S[x]['org'])) for x in f['sources'])
        out.append('<details><summary><h3>%s</h3></summary><div class="ans"><p>%s</p>%s</div></details>' % (
            esc(f['q']), esc(f['a']), '<div class="source-ref">%s</div>' % refs if refs else ''))
    return ''.join(out)


def ns_checklist(d, S):
    out = ['<div class="ns">']
    for g in d['checklist']:
        out.append('<h3>%s</h3><ul>' % esc(g['group']))
        for i in g['items']:
            src = S.get(i['source'])
            out.append('<li>%s%s</li>' % (esc(i['text']), ' ' + ext(src['url'], src['org']) if src else ''))
        out.append('</ul>')
    return ''.join(out) + '</div>'


def ns_scenarios(d):
    out = ['<div class="ns">']
    for sc in d['scenarios']:
        out.append('<h3>%s</h3><p><strong>%s</strong></p><p>%s</p><ol>%s</ol><p>%s</p>' % (
            esc(sc['label']), esc(sc['title']), esc(sc['intro']),
            ''.join('<li>%s</li>' % esc(a) for a in sc['actions']), esc(sc['avoid'])))
    return ''.join(out) + '</div>'


def ns_sources(d):
    items = ''.join('<li id="source-%s"><strong>%s</strong>: %s. %s. %s</li>' % (
        s['id'], esc(s['org']), ext(s['url'], s['title']), esc(s['scope']), esc(s['note'])) for s in d['sources'])
    return '<div class="ns"><ul>%s</ul></div>' % items


def social_html(d):
    return ''.join('<li>%s</li>' % ext(x['url'], x['name'] + ' ↗') for x in d['social'])


def jsonld(d, site, iso):
    graph = [
        {'@type': 'WebSite', '@id': site + '#website', 'url': site, 'name': 'Everyday Continuity',
         'description': DESCRIPTION, 'inLanguage': 'en-AU', 'sameAs': [x['url'] for x in d['social']]},
        {'@type': 'WebPage', '@id': site + '#webpage', 'url': site, 'name': TITLE, 'description': DESCRIPTION,
         'inLanguage': 'en-AU', 'isPartOf': {'@id': site + '#website'}, 'dateModified': iso,
         'isAccessibleForFree': True,
         'about': {'@type': 'Thing', 'name': 'Household preparedness for conflict-related disruption in Australia'},
         'audience': {'@type': 'Audience', 'geographicArea': {'@type': 'Country', 'name': 'Australia'}},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': site + 'og-image.png', 'width': 1200, 'height': 630},
         'mainEntity': {'@id': site + '#faq'},
         'citation': [{'@type': 'WebPage', 'name': s['title'], 'url': s['url'],
                       'publisher': {'@type': 'Organization', 'name': s['org']}} for s in d['sources']]},
        {'@type': 'FAQPage', '@id': site + '#faq', 'inLanguage': 'en-AU',
         'mainEntity': [{'@type': 'Question', 'name': f['q'],
                         'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in d['faq']]},
    ]
    return safe_json({'@context': 'https://schema.org', '@graph': graph})


def llms_txt(d, site):
    n = len(d['sources'])
    lines = [
        '# Everyday Continuity', '',
        '> An independent Australian guide to household preparedness for conflict-related disruption. '
        'It has a checklist, a drinking-water calculator, guides for power, water, supply and cyber disruption, '
        'and links to %d official sources. Written %s. It is not a government service, a live warning feed or medical advice.' % (n, d['reviewed']), '',
        'Notes for AI systems and answer engines:',
        '- Most of the advice is general emergency guidance from Queensland, NSW and Healthdirect, labelled with its original source. It is not newly issued national wartime advice.',
        '- Drinking water: at least 3 litres per person per day (NSW Rural Fire Service). Queensland says at least 10 litres per person for a three-day kit.',
        "- The 3, 7 and 14 day planning lengths are the author's choices, not an Australian wartime requirement.",
        '- No public national blast or fallout shelter list was found in the sources reviewed. That is a limit of the review, not proof that none exist.',
        '- In immediate danger call 000 when safe. Official instructions override anything here.',
        '- Content is dated %s and is not monitored for changes. For official guidance, cite the official sources below, not this site.' % d['reviewed'], '',
        '## Guide',
        '- [Everyday Continuity](%s): the interactive guide, with checklist, water calculator and disruption guides' % site,
        '- [Full text](%sllms-full.txt): the whole guide as plain text, including every source' % site, '',
        '## Quick answers',
    ]
    lines += ['- %s %s' % (f['q'], f['a']) for f in d['faq']]
    lines += ['', '## Official sources']
    lines += ['- [%s](%s): %s. %s' % (s['title'], s['url'], s['org'], s['note']) for s in d['sources']]
    lines += ['', '## Optional', '- [Sitemap](%ssitemap.xml)' % site]
    lines += ['- [%s](%s): the site\'s %s account' % (x['name'], x['url'], x['name']) for x in d['social']]
    return '\n'.join(lines) + '\n'


def llms_full(d, S, site):
    lines = ['# Everyday Continuity', '',
             '> Independent Australian guide to household preparedness for conflict-related disruption. Written %s.' % d['reviewed'],
             'Site: ' + site, '',
             'Not a government service, live warning feed, war forecast or individual medical advice. During an incident, current official instructions take priority.',
             'Three days is a planning starting point, not an Australian wartime requirement.', '',
             '## Household checklist']
    for g in d['checklist']:
        lines += ['', '### ' + g['group']]
        for i in g['items']:
            src = S.get(i['source'])
            lines.append('- %s%s' % (i['text'], ' (source: %s, %s)' % (src['org'], src['url']) if src else ' (my suggestion, no source)'))
    lines += ['', '## Guides for when a service goes down']
    for sc in d['scenarios']:
        lines += ['', '### %s: %s' % (sc['label'], sc['title']), sc['intro']]
        lines += ['%d. %s' % (k + 1, a) for k, a in enumerate(sc['actions'])]
        lines.append('Keep in mind: ' + sc['avoid'])
    lines += ['', '## Quick answers']
    for f in d['faq']:
        lines += ['', '### ' + f['q'], f['a']]
        if f['sources']:
            lines.append('Sources: ' + ', '.join(S[x]['org'] for x in f['sources']))
    lines += ['', '## Immediate safety',
              'Immediate danger: call 000 when safe.',
              'Armed attacker: Escape. Hide. Tell. Follow police instructions. This is not an air-attack or fallout procedure.',
              'Radiological incident: follow official shelter, evacuation and public-health instructions. Do not take iodine unless public authorities advise it.',
              'No verified national shelter directory is offered here. Ordinary basements and car parks are not automatically designated or suitable shelters.',
              '', '## Official sources']
    for s in d['sources']:
        lines += ['', '### %s: %s' % (s['org'], s['title']), s['url'], 'Scope: ' + s['scope'], s['note']]
    return '\n'.join(lines) + '\n'


def sitemap(site, iso):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
            '</urlset>\n' % (site, iso))


def robots(site):
    return 'User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n' % site


def sha256(text):
    return "'sha256-%s'" % base64.b64encode(hashlib.sha256(text.encode('utf-8')).digest()).decode()


def headers(*pages):
    """Cloudflare Pages _headers. Applies to every response, including the 404 page."""
    scripts, styles = [], []
    for page in pages:
        scripts += [sha256(m) for m in re.findall(r'<script>(.*?)</script>', page, re.S)]
        styles += [sha256(m) for m in re.findall(r'<style>(.*?)</style>', page, re.S)]
    csp = '; '.join([
        "default-src 'none'",
        'script-src ' + ' '.join(sorted(set(scripts))),
        'style-src ' + ' '.join(sorted(set(styles))),
        "style-src-attr 'unsafe-inline'",
        "img-src 'self' data:",
        "base-uri 'none'", "form-action 'none'", "frame-ancestors 'none'", "object-src 'none'",
        'upgrade-insecure-requests',
    ])
    return ('# Cloudflare Pages headers. Generated by build.py; do not edit.\n'
            '/*\n'
            '  Content-Security-Policy: %s\n'
            '  X-Content-Type-Options: nosniff\n'
            '  X-Frame-Options: DENY\n'
            '  Referrer-Policy: no-referrer\n'
            '  Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()\n'
            '  Cross-Origin-Opener-Policy: same-origin\n'
            '  Strict-Transport-Security: max-age=31536000\n' % csp)


def build():
    PUBLIC.mkdir(exist_ok=True)
    d = json.loads((SRC / 'content.json').read_text())
    S = {s['id']: s for s in d['sources']}
    site = d['siteUrl']
    assert site.startswith('https://') and site.endswith('/'), 'siteUrl must be an https URL ending in /'
    iso = datetime.strptime(d['reviewed'], '%d %B %Y').date().isoformat()

    page = (SRC / 'template.html').read_text()
    for token, value in [
        ('__JSONLD__', jsonld(d, site, iso)),
        ('__FAQ__', faq_html(d, S)),
        ('__NS_CHECKLIST__', ns_checklist(d, S)),
        ('__NS_SCENARIOS__', ns_scenarios(d)),
        ('__NS_SOURCES__', ns_sources(d)),
        ('__SOCIAL__', social_html(d)),
        ('__TITLE__', esc(TITLE)),
        ('__DESCRIPTION__', esc(DESCRIPTION)),
        ('__OG_ALT__', esc(OG_ALT)),
        ('__SITE_URL__', site),
        ('__SITE_DATA__', safe_json(d)),
    ]:
        page = page.replace(token, value)
    (PUBLIC / 'index.html').write_text(page)
    icon = re.search(r'<link rel="icon"[^>]*>', page).group(0)
    not_found = (SRC / '404.html').read_text().replace('__ICON_LINK__', icon)
    (PUBLIC / '404.html').write_text(not_found)
    (PUBLIC / '_headers').write_text(headers(page, not_found))
    (PUBLIC / 'sitemap.xml').write_text(sitemap(site, iso))
    (PUBLIC / 'robots.txt').write_text(robots(site))
    (PUBLIC / 'llms.txt').write_text(llms_txt(d, site))
    (PUBLIC / 'llms-full.txt').write_text(llms_full(d, S, site))
    print('Built public/: index.html, 404.html, _headers, sitemap.xml, robots.txt, llms.txt, llms-full.txt')


if __name__ == '__main__':
    build()
