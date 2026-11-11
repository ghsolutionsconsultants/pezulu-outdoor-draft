"""Patch a fresh Nuuhaven export of the Pezulu draft for phones and hosting.

Run from the repo root after copying a new export over index.html and
site-finder.html:  python3 tools/apply_mobile.py
Safe to re-run: files that are already patched are left alone.
"""
import json, re, sys

MARK = 'pz-mobile'
TPL = re.compile(r'(<script type="__bundler/template">)(.*?)(</script>)', re.S)
META = ('<meta charset="utf-8">\n'
        '  <meta name="robots" content="noindex, nofollow">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">')

HOME_SWAPS = [
    ('<div style="position:fixed;inset:0;overflow:hidden;background:var(--pz-bg',
     '<div class="pz-stage" style="position:fixed;inset:0;overflow:hidden;background:var(--pz-bg'),
    # overflow:clip, not hidden: content spills past the canvas and a hidden
    # box can still be scrolled, which shoved the whole page 340px left.
    ('<div style="position:absolute;left:0;top:0;width:1600px;height:900px;overflow:',
     '<div class="pz-canvas" style="position:absolute;left:0;top:0;width:1600px;height:900px;overflow:'),
    ('width:1600px;height:900px;overflow:hidden;', 'width:1600px;height:900px;overflow:clip;'),
    ('<div style="position:absolute;inset:0;z-index:1;">{{ rail }}',
     '<div class="pz-railbox" style="position:absolute;inset:0;z-index:1;">{{ rail }}'),
    ('<div style="position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient',
     '<div class="pz-fade" style="position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient'),
    ('<header style=', '<header class="pz-head" style='),
    ('alt="Pezulu Outdoor" style="height:44px', 'alt="Pezulu Outdoor" class="pz-logo" style="height:44px'),
    ('<nav style=', '<nav class="pz-nav" style='),
    ('aria-label="Switch theme" style=', 'aria-label="Switch theme" class="pz-theme" style='),
    ('<a href="site-finder.html" style="height:50px;', '<a href="site-finder.html" class="pz-cta" style="height:50px;'),
    ('<h1 style=', '<h1 class="pz-h1" style='),
    ('<div style="position:absolute;left:58px;top:628px;', '<div class="pz-copy" style="position:absolute;left:58px;top:628px;'),
    ('<div style="position:absolute;right:56px;bottom:126px;', '<div class="pz-stats" style="position:absolute;right:56px;bottom:126px;'),
    ('<div style="position:absolute;left:0;right:0;bottom:0;height:98px;', '<div class="pz-marq" style="position:absolute;left:0;right:0;bottom:0;height:98px;'),
    ('<div ref="{{ cursorRef }}" style=', '<div ref="{{ cursorRef }}" class="pz-cursor" style='),
    ("const rail = h('div', { style: { position: 'absolute', left: 640,",
     "const rail = h('div', { className: 'pz-rail', style: { position: 'absolute', left: 640,"),
]

# Home is a 1600x900 canvas scaled to fit the window. On narrow or portrait
# screens that shrinks it to an unreadable strip, so drop the scaling and let
# each block flow in a single column instead.
HOME_CSS = '''<style id="pz-mobile">
@media (max-width: 860px), (max-aspect-ratio: 4/5) {
  body{overflow:auto !important}
  .pz-stage{position:relative !important;inset:auto !important;min-height:100svh;overflow:clip !important}
  .pz-canvas{position:relative !important;width:auto !important;height:auto !important;transform:none !important;display:flex;flex-direction:column;padding:0 20px}
  .pz-head{position:relative !important;left:auto !important;right:auto !important;height:auto !important;flex-wrap:wrap;gap:12px 14px !important;padding:16px 0 0;order:1}
  .pz-logo{height:34px !important}
  .pz-theme > span:first-child{display:none}
  .pz-cta{height:42px !important;padding:0 18px !important;font-size:15px !important}
  .pz-nav{order:5;width:calc(100% + 40px);margin:4px -20px 0 !important;padding:6px 20px 10px;gap:22px !important;font-size:15px !important;overflow-x:auto;white-space:nowrap;scrollbar-width:none;border-bottom:1px solid var(--pz-line)}
  .pz-nav::-webkit-scrollbar{display:none}
  .pz-h1{position:relative !important;left:auto !important;top:auto !important;order:2;margin:28px 0 0 !important;font-size:clamp(46px,14.5vw,84px) !important}
  .pz-copy{position:relative !important;left:auto !important;top:auto !important;width:auto !important;order:3;margin-top:18px}
  .pz-copy p{font-size:17px !important}
  .pz-copy > div{flex-wrap:wrap;margin-top:22px !important}
  .pz-copy a{height:48px !important;padding:0 22px !important;font-size:15px !important}
  .pz-railbox{position:relative !important;inset:auto !important;order:4;height:300px;margin:32px -20px 0;overflow:clip;-webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent)}
  .pz-rail{left:20px !important;top:0 !important;transform:scale(.6);transform-origin:0 0}
  .pz-fade{display:none}
  .pz-stats{position:relative !important;right:auto !important;bottom:auto !important;order:6;flex-wrap:wrap;gap:8px 10px !important;font-size:11px !important;letter-spacing:.14em !important;margin:20px 0 22px}
  .pz-marq{position:relative !important;left:auto !important;right:auto !important;bottom:auto !important;order:7;height:72px !important;margin:0 -20px}
  .pz-marq > div > div > span{font-size:34px !important;gap:20px !important;padding-right:20px !important}
  .pz-cursor{display:none}
}
</style>
'''

