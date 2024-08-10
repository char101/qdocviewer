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


def get_doc_type():
    if os.path.exists('qtcore'):
        return 'qt'
    if os.path.exists('index.html'):
        with open('index.html', encoding='utf-8') as f:
            if 'typedoc' in f.read():
                return 'typedoc'


def main():
    doctype = get_doc_type()
    print(doctype)
    globals()[f'process_{doctype}']()


if __name__ == '__main__':
    main()
