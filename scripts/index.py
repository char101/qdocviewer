import os
from collections import defaultdict
from operator import itemgetter

import orjson as json
from lxml import etree
from path import Path


class Index:
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.locations = []

    def __setitem__(self, key, value):
        self.symbols.append(key)
        self.locations.append(value)

    def __len__(self):
        return len(self.symbols)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            with open('index.json', 'wb') as f:
                f.write(json.dumps((self.symbols, self.locations)))


def process_qt():
    symbols_map = {}
    name_count = defaultdict(lambda: 0)
    with Index() as ind:
        for dir in Path('.').dirs():
            for file in dir.files('*.qhp'):
                print(file)
                with file.open(encoding='utf-8') as f:
                    tree = etree.parse(f)
                    if index := tree.xpath('//keywords'):
                        for kw in index[0].findall('keyword'):
                            name = kw.get('name')
                            name_count[name] += 1

                            id = kw.get('id')

                            ref = kw.get('ref')
                            if not ref:
                                continue
                            location = dir.name + '/' + ref

                            name = f'{id} ({ref})'

                            if name in symbols_map:
                                if symbols_map[name][0] == ref:
                                    continue

                            assert name not in symbols_map, f'duplicate: {name} {symbols_map[name]} {(ref, file)}'
                            ind[name] = location
                            symbols_map[name] = (ref, file)

    print(f'{len(ind)} symbols')

    name_count = [(name, count) for name, count in name_count.items()]
    name_count.sort(key=itemgetter(1), reverse=True)
    for i in range(10):
        print(name_count[i])


def process_typedoc():
    with Index() as ind:
        for file in Path('.').walkfiles():
            if file.suffix == '.html':
                if file.stem in ('index', 'hierarchy'):
                    continue
                symbol = file.stem.split('.')[-1]
                ind[symbol] = file[2:].replace(os.sep, '/')


def process_vim():
    with Index() as ind:
        with open('tags.json') as f:
            for k, v in json.loads(f.read()).items():
                ind[k] = v


def process_postgres():
    from selectolax.parser import HTMLParser

    def itertag(parent, tag):
        return [node for node in parent.iter() if node.tag == tag]

    with Index() as ind:
        with open('bookindex.html', encoding='utf-8') as f:
            html = HTMLParser(f.read())
        for indexdiv in html.css('.indexdiv'):
            for dl in itertag(indexdiv, 'dl'):
                for dt in itertag(dl, 'dt'):
                    term = dt.text(deep=False).rstrip(', ')
                    if term:
                        for a in dt.css('a'):
                            sym = f'{term} ({a.text().strip()})' if a.text().strip() != term else term
                            print('- ' + sym)
                            loc = a.attributes['href']
                            ind[sym] = loc
                    if dt.next and dt.next.tag == 'dd':
                        for dl in itertag(dt.next, 'dl'):
                            for dt in itertag(dl, 'dt'):
                                subterm = dt.text(deep=False).rstrip(', ')
                                text = f'{term} - {subterm}'
                                for a in dt.css('a'):
                                    if a.text().strip() != subterm:
                                        text += ' (' + a.text().strip() + ')'
                                    sym = text
                                    print('-   ' + sym)
                                    loc = a.attributes['href']
                                    ind[sym] = loc


def get_doc_type():
    if os.path.exists('qtcore'):
        return 'qt'
    if os.path.exists('index.html'):
        with open('index.html', encoding='utf-8') as f:
            if 'typedoc' in f.read():
                return 'typedoc'
    if os.path.exists('tags.json') and os.path.exists('gui_w32.txt.html'):
        return 'vim'
    if os.path.exists('postgres-user.html'):
        return 'postgres'


def main():
    doctype = get_doc_type()
    print(doctype)
    globals()[f'process_{doctype}']()


if __name__ == '__main__':
    main()
