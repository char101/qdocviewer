import orjson as json
from lxml import html
from path import Path


def convert(source):
    with source.open(encoding='latin1') as f:
        tree = html.fromstring(f.read())

    symbols = []
    locations = []
    try:
        for li in tree.xpath('//li'):
            symbol = li.find('object/param[@name="Name"]').get('value')
            location = li.find('object/param[@name="Local"]').get('value')
            symbols.append(symbol)
            locations.append(location)
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
