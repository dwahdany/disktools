from __future__ import unicode_literals, print_function
import os
import sys
import argparse
from disktools import __version__ as disktools_version
from disktools.disk_usage import get_size, purge_rec_cache


def humanize_bytes(num):
    base = 1024.0
    units = ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    value = float(num)
    for unit in units:
        if value < base or unit == units[-1]:
            if unit == 'B':
                return '%dB' % int(num)
            return '%.1f%s' % (value, unit)
        value /= base


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='duc',
        description='Disk Usage (Cached) [disktools ver. %s]' % disktools_version,
        add_help=False,
    )
    parser.add_argument('path', type=str, help='Get size of specified path.')
    parser.add_argument('--purge', action='store_true', help='Purge and remove all the cache.')
    parser.add_argument('-h', '--human', action='store_true', help='Human-readable output (e.g., 1.1K, 234M)')
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        sys.stderr.write('Path was not found: %s' % args.path)
        sys.exit(1)

    if args.purge is True:
        purge_rec_cache(args.path)
        return

    size = get_size(args.path)
    if args.human:
        print('%s\t%s' % (humanize_bytes(size), args.path))
    else:
        print('%d\t%s' % (size, args.path))


if __name__ == '__main__':
    main()

