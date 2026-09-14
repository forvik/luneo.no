"""Bygger luneo.no (nb + en) og den enkeltstående presentasjonen (artifact).

Kilder:  style.css, body.nb.html, body.en.html, white.webp/dark.webp, site/img/bakgrunn.*
Ut:      site/  (index.html, personvern.html, kjopsvilkar.html, en/index.html, en/privacy.html, en/terms.html, img/, favicon.svg)
         luneo-presentasjon.html (én fil med begge språk og hash-ruting)
"""
import os, re, base64, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, 'site')
STYLE = open(os.path.join(HERE, 'style.css'), encoding='utf-8').read()
BODY = {
    'nb': open(os.path.join(HERE, 'body.nb.html'), encoding='utf-8').read(),
    'en': open(os.path.join(HERE, 'body.en.html'), encoding='utf-8').read(),
}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@500;700;800&family=Mulish:wght@400;600;700&display=swap">')

META = {
    'nb': {
        'index': ('Luneo – Booking gjort enkelt',
                  'Luneo er bookingsystemet for norske aktivitetssentre – bowling, laserspill, escape room, gokart og trampolinepark. Fast lav månedspris, ingen prosent av salget. Test gratis i 3 måneder.'),
        'personvern': ('Personvern – Luneo', 'Personvernerklæring for bookingsystemet Luneo og luneo.no.'),
        'kjopsvilkar': ('Kjøpsvilkår – Luneo', 'Kjøpsvilkår for bedriftskunder av bookingsystemet Luneo.'),
    },
    'en': {
        'index': ('Luneo – Booking made simple',
                  'Luneo is the booking system for activity centres – bowling, laser tag, escape rooms, go-karts and trampoline parks. One fixed low monthly price, no percentage of your sales. Free 3-month trial.'),
        'privacy': ('Privacy – Luneo', 'Privacy policy for the Luneo booking system and luneo.no.'),
        'terms': ('Terms of purchase – Luneo', 'Terms of purchase for business customers of the Luneo booking system.'),
    },
}
# side-par på tvers av språk (for flaggene og hreflang)
PAIR = {'index': 'index', 'personvern': 'privacy', 'kjopsvilkar': 'terms'}
URL = {  # sti relativt til roten
    ('nb', 'index'): '', ('nb', 'personvern'): 'personvern.html', ('nb', 'kjopsvilkar'): 'kjopsvilkar.html',
    ('en', 'index'): 'en/', ('en', 'privacy'): 'en/privacy.html', ('en', 'terms'): 'en/terms.html',
}

def split(body):
    """Deler en body i header, main, legal-seksjoner (dict id->html), footer, script."""
    header = body[body.index('<header class="top">'):body.index('<main ')]
    main = body[body.index('<main '):body.index('</main>') + len('</main>')]
    legal_html = body[body.index('</main>') + len('</main>'):body.index('<footer>')]
    legal = {}
    for m in re.finditer(r'<section class="legal" id="([^"]+)".*?</section>', legal_html, re.S):
        legal[m.group(1)] = m.group(0)
    footer = body[body.index('<footer>'):body.index('<script>')]
    script = body[body.index('<script>'):]
    return header, main, legal, footer, script

