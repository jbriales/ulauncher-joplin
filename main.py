import subprocess
import webbrowser

from pyjoplin.main import new, search, edit

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction


class JoplinExtension(Extension):

    def __init__(self):
        super(JoplinExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.items = list()


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

            if not search_str:
                extension.items = [
                    ExtensionResultItem(
                        icon='images/search.png',
                        name='Write search query ended with space...'
                    )
                ]
        else:
            extension.items = list()
            extension.items.append(
                ExtensionSmallResultItem(
                    icon='images/chrome.png',
                    name='New search note: %s' % search_str,
                    on_enter=ExtensionCustomAction(
                        {
                            'type': 'new-search',
                            'str': search_str,
                        },
                        keep_app_open=True
                    ),
                )
            )

            print("Searching database")
            found_notes = search(search_str)
            # Build result list of found items
            for note in found_notes:
                idx_item = len(extension.items)
                item = ExtensionSmallResultItem(
                    icon='images/icon.png',
                    name='NOTE: %s' % note['title'],
                    description=note['snippet'],
                    # description=note['body'],
                    on_enter=ExtensionCustomAction(
                        {
                            'type': 'search-enter2',
                            'idx': idx_item,
                            'uid': note['uid']
                        },
                        keep_app_open=True),
                    on_alt_enter=ExtensionCustomAction(
                        {
                            'type': 'search-enter1',
                            'idx': idx_item,
                            'uid': note['uid']
                        },
                        keep_app_open=True),
                )
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
                icon='images/icon.png',
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
            # TODO: Maybe open in an independent process/thread?
            edit(data['uid'])
            return HideWindowAction()

        elif data['type'] == 'new-search':
            # Open browser and create new note
            query = data['str']
            # Build URL for Google search
            url_google = "https://www.google.com/search?q=" + query.replace(' ', "+")
            # Focus 'search' workspace now
            subprocess.call("i3-msg workspace search", shell=True)
            # Open new browser with Google and calendar search
            browser = webbrowser.get('google-chrome')
            browser.open(url_google, new=1, autoraise=True)
            # Create new note
            new_uid = new(query, 'search')
            edit(new_uid)
            return HideWindowAction()

        return False


if __name__ == '__main__':
    JoplinExtension().run()
