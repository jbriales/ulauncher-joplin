# coding=utf-8
"""
Specializations of ExtensionResultItem via function wrappers
NOTE: We cannot inherit from ExtensionResultItem, see ExtensionResultItem doc
"""
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from responses import *
from history import RecentHistory


def create_note_item(note, idx_item):
    """
    Create item linking to a database note
    :param note:
    :param idx_item:
    :return:
    """
    # HACK: Using note from Notes or FTS table
    if 'id' in note:
        note_id = note['id']
    elif 'uid' in note:
        note_id = note['uid']
    else:
        raise Exception

    return ExtensionSmallResultItem(
        icon='images/joplin.png',
        name=note['title'],
        # description=note['body'],
        on_enter=ExtensionCustomAction(
            {
                'func': open_note_edition_action,
                'uid': note_id
            },
            keep_app_open=True),
        on_alt_enter=ExtensionCustomAction(
            {
                'func': imfeelinglucky_action,
                'uid': note_id
            },
            keep_app_open=True),
    )


def create_search_item(search_str):
    """
    Create item linking to a new search action
    :param search_str:
    :return:
    """
    return ExtensionSmallResultItem(
        icon='images/note-chrome-add-64.png',
        name='New search note: %s' % search_str,
        on_enter=ExtensionCustomAction(
            {
                'func': open_new_search_and_note_action,
                'str_search': search_str,
            },
            keep_app_open=True
        ),
        on_alt_enter=ExtensionCustomAction(
            {
                'func': open_new_note_action,
                'str_search': search_str,
            },
            keep_app_open=True
        ),
    )


def create_default_items_list(history_uids, do_history_clean=True):
    items = list()

    # Find notes for ids in history
    notes = pyjoplin.get_notes_by_id(history_uids[::-1], ordered=True)
    if do_history_clean:
        # Remove any not found history uids
        found_uids = [note['id'] for note in notes]
        notfound_uids = set(history_uids) - set(found_uids)
        for notfound_uid in notfound_uids:
            # NOTE: Use that argument is passed by reference to fix in place
            history_uids.remove(notfound_uid)

    # Add entries from recent history
    for note in notes:
        idx_item = len(items)
        item = create_note_item(note, idx_item)
        items.append(item)

    # Create last entry with instructions
    items.append(
        ExtensionSmallResultItem(
            icon='images/search.png',
            name='Or write search query ended with space...'
        )
    )

    return items