# Site finder is a fixed three-column app (provinces | map | site card). Tighten
# it on small laptops and tablets, and stack it on phones: province chips, then
# the map, then the card.
FINDER_CSS = '''<style id="pz-mobile">
@media (min-width: 861px) and (max-width: 1180px) {
  main{grid-template-columns:230px minmax(0,1fr) 360px}
  .search{width:280px}
  .cnt{display:none}
  .prow{font-size:18px;padding:10px 22px}
  #index .h,.legend{margin-left:22px;margin-right:22px;padding:0}
  .code{font-size:26px}
}
@media (max-width: 860px) {
  html,body{height:auto}
  html{overflow:auto}
  body{overflow:visible}
  #app{display:block;height:auto}
  header{position:sticky;top:0;z-index:10;background:#fff;flex-wrap:wrap;gap:10px 12px;padding:10px 16px 12px}
  header img{height:28px}
  .sep{height:22px}
  .ttl{font-size:12px}
  .cnt{display:none}
  .sl{height:40px;font-size:15px;padding:0 6px 0 14px;gap:8px}
  .sl b{min-width:26px;height:26px;font-size:13px}
  .search{order:10;width:100%;height:44px;padding:0 14px}
  .search input{font-size:16px}
  main{display:flex;flex-direction:column}
  #index{border-right:0;border-bottom:1px solid rgba(0,0,0,.1);padding:12px 0}
  #index .h{display:none}
  #rows{display:flex;gap:8px;overflow-x:auto;padding:0 16px 2px;scrollbar-width:none}
  #rows::-webkit-scrollbar{display:none}
  .prow{flex:none;width:auto;padding:8px 14px;font-size:15px;border:1px solid rgba(0,0,0,.14);border-radius:999px;white-space:nowrap;gap:8px}
  .prow.on{border-color:#EE7B22}
  .prow .pd{display:none}
  .prow .n{margin-left:0;font-size:12px}
  .legend{margin-top:12px;padding:0 16px;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px}
  .dot{width:11px;height:11px}
  .note{width:100%;font-size:12px;margin-top:0}
  #map{height:min(58svh,460px);min-height:320px}
  .plab{font-size:10px;letter-spacing:.16em}
  .pin .tl{font-size:13px}
  .zl{left:16px;top:14px;font-size:12px}
  .toast{position:fixed;bottom:18px;z-index:20;font-size:14px}
  #card{border-left:0;border-top:1px solid rgba(0,0,0,.1);padding:18px 16px 28px;gap:14px}
  .code{font-size:24px}
  .town{font-size:16px}
  .specs dt{font-size:11px}
  .specs dd{font-size:17px}
  .btn{height:48px;font-size:15px}
}
</style>
'''

def encode(t):
    return json.dumps(t, ensure_ascii=False).replace('</', '<\\u002F')

def patch(path, fn):
    s = open(path, encoding='utf-8').read()
    m = TPL.search(s)
    raw = m.group(2).strip()
    t = json.loads(raw)
    assert encode(t) == raw, f'{path}: template encoding changed, check the export format'
    if MARK in t:
        print(f'{path}: already patched')
    else:
        t = fn(t)
        g = m.group(2)
        lead, trail = g[:len(g) - len(g.lstrip())], g[len(g.rstrip()):]
        s = s[:m.start(2)] + lead + encode(t) + trail + s[m.end(2):]
        print(f'{path}: patched')
    if 'name="robots"' not in s:
        s = s.replace('<meta charset="utf-8">', META, 1)
    open(path, 'w', encoding='utf-8').write(s)

def home(t):
    for old, new in HOME_SWAPS:
        n = t.count(old)
        if n == 0 and new in t:
            continue
        assert n == 1, f'index.html: expected 1 match, found {n}: {old[:60]}'
        t = t.replace(old, new)
    return t.replace('</helmet>', HOME_CSS + '</helmet>', 1)

def finder(t):
    assert t.count('</head>') == 1
    return t.replace('</head>', FINDER_CSS + '</head>', 1)

patch('index.html', home)
patch('site-finder.html', finder)
