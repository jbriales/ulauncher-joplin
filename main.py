from pyjoplin.main import search

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
                    name='New search: %s' % search_str,
                    on_enter=HideWindowAction()
                )
            )

            print("Searching database")
            found_notes = search(search_str)
            # Rebuild found items list

            for note in found_notes:
                # print("Note: {title}\n{body}\n".format(**idx_note))
                # print("Note: {title}\nSnippet:\n{snippet}\n".format(**note))

                idx_item = len(extension.items)
                item = ExtensionSmallResultItem(
                # item = ExtensionResultItem(
                    icon='images/icon.png',
                    name='NOTE: %s' % note['title'],
                    description=note['snippet'],
                    # description=note['body'],
                    on_enter=ExtensionCustomAction({'type': 'enter', 'idx': idx_item}, keep_app_open=True),
                    on_alt_enter=ExtensionCustomAction({'type': 'alt', 'idx': idx_item}, keep_app_open=True)
                )
                extension.items.append(item)
                # on_enter_data = {'new_name': 'Item %s was clicked' % i}
                # on_alt_enter_data = {'new_name': 'Item %s was alt-entered' % i}
                # items.append(ExtensionSmallResultItem(
                #     icon='images/icon.png',
                #     name='Item %s' % i,
                #     description='Item description %s' % i,
                #     on_enter=ExtensionCustomAction(on_enter_data, keep_app_open=True),
                #     on_alt_enter=ExtensionCustomAction(on_alt_enter_data, keep_app_open=True)
                # ))

        return RenderResultListAction(extension.items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        data = event.get_data()
        if data['type'] == 'alt':
            # Display details of chosen entry
            idx_item = data['idx']
            item = extension.items[idx_item]
            # Substitute this entry by detailed one
            detailed_item = ExtensionResultItem(
                icon='images/icon.png',
                name=item.get_name(),
                description=item.get_description(None),
                # on_enter=ExtensionCustomAction({'type': 'enter', 'idx': idx_item}, keep_app_open=True),
                # on_alt_enter=ExtensionCustomAction({'type': 'alt', 'idx': idx_item}, keep_app_open=True)
            )
            extension.items[idx_item] = detailed_item

            return RenderResultListAction(extension.items)

        return False


if __name__ == '__main__':
    JoplinExtension().run()
