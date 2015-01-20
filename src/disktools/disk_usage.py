import os
import bson
from findtools.find_files import (find_files, Match, mkpathname)


HIDDEN = '.duc'  # stands for 'disk usage cache'
folder_pattern = Match(filetype='d', name=r'/^\.%s/' % HIDDEN)
file_pattern = Match(filetype='f')


def get_cache_path(folder_path):
    return os.path.join(folder_path, HIDDEN, 'du.cache')


def get_cache_mtime(folder_path):
    cache_path = get_cache_path(folder_path)
    return os.path.getmtime(cache_path)


def load_cache(folder_path):
    # Start with empty cache.
    cache = {'folder_sizes': dict()}
    cache_path = get_cache_path(folder_path)
    # Check if any previous values have been kept.
    if not os.path.exists(cache_path):
        return cache
    cache['last_modified'] = os.path.getmtime(cache_path)
    cache['folder_sizes'] = bson.loads(open(cache_path).read())
    return cache


def save_cache(folder_path, folder_sizes):
    cache_path = get_cache_path(folder_path)
    os.makedirs(os.path.dirname(cache_path))
    with open(cache_path, 'w+') as output:
        output.write(bson.dumps(folder_sizes))


def collect_size(root, name):
    pathname = mkpathname(root, name)
    filesize = os.path.getsize(pathname)
    return (pathname, filesize)


def get_size(path, cached=True):
    size = 0
    # Find size of all files in this folder.
    inside_files = find_files(path=path, match=file_pattern)
    for inside_file in inside_files:
        size += os.path.getsize(inside_file)
    # Sum it up with the size of subfolders.
    sub_folders = find_files(path=path, match=folder_pattern)
    folder_sizes = {'folder_sizes': dict()}
    cache = load_cache(path)
    for sub_folder in sub_folders:
        folder_mtime = os.path.getmtime(sub_folder)
        if sub_folder not in cache['folder_sizes'] \
                or folder_mtime > cache['last_modified']:
            # Learn size recursively.
            folder_size = get_size(sub_folder)
        else:
            folder_size = cache['folder_sizes'][sub_folder]
        folder_sizes[sub_folder] = folder_size
        size += folder_size
    # Update cache.
    save_cache(path, folder_sizes)
    return size
