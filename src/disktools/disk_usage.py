from __future__ import unicode_literals, print_function
import sys
import os
import bson
import stat
import shutil

# Fix utf-8 bugs.
reload(sys)
sys.setdefaultencoding('utf-8')


HIDDEN = '.duc'  # stands for 'disk usage cache'


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
    cache['folder_sizes'] = bson.loads(open(cache_path).read())
    cache['last_modified'] = os.path.getmtime(cache_path)
    return cache


def save_cache(folder_path, folder_sizes):
    '''
    Cache is written into .duc folder. The size of the folder is filled
    using a file called blob. The size of the file pads folder disk size
    in bytes to be dividable by a dev block size. This allows for `duc` to
    report the same size as `du`.
    '''
    cache_path = get_cache_path(folder_path)
    cache_dir_path = os.path.dirname(cache_path)
    cache_blob_path = os.path.join(cache_dir_path, 'blob')
    if not os.path.exists(cache_dir_path):
        os.makedirs(cache_dir_path)
    # Touch the blob file.
    open(cache_blob_path, 'w+').close()
    block_size = os.stat(cache_blob_path).st_blksize
    # Size of the FAT of the folder plus rounded up data size
    cache_data = bson.dumps(folder_sizes)
    delta = block_size - len(cache_data) % block_size
    ceiled_cache_size = os.path.getsize(cache_dir_path) \
        + len(cache_data) + delta
    folder_sizes[HIDDEN] = ceiled_cache_size
    with open(cache_path, 'w+') as output:
        output.write(bson.dumps(folder_sizes))
    with open(cache_blob_path, 'w+') as blob:
        blob.write('0' * delta)


def purge_cache(path):
    # print path
    sub_folders = [folder for folder in os.listdir(path)
                   if os.path.isdir(os.path.join(path, folder))
                   and folder != HIDDEN]
    for sub_folder in sub_folders:
        sub_path = os.path.join(path, sub_folder)
        purge_cache(sub_path)
        cache_folder_path = os.path.dirname(get_cache_path(path))
        if os.path.exists(cache_folder_path):
            print('Purging: %s' % sub_path)
            assert cache_folder_path.endswith(HIDDEN)
            shutil.rmtree(cache_folder_path)


def get_size(path, cached=True, seen_hardlinks=None):
    assert os.path.isdir(path)
    size = os.path.getsize(path)
    if seen_hardlinks is None:
        seen_hardlinks = list()
    entries = [unicode(entry_name) for entry_name in os.listdir(path)]
    folder_sizes = dict()
    cache = load_cache(path)
    # wow = u'\u0418\u0433\u0440\u0430 \u043f\u0440\u0435\u0441\u0442\u043e\u043b\u043e\u0432 Soundtrack'
    # print(cache['folder_sizes'])
    # print(entries)
    # assert wow in cache['folder_sizes']
    for entry_name in entries:
        entry_path = os.path.join(path, entry_name)
        attributes = os.stat(entry_path)
        # Sum if os.path.isdir(size of linked files only once.
        if attributes.st_nlink > 0:
            if attributes.st_ino not in seen_hardlinks:
                seen_hardlinks.append(attributes.st_ino)
            else:
                continue
        # Sum size on entries.
        # if os.path.isdir(entry_path):
        if stat.S_ISDIR(attributes.st_mode):
            # Deep first get_size recursion for folders.
            if cached and (entry_name not in cache['folder_sizes']
                           or attributes.st_ctime > cache['last_modified']):
                # Learn size recursively.
                folder_size = get_size(entry_path,
                                       seen_hardlinks=seen_hardlinks)
            else:
                folder_size = cache['folder_sizes'][entry_name]
            folder_sizes[entry_name] = folder_size
            size += folder_size
        else:
            # Simply sum the file size.
            size += attributes.st_size
    # Cache learned result on disk.
    if not path.endswith(HIDDEN):
        # Don't cache the cache.
        save_cache(path, folder_sizes)
    return size
