# coding=utf-8

import os
import subprocess
import webbrowser

import pyjoplin

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
# from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

from history import RecentHistory
from items import create_note_item, create_search_item


def create_default_items_list(history_uids):
    items = list()

    # Add entries from recent history
    notes = pyjoplin.get_notes_by_id(history_uids[::-1], ordered=True)
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


class JoplinExtension(Extension):

    def __init__(self):
        super(JoplinExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.history_uids = RecentHistory()
        self.items = create_default_items_list(self.history_uids)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get search query from event
        search_str_start_index = len(extension.preferences['joplin_kw'])+1
        search_str = event.query[search_str_start_index:]

        # NOTE: Wait for space at the end of query to trigger search
        last_query_character = search_str[-1:]
        if last_query_character != ' ':
            # Skip search, use same items as before (stored in extension)
            pass

        else:
            extension.items = list()
            # Add first item for new search and note
            item = create_search_item(search_str)
            extension.items.append(item)

            print("Searching database")
            found_notes = pyjoplin.search(search_str)
            # Build result list of found items
            for note in found_notes:
                idx_item = len(extension.items)
                item = create_note_item(note, idx_item)
                extension.items.append(item)

        return RenderResultListAction(extension.items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        data = event.get_data()
        if data['type'] == 'search-enter1':
            # Make chosen entry detailed
            idx_item = data['idx']
            item = extension.items[idx_item]
            # Substitute this entry by detailed one
            detailed_item = ExtensionResultItem(
                icon='images/joplin.png',
                name=item.get_name(),
                description=item.get_description(None),
                on_enter=ExtensionCustomAction(
                    {
                        'type': 'search-enter2',
                        'idx': idx_item,
                        'uid': data['uid']
                    },
                    keep_app_open=True),
            )
            extension.items[idx_item] = detailed_item

            # Ensure all other entries are small
            # TODO

            return RenderResultListAction(extension.items)

        elif data['type'] == 'search-enter2':
            # Edit chosen note
            print("Opening note edition")
            cmd = 'pyjoplin edit %s' % data['uid']
            proc = subprocess.Popen(cmd, shell=True)
            extension.history_uids.append(data['uid'])
            return HideWindowAction()

        elif data['type'] == 'imfeelinglucky':
            # Try to get solution code stub
            print("Extracting code stub")
            cmd = 'pyjoplin imfeelinglucky %s' % data['uid']
            proc = subprocess.Popen(cmd, shell=True)
            extension.history_uids.append(data['uid'])
            return HideWindowAction()

        elif data['type'] == 'new-search-and-note':
            # Open browser and create new note
            query = data['str'].strip()
            # Build URL for Google search
            url_google = "https://www.google.com/search?q=" + query.replace(' ', "+")
            # Focus 'search' workspace now
            subprocess.call("i3-msg workspace search", shell=True)
            # Open new browser with Google and calendar search
            browser = webbrowser.get('google-chrome')
            browser.open(url_google, new=1, autoraise=True)
            # Create new note and edit it
            new_uid = pyjoplin.new(query, notebook='search')
            extension.history_uids.append(new_uid)
            cmd = 'pyjoplin edit %s' % new_uid
            proc = subprocess.Popen(cmd, shell=True)
            return HideWindowAction()

        elif data['type'] == 'new-note':
            # Create new note and edit it
            query = data['str'].strip()
            new_uid = pyjoplin.new(query, notebook='search')
            extension.history_uids.append(new_uid)
            cmd = 'pyjoplin edit %s' % new_uid
            proc = subprocess.Popen(cmd, shell=True)
            return HideWindowAction()

        return False


if __name__ == '__main__':
    JoplinExtension().run()