def doc(lang, title, desc, body, path, alt_nb, alt_en, prefix):
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://luneo.no/{path}">
<link rel="alternate" hreflang="nb" href="https://luneo.no/{alt_nb}">
<link rel="alternate" hreflang="en" href="https://luneo.no/{alt_en}">
<link rel="alternate" hreflang="x-default" href="https://luneo.no/{alt_nb}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://luneo.no/{path}">
<meta property="og:locale" content="{'nb_NO' if lang == 'nb' else 'en_GB'}">
<meta name="theme-color" content="#1B222D">
<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
{FONTS}
<style>
{STYLE}</style>
</head>
<body>
{body}
</body>
</html>
'''

SHOTS = ('SHOT_LASER', 'laser.webp'), ('SHOT_CURLING', 'curling.webp'), ('SHOT_GOKART', 'gokart.webp')

def assets(s, prefix):
    s = (s.replace('LOGO_WHITE', prefix + 'img/luneo-logo-hvit.webp')
          .replace('VIDEO_SRC', prefix + 'img/bakgrunn.mp4')
          .replace('POSTER_SRC', prefix + 'img/bakgrunn.jpg'))
    for key, f in SHOTS:
        s = s.replace(key, prefix + 'img/' + f)
    return s

def build_site():
    os.makedirs(os.path.join(SITE, 'en'), exist_ok=True)
    os.makedirs(os.path.join(SITE, 'img'), exist_ok=True)
    for lang in ('nb', 'en'):
        header, main, legal, footer, script = split(BODY[lang])
        prefix = '' if lang == 'nb' else '../'
        other = 'en' if lang == 'nb' else 'nb'
        pages = ['index'] + list(legal.keys())
        for page in pages:
            # motsvarende side på det andre språket
            pair = PAIR[page] if lang == 'nb' else {v: k for k, v in PAIR.items()}[page]
            nb_key, en_key = (page, pair) if lang == 'nb' else (pair, page)
            url_nb, url_en = URL[('nb', nb_key)], URL[('en', en_key)]
            if lang == 'nb':
                href_nb = url_nb or 'index.html'          # egen side
                href_en = url_en                          # 'en/' eller 'en/privacy.html'
            else:
                href_nb = '../' + url_nb                  # '../' eller '../personvern.html'
                href_en = url_en.replace('en/', '') or 'index.html'
            title, desc = META[lang][page]
            legal_hrefs = {k: (k + '.html') for k in legal}  # #personvern -> personvern.html
            h = header
            if page != 'index':
                h = h.replace('href="#top"', 'href="index.html"').replace('href="#topp"', 'href="index.html"')
                h = re.sub(r'href="#(bransjen|produktet|demo|pris|igang|kontakt|industry|product|pricing|get-started|contact)"', r'href="index.html#\1"', h)
            h = h.replace('LANG_NB_HREF', href_nb).replace('LANG_EN_HREF', href_en)
            if page == 'index':
                body = h + main + footer + script
            else:
                sec = legal[page].replace(' hidden>', '>', 1).replace('href="#topp"', 'href="index.html"').replace('href="#top"', 'href="index.html"')
                body = h + sec + footer
            for k, v in legal_hrefs.items():
                body = body.replace(f'href="#{k}"', f'href="{v}"')
            body = assets(body, prefix)
            fname = 'index.html' if page == 'index' else page + '.html'
            out = os.path.join(SITE, fname) if lang == 'nb' else os.path.join(SITE, 'en', fname)
            path = URL[(lang, page)]
            open(out, 'w', encoding='utf-8').write(doc(lang, title, desc, body, path, url_nb, url_en, prefix))

    shutil.copy(os.path.join(HERE, 'white.webp'), os.path.join(SITE, 'img', 'luneo-logo-hvit.webp'))
    shutil.copy(os.path.join(HERE, 'dark.webp'), os.path.join(SITE, 'img', 'luneo-logo-svart.webp'))
    open(os.path.join(SITE, 'favicon.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="14" fill="#C010C5"/>'
        '<path d="M20 14h10v26h16v10H20z" fill="#fff"/></svg>')
    # README-en og _headers skrives IKKE lenger.
    #
    # De sto her, og den dokumenterte arbeidsgangen er «kopier innholdet i
    # site/ til roten». Da overskrev byggingen repoets egen README – som
    # forklarer nettopp denne arbeidsgangen – med en kortere stubb, hver
    # eneste gang noen bygget. Begge to hører til repoet og ikke til
    # byggeresultatet.
    open(os.path.join(SITE, '_headers'), 'w', encoding='utf-8').write(
        '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')

def build_artifact():
    def b64(path, mime):
        return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    logo = b64(os.path.join(HERE, 'white.webp'), 'image/webp')
    shots = {k: b64(os.path.join(SITE, 'img', f), 'image/webp') for k, f in SHOTS}
    video = b64(os.path.join(SITE, 'img', 'bakgrunn.mp4'), 'video/mp4')
    poster = b64(os.path.join(SITE, 'img', 'bakgrunn.jpg'), 'image/jpeg')

    def prep(lang):
        s = BODY[lang]
        if lang == 'en':  # unike id-er når begge språk ligger i samme dokument
            s = re.sub(r'id="([^"]+)"', r'id="\1-en"', s)
            s = re.sub(r'href="#([^"]+)"', r'href="#\1-en"', s)
            s = re.sub(r'for="([^"]+)"', r'for="\1-en"', s)
            s = re.sub(r"\$\('#([a-z-]+)'\)", r"$('#\1-en')", s)
        s = s.replace('LANG_NB_HREF', '#nb').replace('LANG_EN_HREF', '#en')
        s = s.replace('LOGO_WHITE', logo).replace('VIDEO_SRC', video).replace('POSTER_SRC', poster)
        for k, v in shots.items():
            s = s.replace(k, v)
        return s

    toggle = '''<script>
(function(){
  var wraps = document.querySelectorAll('[data-lang]');
  function setLang(l){
    for (var i = 0; i < wraps.length; i++){ wraps[i].hidden = (wraps[i].getAttribute('data-lang') !== l); }
    document.documentElement.lang = l;
    var m = document.querySelector('[data-lang="' + l + '"] main');
    if (m && !location.hash) document.title = m.getAttribute('data-title') || document.title;
  }
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('.lang a[lang]');
    if (!a) return;
    e.preventDefault();
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    setLang(a.getAttribute('lang'));
    window.dispatchEvent(new HashChangeEvent('hashchange'));
    window.scrollTo(0, 0);
  });
  setLang('nb');
})();
</script>'''
    html = ('<title>Luneo</title>\n' + FONTS + '\n<style>\n' + STYLE + '</style>\n'
            + '<div data-lang="nb">\n' + prep('nb') + '\n</div>\n'
            + '<div data-lang="en" hidden>\n' + prep('en') + '\n</div>\n' + toggle + '\n')
    open(os.path.join(HERE, 'luneo-presentasjon.html'), 'w', encoding='utf-8').write(html)

build_site()
build_artifact()
print('built:', sorted(os.listdir(SITE)), sorted(os.listdir(os.path.join(SITE, 'en'))))
