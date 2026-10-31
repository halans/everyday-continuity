#!/usr/bin/env python3
"""Zero-dependency content/build contract checks; browser tests documented separately."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
SRC = ROOT/'src'
PUBLIC = ROOT/'public'
D = json.loads((SRC/'content.json').read_text())
H = (PUBLIC/'index.html').read_text()

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.external=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a':
            self.links.append(a.get('href',''))
            if a.get('href','').startswith('http'): self.external.append(a)

class Contracts(unittest.TestCase):
    def test_01_source_ids_unique(self):
        ids=[s['id'] for s in D['sources']]; self.assertEqual(len(ids),len(set(ids))); self.assertEqual(len(ids),20)
    def test_02_sources_https_and_scoped(self):
        for s in D['sources']:
            self.assertTrue(s['url'].startswith('https://')); self.assertTrue(s['scope']); self.assertTrue(s['note'])
    def test_03_checklist_ids_unique(self):
        ids=[i['id'] for g in D['checklist'] for i in g['items']]
        self.assertEqual(len(ids),18); self.assertEqual(len(ids),len(set(ids)))
    def test_04_source_references_resolve(self):
        ids={s['id'] for s in D['sources']}
        for g in D['checklist']:
            for i in g['items']:
                self.assertTrue(i['source'] is None or i['source'] in ids)
        for s in D['scenarios']:
            for ref in s['sources']: self.assertIn(ref,ids)
    def test_05_embedded_data_matches(self):
        m=re.search(r'<script id="site-data" type="application/json">(.*?)</script>',H,re.S)
        self.assertEqual(json.loads(m.group(1)),D)
    def test_06_no_build_token(self): self.assertNotRegex(H,r'__[A-Z][A-Z_]*[A-Z]__')
    def test_07_html_ids_unique(self):
        p=Parser();p.feed(H);self.assertEqual(len(p.ids),len(set(p.ids)))
    def test_08_static_anchors_resolve(self):
        p=Parser();p.feed(H);ids=set(p.ids)|{'source-'+s['id'] for s in D['sources']}
        for a in p.links:
            if a.startswith('#'): self.assertIn(a[1:],ids)
    def test_09_no_runtime_network_dependencies(self):
        self.assertNotRegex(H,r'<script[^>]+src='); 
        for tag in re.findall(r'<link\b[^>]*>',H):
            self.assertTrue(any(k in tag for k in ('rel="canonical"','rel="alternate"','rel="sitemap"','href="data:')),tag[:80])
        self.assertNotRegex(H,r'<img[^>]+src="https?');self.assertNotIn('fetch(',H)
    def test_10_js_syntax(self):
        scripts=re.findall(r'<script>(.*?)</script>',H,re.S)
        with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as f:
            f.write('\n'.join(scripts));f.flush();subprocess.run(['node','--check',f.name],check=True,capture_output=True)
    def test_14_scope_and_safety_boundaries(self):
        for phrase in ['not a live warning','not a universal shelter rule','Do not self-dose with iodine',"haven't confirmed that every state and territory is live",'not a safety score']:
            self.assertIn(phrase.lower(),H.lower())
    def test_15_sources_open_safely(self):
        self.assertIn('target="_blank" rel="noopener noreferrer"',H)
    def test_16_accessibility_hooks(self):
        for phrase in ['class="skip"','prefers-reduced-motion','role="tablist"','aria-live="polite"','@media print']:
            self.assertIn(phrase,H)
    def test_18_branding_consistent(self):
        self.assertIn('Everyday Continuity', H)
        self.assertIn('Keep everyday', H)
        self.assertIn('<em>working.</em>', H)
        self.assertNotIn('Civil Ready Australia', H)
        self.assertNotIn('CIVIL READY', H)
        self.assertIn('Sources reviewed', H)
        self.assertIn("const KEY='civil-ready-au-v1'", H)

    # ---- search and AI-discovery files ----
    def _ld(self):
        m=re.search(r'<script type="application/ld\+json">(.*?)</script>',H,re.S)
        return json.loads(m.group(1))
    def test_19_structured_data_matches_page(self):
        g={n['@type']:n for n in self._ld()['@graph']}
        self.assertEqual(set(g),{'WebSite','WebPage','FAQPage'})
        self.assertEqual(g['WebPage']['url'],D['siteUrl'])
        self.assertEqual(len(g['WebPage']['citation']),len(D['sources']))
        qs=[q['name'] for q in g['FAQPage']['mainEntity']]
        self.assertEqual(qs,[f['q'] for f in D['faq']])
        visible=re.findall(r'<summary><h3>(.*?)</h3></summary>',H)
        self.assertEqual([x.replace('&#x27;',"'") for x in visible],qs)
    def test_20_faq_sources_resolve(self):
        ids={s['id'] for s in D['sources']}
        for f in D['faq']:
            for x in f['sources']: self.assertIn(x,ids)
    def test_21_head_tags(self):
        site=D['siteUrl']
        self.assertTrue(site.startswith('https://') and site.endswith('/'))
        for needle in ['<link rel="canonical" href="%s">'%site,'property="og:url" content="%s"'%site,'property="og:image" content="%sog-image.png"'%site,
                       'name="twitter:card" content="summary_large_image"','name="robots"','<html lang="en-AU"']:
            self.assertIn(needle,H)
        title=re.search(r'<title>(.*?)</title>',H).group(1); desc=re.search(r'name="description" content="([^"]*)"',H).group(1)
        self.assertLessEqual(len(title),65); self.assertTrue(120<=len(desc)<=160,len(desc)); self.assertEqual(len(re.findall(r'<h1[ >]',H)),1)
    def test_22_sitemap_robots_llms(self):
        import xml.etree.ElementTree as ET
        site=D['siteUrl']
        root=ET.parse(PUBLIC/'sitemap.xml').getroot(); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        self.assertEqual([e.text for e in root.findall('s:url/s:loc',ns)],[site])
        self.assertRegex(root.find('s:url/s:lastmod',ns).text,r'^\d{4}-\d{2}-\d{2}$')
        self.assertIn('Sitemap: '+site+'sitemap.xml',(PUBLIC/'robots.txt').read_text())
        llms=(PUBLIC/'llms.txt').read_text(); self.assertTrue(llms.startswith('# Everyday Continuity\n')); self.assertIn('\n> ',llms)
        full=(PUBLIC/'llms-full.txt').read_text()
        for s in D['sources']: self.assertIn(s['url'],llms); self.assertIn(s['url'],full)
        for g in D['checklist']:
            for i in g['items']: self.assertIn(i['text'],full)
    def test_23_content_readable_without_javascript(self):
        for g in D['checklist']:
            for i in g['items']: self.assertIn(i['text'].replace("'",'&#x27;'),H)
        for sc in D['scenarios']: self.assertIn(sc['intro'].replace("'",'&#x27;'),H)
        for s in D['sources']: self.assertIn('<li id="source-%s">'%s['id'],H)
    def test_24_og_image(self):
        b=(PUBLIC/'og-image.png').read_bytes()
        self.assertEqual(b[:8],b'\x89PNG\r\n\x1a\n'); self.assertEqual(int.from_bytes(b[16:20],'big'),1200); self.assertEqual(int.from_bytes(b[20:24],'big'),630)

    def test_25_social_link(self):
        url=D['social'][0]['url']
        self.assertEqual(url,'https://bsky.app/profile/prepper.downunder.blue')
        self.assertIn('<a href="%s" target="_blank" rel="noopener noreferrer">Bluesky'%url,H)
        g={n['@type']:n for n in self._ld()['@graph']}
        self.assertEqual(g['WebSite']['sameAs'],[url])
        self.assertIn(url,(PUBLIC/'llms.txt').read_text())

    # ---- hosting: 404 page, security headers, hash handling ----
    def test_26_malformed_hash_cannot_throw(self):
        self.assertNotIn('querySelector(location.hash)',H)
        self.assertIn('decodeURIComponent(location.hash',H); self.assertIn('document.getElementById(id)',H)
    def test_27_404_page(self):
        n=(PUBLIC/'404.html').read_text()
        self.assertIn('name="robots" content="noindex"',n); self.assertIn('<title>Page not found',n)
        self.assertNotRegex(n,r'<script'); self.assertNotRegex(n,r'(src|href)="https?://')
        self.assertNotIn('__ICON_LINK__',n); self.assertIn('href="/"',n); self.assertNotIn('canonical',n)
        self.assertNotIn('404.html',(PUBLIC/'sitemap.xml').read_text())
    def test_28_headers_cover_every_inline_script_and_style(self):
        import base64
        hd=(PUBLIC/'_headers').read_text()
        csp=re.search(r'Content-Security-Policy: (.*)',hd).group(1)
        def h(x): return "'sha256-%s'"%base64.b64encode(hashlib.sha256(x.encode('utf-8')).digest()).decode()
        for name in ('index.html','404.html'):
            page=(PUBLIC/name).read_text()
            for m in re.findall(r'<script>(.*?)</script>',page,re.S): self.assertIn(h(m),csp,name)
            for m in re.findall(r'<style>(.*?)</style>',page,re.S): self.assertIn(h(m),csp,name)
        for need in ["default-src 'none'","frame-ancestors 'none'","object-src 'none'","base-uri 'none'","form-action 'none'","style-src-attr 'unsafe-inline'"]: self.assertIn(need,csp)
        self.assertNotIn('unsafe-eval',csp)
        self.assertNotRegex(re.sub(r"style-src-attr 'unsafe-inline'","",csp),r"unsafe-inline")
        for hdr in ('X-Content-Type-Options: nosniff','Referrer-Policy: no-referrer','Permissions-Policy:','Strict-Transport-Security:'): self.assertIn(hdr,hd)
        self.assertLess(max(len(l) for l in hd.splitlines()),2000)

    def test_17_rebuild_reproducible(self):
        before={f.name:f.read_bytes() for f in PUBLIC.iterdir()};subprocess.run(['python3',str(ROOT/'build.py')],check=True,capture_output=True);self.assertEqual(before,{f.name:f.read_bytes() for f in PUBLIC.iterdir()})

if __name__=='__main__':unittest.main(verbosity=2)
