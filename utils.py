from contextlib import contextmanager
from time import perf_counter

import colorama
import orjson as json
from selectolax.parser import HTMLParser

from . import Qt, qt


def shortcut(parent, key):
    s = qt.QShortcut(qt.QKeySequence(key), parent)
    s.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
    return s


def shortcuts(parent, keys):
    for key, handler in keys.items():
        shortcut(parent, key).activated.connect(handler)


def fix_html(html):
    tree = HTMLParser(html)
    for link in tree.css('link'):
        # crossorigin in <link rel="preload" as="font" type="font/woff2" crossorigin causes the font file not to be useable
        attrs = link.attrs
        if 'crossorigin' in attrs:
            del attrs['crossorigin']

    return tree.html


def extract_genindex(html):
    tree = HTMLParser(html)
    symbols = []
    locations = []
    for table in tree.tags('table'):
        for li in table.css('td > ul > li'):
            a = li.css_first('a')
            text = a.text()
            # assert text[0] != '(', li.parent.parent.tag
            symbol = text.split(' (', 1)[0]
            symbols.append(text)
            locations.append(a.attributes['href'])
            if ul := li.css_first('ul'):
                for a in ul.css('a'):
                    symbols.append(symbol + ' ' + a.text())
                    locations.append(a.attributes['href'])
    return symbols, locations


def extract_searchindex(content):
    if not content.startswith(b'Search.setIndex'):
        return

    try:
        data = json.loads(content[16:-1])
    except Exception as err:
        print(content)
        raise err
    symbols = []
    locations = []

    try:
        docnames = data['docnames']
        add_html = True
    except KeyError:
        docnames = data['docurls']
        add_html = False

    for k, v in data['indexentries'].items():
        if len(v) == 1:
            symbols.append(k)
            url = docnames[v[0][0]]
            if add_html:
                url += '.html'
            if hash := v[0][1]:
                url += f'#{hash}'
            locations.append(url)

    if not symbols:
        return None

    return symbols, locations


@contextmanager
def timeit(*args):
    t = perf_counter()
    yield
    if args:
        if not args[0]:
            return
        print(colorama.Fore.BLUE + ' '.join(args) + ': ' + colorama.Fore.RESET, end='')
    print(perf_counter() - t)
