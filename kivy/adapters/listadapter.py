'''
ListAdapter
=================

.. versionadded:: 1.5

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

A :class:`ListAdapter` is an adapter around a python list.

Selection operations are a main concern for the class.

From an :class:`Adapter`, a :class:`ListAdapter` gets cls, template, and
args_converter properties and adds others that control selection behaviour:

* *selection*, a list of selected items.

* *selection_mode*, 'single', 'multiple', 'none'

* *allow_empty_selection*, a boolean -- If False, a selection is forced. If
  True, and only user or programmatic action will change selection, it can
  be empty.

If you wish to have a bare-bones list adapter, without selection, use a
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`.

A :class:`~kivy.adapters.dictadapter.DictAdapter` is a subclass of a
:class:`~kivy.adapters.listadapter.ListAdapter`. They both dispatch the
*on_selection_change* event.

    :Events:
        `on_selection_change`: (view, view list )
            Fired when selection changes

.. versionchanged:: 1.6.0

    Added data = ListProperty([]), which was proably inadvertently deleted at
    some point. This means that whenever data changes an update will fire,
    instead of having to reset the data object (Adapter has data defined as
    an ObjectProperty, so we need to reset it here to ListProperty). See also
    DictAdapter and its set of data = DictProperty().

'''

__all__ = ('ListAdapter', )

import inspect
from kivy.event import EventDispatcher
from kivy.adapters.adapter import Adapter
from kivy.adapters.models import SelectableDataItem
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.properties import BooleanProperty
from kivy.properties import OptionProperty
from kivy.properties import NumericProperty
from kivy.properties import ObservableList
from kivy.lang import Builder


class RangeObservingObservableList(ObservableList):
    '''Adds range-observing intelligence to ObservableList'''

    # range_change is a normal python object consisting of:
    #
    #     (data_op, (start_index, end_index)
    #
    # If the op does not cause a range change, range_change is set to None.
    #
    # Observers of data changes may consult range_change if needed, for
    # example, listview needs to know details for scrolling.
    #
    # ListAdapter itself, the owner of data, is the first observer of data
    # change that must react to delete ops, if the existing selection is
    # affected.
    #

    cached_view_indices_and_data = DictProperty({})
    '''This has keys as the indices of the containing adapter's cached_views,
    for use in sorting operations. It is set by the adapter when needed.  In
    sorting, a temporary association is made to the data items. It is destroyed
    by the adapter in its sort op callback.
    '''

    def __init__(self, *largs):
        super(RangeObservingObservableList, self).__init__(*largs)

    def __setitem__(self, key, value):
        if key == 'range_change':
            self.range_change = None
        super(RangeObservingObservableList, self).__setitem__(key, value)

    def __delitem__(self, key):
        index = self.index(key)
        self.range_change = ('rool_delete', (index, index))
        super(RangeObservingObservableList, self).__delitem__(key)

    def __setslice__(self, *largs):
        self.range_change = None
        super(RangeObservingObservableList, self).__setslice__(*largs)

    def __delslice__(self, *largs):
        start_index = largs[0]
        end_index = largs[-1]
        self.range_change = ('rool_delete', (start_index, end_index))
        super(RangeObservingObservableList, self).__delslice__(*largs)

    def __iadd__(self, *largs):
        self.range_change = None
        super(RangeObservingObservableList, self).__iadd__(*largs)

    def __imul__(self, *largs):
        self.range_change = None
        super(RangeObservingObservableList, self).__imul__(*largs)

    def append(self, *largs):
        index = len(self)
        self.range_change = ('rool_add', (index, index))
        super(RangeObservingObservableList, self).append(*largs)

    def remove(self, *largs):
        index = self.index(largs[0])
        self.range_change = ('rool_delete', (index, index))
        super(RangeObservingObservableList, self).remove(*largs)

    def insert(self, *largs):
        index = self.index(largs[0])
        self.range_change = ('rool_insert', (index, index))
        super(RangeObservingObservableList, self).insert(*largs)

    def pop(self, *largs):
        if largs[0]:
            index = self.index(largs[0])
        else:
            index = len(self) - 1
        self.range_change = ('rool_delete', (index, index))
        return super(RangeObservingObservableList, self).pop(*largs)

    def extend(self, *largs):
        start_index = len(self)
        end_index = start_index + len(largs) - 1
        self.range_change = ('rool_add', (start_index, end_index))
        super(RangeObservingObservableList, self).extend(*largs)

    def sort(self, *largs):
        for i in self.cached_view_indices_and_data:
            self.cached_view_indices_and_data[i] = self.data[i]

        self.range_change = ('rool_sort', (0, len(self) - 1))
        super(RangeObservingObservableList, self).sort(*largs)

    def reverse(self, *largs):
        self.range_change = ('rool_sort', (0, len(self) - 1))
        super(RangeObservingObservableList, self).reverse(*largs)


