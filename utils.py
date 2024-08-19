from contextlib import contextmanager
from time import perf_counter
from urllib.parse import urljoin

import colorama
import lxml.html
import orjson as json
import polars as pl
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


def epoch():
    from time import time

    return int(time())


def extract_genindex(html, base_url='/'):
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
            locations.append(urljoin(base_url, a.attributes['href']))
            if ul := li.css_first('ul'):
                for a in ul.css('a'):
                    symbols.append(symbol + ' ' + a.text())
                    locations.append(urljoin(base_url, a.attributes['href']))
    return pl.DataFrame({'symbol': symbols, 'location': locations})


def extract_searchindex(content, base_url='/'):
    if not content.startswith(b'Search.setIndex'):
        return

    symbols = []
    locations = []

    try:
        data = json.loads(content[16:-1])
    except Exception as err:
        print(content)
        raise err

    # locations
    try:
        docnames = data['docnames']
        add_html = True
    except KeyError:
        docnames = data['docurls']
        add_html = False

    # symbols
    indexentries = data['indexentries']
    titles = data['titles']
    if len(indexentries) > len(titles):
        for k, v in indexentries.items():
            if len(v) > 0:
                v = v[0]
                url = docnames[v[0]]
                if add_html:
                    url += '.html'
                if hash := v[1]:
                    url += f'#{hash}'
                symbols.append(k)
                locations.append(urljoin(base_url, url))
    else:
        for i, symbol in enumerate(titles):
            url = docnames[i]
            symbols.append(symbol)
            locations.append(urljoin(base_url, url))

    if not symbols:
        return None

    return pl.DataFrame({'symbol': symbols, 'location': locations})


def extract_hhk(content):
    tree = lxml.html.fromstring(content)

    symbols = []
    locations = []
    try:
        for li in tree.xpath('//li'):
            symbol = li.find('object/param[@name="Name"]').get('value')
            location = li.find('object/param[@name="Local"]').get('value')
            symbols.append(symbol)
            locations.append(location)
        return pl.DataFrame(dict(symbol=symbols, location=locations))
    except AttributeError:
        print(lxml.html.tostring(li))
        raise


@contextmanager
def timeit(*args):
    t = perf_counter()
    yield
    if args:
        if not args[0]:
            return
        print(colorama.Fore.BLUE + ' '.join(args) + ': ' + colorama.Fore.RESET, end='')
    print(perf_counter() - t)
