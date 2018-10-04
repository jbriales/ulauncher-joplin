# coding=utf-8
import subprocess
import webbrowser

from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

import pyjoplin

# def show_note_details_action(list_items, name_item):
#     # Make chosen entry detailed
#     idx_item = data['idx']
#     item = extension.items[idx_item]
#     # Substitute this entry by detailed one
#     detailed_item = ExtensionResultItem(
#         icon='images/joplin.png',
#         name=item.get_name(),
#         description=item.get_description(None),
#         on_enter=ExtensionCustomAction(
#             {
#                 'type': 'search-enter2',
#                 'idx': idx_item,
#                 'uid': data['uid']
#             },
#             keep_app_open=True),
#     )
#     extension.items[idx_item] = detailed_item
#
#     # Ensure all other entries are small
#     # TODO
#
#     return None, RenderResultListAction(extension.items)


def open_note_edition_action(uid):
    # Edit chosen note
    print("Opening note edition")
    cmd = 'pyjoplin edit %s' % uid
    proc = subprocess.Popen(cmd, shell=True)
    return uid, HideWindowAction()


def imfeelinglucky_action(uid):
    # Try to get solution code stub
    print("Extracting code stub")
    cmd = 'pyjoplin imfeelinglucky %s' % uid
    proc = subprocess.Popen(cmd, shell=True)
    return uid, HideWindowAction()


def open_new_search_and_note_action(str_search):
    # Open browser and create new note
    query = str_search.strip()
    # Build URL for Google search
    url_google = "https://www.google.com/search?q=" + query.replace(' ', "+")
    # Focus 'search' workspace now
    subprocess.call("i3-msg workspace search", shell=True)
    # Open new browser with Google and calendar search
    browser = webbrowser.get('google-chrome')
    browser.open(url_google, new=1, autoraise=True)
    # Create new note and edit it
    new_uid = pyjoplin.new(query, notebook='search')

    cmd = 'pyjoplin edit %s' % new_uid
    proc = subprocess.Popen(cmd, shell=True)
    return new_uid, HideWindowAction()


def open_new_note_action(str_search):
    # Create new note and edit it
    query = str_search.strip()
    new_uid = pyjoplin.new(query, notebook='search')
    cmd = 'pyjoplin edit %s' % new_uid
    proc = subprocess.Popen(cmd, shell=True)
    return new_uid, HideWindowAction()
