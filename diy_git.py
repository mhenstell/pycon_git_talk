#!/bin/python3
"""Testing creating a git repo by hand."""

import os
import hashlib
import zlib
import time

NORMAL_FILE = "100644"
ME = "Max Henstell <max@kapamaki.net>"
TIMEZONE = "-0700"


def git_init():
    """Initialize a barebones .git folder."""
    os.mkdir('.git')
    os.makedirs('.git/objects/info')
    os.makedirs('.git/objects/pack')
    os.makedirs('.git/refs/heads')
    os.makedirs('.git/refs/tags')

    with open('.git/HEAD', 'w') as head:
        head.write('ref: refs/heads/master')

def write_git_object(contents):
    """Hash a string, write it to a file, and return the hash."""
    sha1_hash = hashlib.sha1(contents)
    sha1_hex = sha1_hash.hexdigest()

    os.mkdir(os.path.join('.git', 'objects', sha1_hex[0:2]))

    with open(os.path.join('.git', 'objects', sha1_hex[0:2], sha1_hex[2:]), 'wb') as git_object:
        git_object.write(zlib.compress(bytes(contents), level=1))

    return sha1_hash

def create_blob():
    """Create a blob object from this file and write it to our .git folder."""
    file_size = os.path.getsize(__file__)

    with open(__file__) as this_file:
        contents = this_file.read()
        blob_contents = 'blob %s\0%s' % (file_size, contents)
        sha1_hash = write_git_object(bytes(blob_contents, encoding='utf-8'))
        print("Wrote blob: %s" % sha1_hash.hexdigest())

        return sha1_hash


def create_tree(sha1_hash):
    """Create a tree object from a blob's hash and write it to our .git folder."""
    tree_entry = '%s %s' % (NORMAL_FILE, __file__)
    tree_entry = bytes(tree_entry, encoding='utf-8') + b'\0' + sha1_hash.digest()
    tree_contents = bytes('tree %s' % len(tree_entry), encoding='utf-8') + b'\0' + tree_entry

    tree_hash = write_git_object(tree_contents)
    print("Wrote tree: %s" % tree_contents)
    print("Wrote tree: %s" % tree_hash.hexdigest())
    print("len %s" % len(tree_contents))
    return tree_hash

def create_commit(sha1_hash):
    """Create a commit object from a tree's hash and write it to our .git folder."""
    timestamp = int(time.time())
    author_line = "author %s %s %s" % (ME, timestamp, TIMEZONE)
    committer_line = "committer %s %s %s" % (ME, timestamp, TIMEZONE)
    commit_message = "test"

    commit_entry = 'tree %s\n%s\n%s\n\n%s\n' % (sha1_hash.hexdigest(),
                                                author_line, committer_line,
                                                commit_message)
    commit_contents = bytes('commit %s' % len(commit_entry),
                            encoding='utf-8') + b'\0' + \
                            bytes(commit_entry, encoding='utf-8')
    commit_hash = write_git_object(commit_contents)

    print("Wrote commit: %s" % commit_contents)
    print("Wrote commit: %s" % commit_hash.hexdigest())
    return commit_hash

def run():
    """Entry point."""
    git_init()

    blob_hash = create_blob()
    tree_hash = create_tree(blob_hash)
    commit_hash = create_commit(tree_hash)
    print("Created commit hash: %s" % commit_hash.hexdigest())

if __name__ == "__main__":
    run()