class ListAdapter(Adapter, EventDispatcher):
    '''
    A base class for adapters interfacing with lists, dictionaries or other
    collection type data, adding selection, view creation and management
    functonality.
    '''

    data = ListProperty([], cls=RangeObservingObservableList)
    '''The data list property is redefined here, overriding its definition as
    an ObjectProperty in the Adapter class. We bind to data so that any
    changes will trigger updates. See also how the
    :class:`~kivy.adapters.DictAdapter` redefines data as a
    :class:`~kivy.properties.DictProperty`.

    :data:`data` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    selection = ListProperty([])
    '''The selection list property is the container for selected items.

    :data:`selection` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    selection_mode = OptionProperty('single',
            options=('none', 'single', 'multiple'))
    '''Selection modes:

       * *none*, use the list as a simple list (no select action). This option
         is here so that selection can be turned off, momentarily or
         permanently, for an existing list adapter.
         A :class:`~kivy.adapters.listadapter.ListAdapter` is not meant to be
         used as a primary no-selection list adapter.  Use a
         :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` for that.

       * *single*, multi-touch/click ignored. Single item selection only.

       * *multiple*, multi-touch / incremental addition to selection allowed;
         may be limited to a count by selection_limit

    :data:`selection_mode` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'single'.
    '''

    propagate_selection_to_data = BooleanProperty(False)
    '''Normally, data items are not selected/deselected because the data items
    might not have an is_selected boolean property -- only the item view for a
    given data item is selected/deselected as part of the maintained selection
    list. However, if the data items do have an is_selected property, or if
    they mix in :class:`~kivy.adapters.models.SelectableDataItem`, the
    selection machinery can propagate selection to data items. This can be
    useful for storing selection state in a local database or backend database
    for maintaining state in game play or other similar scenarios. It is a
    convenience function.

    NOTE: This would probably be better named as sync_selection_with_data().

    To propagate selection or not?

    Consider a shopping list application for shopping for fruits at the
    market. The app allows for the selection of fruits to buy for each day of
    the week, presenting seven lists: one for each day of the week. Each list is
    loaded with all the available fruits, but the selection for each is a
    subset. There is only one set of fruit data shared between the lists, so
    it would not make sense to propagate selection to the data because
    selection in any of the seven lists would clash and mix with that of the
    others.

    However, consider a game that uses the same fruits data for selecting
    fruits available for fruit-tossing. A given round of play could have a
    full fruits list, with fruits available for tossing shown selected. If the
    game is saved and rerun, the full fruits list, with selection marked on
    each item, would be reloaded correctly if selection is always propagated to
    the data. You could accomplish the same functionality by writing code to
    operate on list selection, but having selection stored in the data
    ListProperty might prove convenient in some cases.

    :data:`propagate_selection_to_data` is a
    :class:`~kivy.properties.BooleanProperty` and defaults to False.
    '''

    allow_empty_selection = BooleanProperty(True)
    '''The allow_empty_selection may be used for cascading selection between
    several list views, or between a list view and an observing view. Such
    automatic maintenance of the selection is important for all but simple
    list displays. Set allow_empty_selection to False and the selection is
    auto-initialized and always maintained, so any observing views
    may likewise be updated to stay in sync.

    :data:`allow_empty_selection` is a
    :class:`~kivy.properties.BooleanProperty` and defaults to True.
    '''

    selection_limit = NumericProperty(-1)
    '''When the selection_mode is multiple and the selection_limit is
    non-negative, this number will limit the number of selected items. It can
    be set to 1, which is equivalent to single selection. If selection_limit is
    not set, the default value is -1, meaning that no limit will be enforced.

    :data:`selection_limit` is a :class:`~kivy.properties.NumericProperty` and
    defaults to -1 (no limit).
    '''

    cached_views = DictProperty({})
    '''View instances for data items are instantiated and managed by the
    adapter. Here we maintain a dictionary containing the view
    instances keyed to the indices in the data.

    This dictionary works as a cache. get_view() only asks for a view from
    the adapter if one is not already stored for the requested index.

    :data:`cached_views` is a :class:`~kivy.properties.DictProperty` and
    defaults to {}.
    '''

    __events__ = ('on_selection_change',)

    def __init__(self, **kwargs):
        super(ListAdapter, self).__init__(**kwargs)

        self.bind(selection_mode=self.selection_mode_changed,
                  allow_empty_selection=self.check_for_empty_selection,
                  data=self.data_changed)

        # Prepare the dict property cached_view_indices_and_data, in our data
        # property (an ObservableList instance) so that, in the case of
        # sorting-related ops, an association can be made between the
        # item_views in cached_views to the data_items in data, enabling a
        # post-op update of cached_views indices.
        self.data.cached_view_indices_and_data = \
                dict([item_view.index for item_view in self.cached_views])

        self.delete_cache()
        self.initialize_selection()

    def data_changed(self, *dt):

        print 'ADAPTER data_changed callback', dt

        print self.data.range_change

        if self.data.range_change:

            data_op, (start_index, end_index) = self.data.range_change

            if data_op == 'rool_add':
                # The add op is an append, so this shouldn't affect anything.
                pass

            elif data_op == 'rool_delete':

                selection_was_affected = False

                deleted_indices = range(start_index, end_index + 1)

                # Delete views from cache.
                print 'cached_views', self.cached_views
                deleted_indices = range(start_index, end_index + 1)

                new_cached_views = {}

                i = 0
                for k, v in self.cached_views.iteritems():
                    if not k in deleted_indices:
                        new_cached_views[i] = self.cached_views[k]
                        if k >= start_index:
                            new_cached_views[i].index = i
                        i += 1

                self.cached_views = new_cached_views
                print 'cached_views', self.cached_views

                # Remove deleted views from selection.
                for selected_index in [item.index for item in self.selection]:
                    if selected_index in deleted_indices:
                        del self.selection[selected_index]
                        selection_was_affected = True

                if selection_was_affected:
                    self.dispatch('on_selection_change')

                self.check_for_empty_selection()

            elif data_op == 'rool_insert':

                inserted_indices = range(start_index, end_index + 1)

                new_cached_views = {}

                i = 0
                for k, v in self.cached_views.iteritems():
                    new_cached_views[i] = self.cached_views[k]
                    i += 1
                    if k >= start_index:
                        new_cached_views[i].index = i

                self.cached_views = new_cached_views

            elif data_op == 'rool_sort':

                for item_view in self.cached_views:
                    item_view.index = self.data.index(
                            self.data.cached_view_indices_and_data[item_view])

                self.data.cached_view_indices_and_data = {}

    def data_will_be_sorted(self, *args):
        self.cached_views_with_data_items = {}

        for item_view in self.cached_views:
            self.cached_views_with_data_items[item_view] = self.data[item_view.index]

    def delete_cache(self, *args):
        self.cached_views = {}

    def get_count(self):
        return len(self.data)

    def get_data_item(self, index):
        if index < 0 or index >= len(self.data):
            return None
        return self.data[index]

    def selection_mode_changed(self, *args):
        if self.selection_mode == 'none':
            for selected_view in self.selection:
                self.deselect_item_view(selected_view)
        else:
            self.check_for_empty_selection()

    def get_view(self, index):
        if index in self.cached_views:
            return self.cached_views[index]
        item_view = self.create_view(index)
        if item_view:
            self.cached_views[index] = item_view
        return item_view

    def create_view(self, index):
        '''This method is more complicated than the one in
        :class:`kivy.adapters.adapter.Adapter` and
        :class:`kivy.adapters.simplelistadapter.SimpleListAdapter`, because
        here we create bindings for the data item and its children back to
        self.handle_selection(), and do other selection-related tasks to keep
        item views in sync with the data.
        '''
        item = self.get_data_item(index)
        if item is None:
            return None

        item_args = self.args_converter(index, item)

        item_args['index'] = index

        if self.cls:
            view_instance = self.cls(**item_args)
        else:
            view_instance = Builder.template(self.template, **item_args)

        if self.propagate_selection_to_data:
            # The data item must be a subclass of SelectableDataItem, or must
            # have an is_selected boolean or function, so it has is_selected
            # available.  If is_selected is unavailable on the data item, an
            # exception is raised.
            #
            if isinstance(item, SelectableDataItem):
                if item.is_selected:
                    self.handle_selection(view_instance)
            elif type(item) == dict and 'is_selected' in item:
                if item['is_selected']:
                    self.handle_selection(view_instance)
            elif hasattr(item, 'is_selected'):
                if (inspect.isfunction(item.is_selected)
                        or inspect.ismethod(item.is_selected)):
                    if item.is_selected():
                        self.handle_selection(view_instance)
                else:
                    if item.is_selected:
                        self.handle_selection(view_instance)
            else:
                msg = "ListAdapter: unselectable data item for {0}"
                raise Exception(msg.format(index))

        view_instance.bind(on_release=self.handle_selection)

        for child in view_instance.children:
            child.bind(on_release=self.handle_selection)

        return view_instance

    def on_selection_change(self, *args):
        '''on_selection_change() is the default handler for the
        on_selection_change event.
        '''
        pass

    def handle_selection(self, view, hold_dispatch=False, *args):
        if view not in self.selection:
            if self.selection_mode in ['none', 'single'] and \
                    len(self.selection) > 0:
                for selected_view in self.selection:
                    self.deselect_item_view(selected_view)
            if self.selection_mode != 'none':
                if self.selection_mode == 'multiple':
                    if self.allow_empty_selection:
                        # If < 0, selection_limit is not active.
                        if self.selection_limit < 0:
                            self.select_item_view(view)
                        else:
                            if len(self.selection) < self.selection_limit:
                                self.select_item_view(view)
                    else:
                        self.select_item_view(view)
                else:
                    self.select_item_view(view)
        else:
            self.deselect_item_view(view)
            if self.selection_mode != 'none':
                #
                # If the deselection makes selection empty, the following call
                # will check allows_empty_selection, and if False, will
                # select the first item. If view happens to be the first item,
                # this will be a reselection, and the user will notice no
                # change, except perhaps a flicker.
                #
                self.check_for_empty_selection()

        if not hold_dispatch:
            self.dispatch('on_selection_change')

    def select_data_item(self, item):
        self.set_data_item_selection(item, True)

    def deselect_data_item(self, item):
        self.set_data_item_selection(item, False)

    def set_data_item_selection(self, item, value):
        if isinstance(item, SelectableDataItem):
            item.is_selected = value
        elif type(item) == dict:
            item['is_selected'] = value
        elif hasattr(item, 'is_selected'):
            if (inspect.isfunction(item.is_selected)
                    or inspect.ismethod(item.is_selected)):
                item.is_selected()
            else:
                item.is_selected = value

    def select_item_view(self, view):
        view.select()
        view.is_selected = True
        self.selection.append(view)

        # [TODO] sibling selection for composite items
        #        Needed? Or handled from parent?
        #        (avoid circular, redundant selection)
        #if hasattr(view, 'parent') and hasattr(view.parent, 'children'):
         #siblings = [child for child in view.parent.children if child != view]
         #for sibling in siblings:
             #if hasattr(sibling, 'select'):
                 #sibling.select()

        if self.propagate_selection_to_data:
            data_item = self.get_data_item(view.index)
            self.select_data_item(data_item)

    def select_list(self, view_list, extend=True):
        '''The select call is made for the items in the provided view_list.

        Arguments:

            view_list: the list of item views to become the new selection, or
            to add to the existing selection

            extend: boolean for whether or not to extend the existing list
        '''
        if not extend:
            self.selection = []

        for view in view_list:
            self.handle_selection(view, hold_dispatch=True)

        self.dispatch('on_selection_change')

    def deselect_item_view(self, view):
        view.deselect()
        view.is_selected = False
        self.selection.remove(view)

        # [TODO] sibling deselection for composite items
        #        Needed? Or handled from parent?
        #        (avoid circular, redundant selection)
        #if hasattr(view, 'parent') and hasattr(view.parent, 'children'):
         #siblings = [child for child in view.parent.children if child != view]
         #for sibling in siblings:
             #if hasattr(sibling, 'deselect'):
                 #sibling.deselect()

        if self.propagate_selection_to_data:
            item = self.get_data_item(view.index)
            self.deselect_data_item(item)

    def deselect_list(self, l):
        for view in l:
            self.handle_selection(view, hold_dispatch=True)

        self.dispatch('on_selection_change')

    # [TODO] Could easily add select_all() and deselect_all().

    def initialize_selection(self, *args):
        if len(self.selection) > 0:
            self.selection = []
            self.dispatch('on_selection_change')

        self.check_for_empty_selection()

    def check_for_empty_selection(self, *args):
        if not self.allow_empty_selection:
            if len(self.selection) == 0:
                # Select the first item if we have it.
                v = self.get_view(0)
                if v is not None:
                    self.handle_selection(v)

    # [TODO] Also make methods for scroll_to_sel_start, scroll_to_sel_end,
    #        scroll_to_sel_middle.

    def trim_left_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are less than the
        index of the first selected item if there is a selection.
        '''
        if len(self.selection) > 0:
            first_sel_index = min([sel.index for sel in self.selection])
            self.data = self.data[first_sel_index:]

    def trim_right_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are greater than
        the index of the last selected item if there is a selection.
        '''
        if len(self.selection) > 0:
            last_sel_index = max([sel.index for sel in self.selection])
            print('last_sel_index', last_sel_index)
            self.data = self.data[:last_sel_index + 1]

    def trim_to_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are les than or
        greater than the index of the last selected item if there is a
        selection. This preserves intervening list items within the selected
        range.
        '''
        if len(self.selection) > 0:
            sel_indices = [sel.index for sel in self.selection]
            first_sel_index = min(sel_indices)
            last_sel_index = max(sel_indices)
            self.data = self.data[first_sel_index:last_sel_index + 1]

    def cut_to_sel(self, *args):
        '''Same as trim_to_sel, but intervening list items within the selected
        range are also cut, leaving only list items that are selected.
        '''
        if len(self.selection) > 0:
            self.data = self.selection
