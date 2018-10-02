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
        self.last_query = ""
        self.last_search_str = ""
        self.last_items = list()


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get search query from event
        search_str = event.query.lstrip(extension.preferences['joplin_kw'] + ' ')

        print("Last search string: %s" % extension.last_search_str)
        print("Last extension query: %s" % extension.last_query)
        print("Current query: %s" % search_str)

        # Find fixed part from last query
        previous_terms = extension.last_query.split()
        current_terms = search_str.split()
        # Find common head elements
        fixed_terms = list()
        for term, i in enumerate(previous_terms):
            if term == current_terms[i]:
                fixed_terms.append(term)
            else:
                break
        fixed_search_str = ' '.join(fixed_terms)

        # Update last query stored in extension
        extension.last_query = search_str

        if fixed_search_str == extension.last_search_str:
            # Skip search, use same items as before
            items = extension.last_items
        else:
            print("Making new search")
            found_index_notes = search(fixed_search_str)
            items = list()
            for idx_note in found_index_notes:
                # print("Note: {title}\n{body}\n".format(**idx_note))
                print("Note: {title}\n{snippet}\n".format(**idx_note))

                item = ExtensionResultItem(
                    icon='images/icon.png',
                    name='NOTE: %s' % idx_note['title'],
                    description=idx_note['snippet'],
                    on_enter=HideWindowAction()
                )
                items.append(item)
                # on_enter_data = {'new_name': 'Item %s was clicked' % i}
                # on_alt_enter_data = {'new_name': 'Item %s was alt-entered' % i}
                # items.append(ExtensionSmallResultItem(
                #     icon='images/icon.png',
                #     name='Item %s' % i,
                #     description='Item description %s' % i,
                #     on_enter=ExtensionCustomAction(on_enter_data, keep_app_open=True),
                #     on_alt_enter=ExtensionCustomAction(on_alt_enter_data, keep_app_open=True)
                # ))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        data = event.get_data()
        # do additional actions here...

        # you may want to return another list of results
        return RenderResultListAction([ExtensionResultItem(icon='images/icon.png',
                                                           name=data['new_name'],
                                                           on_enter=HideWindowAction())])


if __name__ == '__main__':
    JoplinExtension().run()
