import orjson as json
from lxml import html
from path import Path


def convert(source):
    with source.open(encoding='latin1') as f:
        tree = html.fromstring(f.read())

    symbols = []
    locations = []
    keys = set()
    try:
        for li in tree.xpath('//li'):
            symbol = li.find('object/param[@name="Name"]').get('value')
            location = li.find('object/param[@name="Local"]').get('value')
            key = f'{symbol}|{location}'
            if key not in keys:
                symbols.append(symbol)
                locations.append(location)
                keys.add(key)
    except AttributeError:
        print(html.tostring(li))
        raise

    with open('index.json', 'wb') as f:
        f.write(json.dumps([symbols, locations]))


def main():
    for file in Path('.').files('*.hhk'):
        convert(file)


if __name__ == '__main__':
    main()
