import argparse
import os

from path import Path

os.environ['LIBARCHIVE'] = Path(__file__).parent / 'archive.dll'

# isort: split
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import libarchive
from tqdm import tqdm

REGULAR_FILE = libarchive.entry.FileType.REGULAR_FILE


# convert from 7z to zip or fix github zip Overlapped Entries exception
# deflate is smaller for small files compared to zstd https://github.com/facebook/zstd/issues/1134
def convert_archive(file, output_dir, cut_prefix=0):
    file = Path(file)
    if output_dir == '.' and file.suffix == '.zip':
        output_file = Path(output_dir) / (file.stem + '-converted.zip')
    else:
        output_file = Path(output_dir) / (file.stem + '.zip')
    assert not os.path.exists(output_file)

    with tqdm(total=os.path.getsize(file), unit='bytes') as pb:
        with libarchive.file_reader(file) as ar, ZipFile(output_file, 'w', ZIP_DEFLATED) as zf:
            for entry in ar:
                if entry.filetype == REGULAR_FILE:
                    path = entry.pathname
                    buf = BytesIO()
                    for block in entry.get_blocks():
                        buf.write(block)

                    if cut_prefix:
                        for _ in range(cut_prefix):
                            path = path[path.index('/') + 1 :]

                    zf.writestr(path, buf.getvalue())
                    pb.update(ar.bytes_read - pb.n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='Output directory', default='.')
    parser.add_argument('-c', '--cut', type=int, help='Cut n number of prefix directory', default=0)
    parser.add_argument('input', nargs=1)
    args = parser.parse_args()

    convert_archive(args.input[0], args.directory, args.cut)


if __name__ == '__main__':
    main()
