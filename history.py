# coding=utf-8
"""
Handle history of visited items
"""
import errno
import os

PATH_TEMP = '/tmp/ulauncher-joplin'
try:
    os.makedirs(PATH_TEMP)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(PATH_TEMP):
        pass
    else:
        raise

PATH_CACHE = os.path.expanduser('~/.cache/ulauncher-joplin')
try:
    os.makedirs(PATH_CACHE)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(PATH_CACHE):
        pass
    else:
        raise

PATH_HISTORY = os.path.join(PATH_CACHE, 'history')
if not os.path.exists(PATH_HISTORY):
    # Ensure history file exists (even if empty)
    with open(PATH_HISTORY, 'w') as f:
        f.write('')


class RecentHistory(list):

    def __init__(self):
        # Load previous history from file
        with open(PATH_HISTORY, 'r') as f:
            super(RecentHistory, self).__init__(f.read().splitlines())

    def save(self):
        # Save current content into file
        with open(PATH_HISTORY, 'w') as f:
            for uid in self:
                f.write(uid + '\n')

    def append(self, uid):
        """ Same as list.append(val),
        but ensures no repeated values by removing if existing
        """
        # Avoid repetitions of uid
        if uid in self:
            self.remove(uid)
        # TODO: Turn this into preference option
        MAX_NUM_ENTRIES = 15
        if len(self) >= MAX_NUM_ENTRIES:
            # TODO: Better use deque
            self.pop(0)
        super(RecentHistory, self).append(uid)
        # Make backup for safety
        self.save()

    def __del__(self):
        self.save()
        print("DELETING HISTORY OBJECT")
        super(RecentHistory, self).__del__()
