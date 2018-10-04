# coding=utf-8
"""
Specializations of ExtensionResultItem via function wrappers
NOTE: We cannot inherit from ExtensionResultItem, see ExtensionResultItem doc
"""
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction


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
                'type': 'search-enter2',
                'idx': idx_item,
                'uid': note_id
            },
            keep_app_open=True),
        on_alt_enter=ExtensionCustomAction(
            {
                'type': 'imfeelinglucky',
                'idx': idx_item,
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
                'type': 'new-search-and-note',
                'str': search_str,
            },
            keep_app_open=True
        ),
        on_alt_enter=ExtensionCustomAction(
            {
                'type': 'new-note',
                'str': search_str,
            },
            keep_app_open=True
        ),
    )
