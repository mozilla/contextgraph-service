import os
import shutil
import sys

import hydra


def create(in_filename, out_filename, archive_path, tmp_path):
    out_filepath = os.path.join(tmp_path, out_filename)

    lines = []
    with open(in_filename, 'rt', encoding='utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line:
                lines.append(line)

    with hydra.WritingBloomFilter(len(lines), 0.001, out_filepath) as bf:
        for line in lines:
            bf[(line.encode('utf-8'))] = 0

    # Create a tar archive in /tmp/block.dat.tar
    shutil.make_archive(archive_path, 'tar', tmp_path)


def main(in_filename, base='/tmp'):
    # Convert from data/block.txt to block.dat
    out_filename = '.'.join(
        os.path.splitext(os.path.basename(in_filename))[:-1] + ('dat', ))

    archive_path = os.path.join(base, 'output')
    try:
        tmp_path = os.path.join(base, 'archive')
        os.makedirs(tmp_path)
        create(in_filename, out_filename, archive_path, tmp_path)
    finally:
        shutil.rmtree(tmp_path)


def console_entry():  # pragma: no cover
    argv = sys.argv
    in_filename = argv[1]
    main(in_filename)