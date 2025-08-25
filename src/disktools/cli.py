from __future__ import unicode_literals, print_function
import os
import sys
import argparse
from disktools import __version__ as disktools_version
from disktools.disk_usage import get_size, purge_rec_cache


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='duc',
        description='Disk Usage (Cached) [disktools ver. %s]' % disktools_version,
    )
    parser.add_argument('path', type=str, help='Get size of specified path.')
    parser.add_argument('--purge', action='store_true', help='Purge and remove all the cache.')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        sys.stderr.write('Path was not found: %s' % args.path)
        sys.exit(1)

    if args.purge is True:
        purge_rec_cache(args.path)
        return

    size = get_size(args.path)
    print('%d\t%s' % (size, args.path))


if __name__ == '__main__':
    main()

