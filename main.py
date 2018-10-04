# coding=utf-8

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
from items import create_note_item, create_search_item, create_default_items_list


class JoplinExtension(Extension):

    def __init__(self):
        super(JoplinExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.history_uids = RecentHistory()
        self.items = list()


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get search query from event
        search_str_start_index = len(extension.preferences['joplin_kw'])+1
        search_str = event.query[search_str_start_index:]
        # Save last query character (space gives special behavior)
        last_query_character = search_str[-1:]
        # Remove trailing whitespace from query
        search_str = search_str.strip()
        if not search_str:
            # Corner case: No search query, empty list
            # Populate default history view
            extension.items = create_default_items_list(extension.history_uids, do_history_clean=True)
        else:
            # If there is a non-empty query

            # Trigger search of query in database and build search result list
            fts_search_pattern = search_str
            if last_query_character != ' ':
                # Probably incomplete word (so use prefix query type, e.g. 'py*')
                fts_search_pattern += '*'
            print("Searching database")
            found_notes = pyjoplin.search(fts_search_pattern)

            extension.items = list()
            extension.items.append(
                create_search_item(search_str)
            )
            for note in found_notes:
                idx_item = len(extension.items)
                item = create_note_item(note, idx_item)
                extension.items.append(item)

        return RenderResultListAction(extension.items)


class ItemEnterEventListener(EventListener):
    """
    Handle responses to item list clicks
    """

    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        data = event.get_data()
        # Get function to call
        fun = data.pop('func')
        visited_uid, action = fun(**data)
        if visited_uid:
            extension.history_uids.append(visited_uid)
        if isinstance(action, HideWindowAction):
            # Clear list of result items for next extension execution
            extension.items = list()
        return action


if __name__ == '__main__':
    JoplinExtension().run()
