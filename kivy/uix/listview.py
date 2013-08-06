'''
List View
===========

.. versionadded:: 1.5

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

The :class:`~kivy.uix.listview.ListView` widget provides a scrollable/pannable
viewport that is clipped at the scrollview's bounding box, which contains
list item view instances.

:class:`~kivy.uix.listview.ListView` implements :class:`AbstractView` as a
vertical scrollable list. :class:`AbstractView` has one property, adapter.
:class:`~kivy.uix.listview.ListView` sets adapter to one of:
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`,
:class:`~kivy.adapters.listadapter.ListAdapter`, or
:class:`~kivy.adapters.dictadapter.DictAdapter`.

.. versionchanged:: 1.8.0

    The underlying adapter and selection system changed in support of
    operations here, which needed to receive more detailed information about
    changes to data held in adapters, either in ListAdapter or DictAdapter. The
    data_changed() method replaces a call to bind_triggers_to_view(), now
    deprecated. Previously, with limited information about data change, only
    broad scroll and child handling reactions could be made. Now, in the new
    data_changed() method, there is an opportunity to react to individual item
    resets, to insertions, deletions, sort, etc. Sometimes it is necessary to
    remove and force recreation of views, sometimes it is necessary to make a
    specific scroll action, and so on.

    Removed ListItemLabel.

    SelectableView now subclasses ButtonBehavior, and has a
    carry_selection_to_children property.

    CompositeListItem now has a bind_selection_from_children property, and its
    is_representing_cls is now deprecated.

Introduction
------------

Lists are central parts of many software projects. Kivy's approach to lists
includes providing solutions for simple lists, along with a substantial
framework for building lists of moderate to advanced complexity. For the new
user of the system, it can be difficult to ramp up from simple to advanced. For
this reason, Kivy provides an extensive set of examples that you may wish to
run first, to get a taste of the range of functionality offered. You can tell
from the names of the examples that they illustrate the "ramping up" from
simple to advanced:

    * kivy/examples/widgets/lists/list_simple.py
    * kivy/examples/widgets/lists/list_simple_in_kv.py
    * kivy/examples/widgets/lists/list_simple_in_kv_2.py
    * kivy/examples/widgets/lists/list_master_detail.py
    * kivy/examples/widgets/lists/list_two_up.py
    * kivy/examples/widgets/lists/list_kv.py
    * kivy/examples/widgets/lists/list_composite.py
    * kivy/examples/widgets/lists/list_cascade.py
    * kivy/examples/widgets/lists/list_cascade_dict.py
    * kivy/examples/widgets/lists/list_cascade_images.py
    * kivy/examples/widgets/lists/list_ops.py

Many of the examples feature selection, some restricting selection to single
selection, where only one item at at time can be selected, and others allowing
multiple item selection. Many of the examples illustrate how selection in one
list can be connected to action and selection in another view or another list.

Find your own way of reading the documentation here, examining the source code
for the example apps, and running the examples. Some may prefer to read the
documentation through first, others may want to run the examples and view their
code. No matter what you do, going back and forth will likely be needed.

Basic Example
-------------

In its simplest form, we make a listview with 100 items::

    from kivy.uix.listview import ListView
    from kivy.uix.gridlayout import GridLayout


    class MainView(GridLayout):

        def __init__(self, **kwargs):
            kwargs['cols'] = 2
            super(MainView, self).__init__(**kwargs)

            list_view = ListView(
                item_strings=[str(index) for index in range(100)])

            self.add_widget(list_view)


    if __name__ == '__main__':
        from kivy.base import runTouchApp
        runTouchApp(MainView(width=800))

Or, we could declare the listview in using the kv language::

    from kivy.uix.modalview import ModalView
    from kivy.uix.listview import ListView
    from kivy.uix.gridlayout import GridLayout
    from kivy.lang import Builder

    Builder.load_string("""
    <ListViewModal>:
        size_hint: None, None
        size: 400, 400
        ListView:
            size_hint: .8, .8
            item_strings: [str(index) for index in range(100)]
    """)


    class ListViewModal(ModalView):
        def __init__(self, **kwargs):
            super(ListViewModal, self).__init__(**kwargs)


    class MainView(GridLayout):

        def __init__(self, **kwargs):
            kwargs['cols'] = 1
            super(MainView, self).__init__(**kwargs)

            listview_modal = ListViewModal()

            self.add_widget(listview_modal)


    if __name__ == '__main__':
        from kivy.base import runTouchApp
        runTouchApp(MainView(width=800))

Using an Adapter
-------------------

Behind the scenes, the basic example above uses
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`.  When the
constructor for :class:`~kivy.uix.listview.ListView` sees that only a list of
strings is provided as an argument, called item_strings, it creates an instance
of :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` using the list
of strings.

Simple in :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` means:
*without selection support*. It is a scrollable list of items that do not
respond to touch events.

To use :class:`SimpleListAdaper` explicitly in creating a ListView instance,
do::

    simple_list_adapter = SimpleListAdapter(
            data=["Item #{0}".format(i) for i in range(100)],
            cls=Label)

    list_view = ListView(adapter=simple_list_adapter)

The instance of :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` has
a required data argument, which contains data items to use for instantiating
Label views for the list view (Note the cls=Label argument). The data items are
strings.  Each item string is set by
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` as the *text*
argument for each Label instantiation.

You can declare a ListView with an adapter in a kv file, with special attention
given to the way longer python blocks are indented::

    from kivy.uix.modalview import ModalView
    from kivy.uix.listview import ListView
    from kivy.uix.gridlayout import GridLayout
    from kivy.lang import Builder
    from kivy.factory import Factory

    # Note the special nature of indentation in the adapter declaration, where
    # the adapter: is on one line, then the value side must be given at one
    # level of indentation.

    Builder.load_string("""
    #:import label kivy.uix.label
    #:import sla kivy.adapters.simplelistadapter

    <ListViewModal>:
        size_hint: None, None
        size: 400, 400
        ListView:
            size_hint: .8, .8
            adapter:
                sla.SimpleListAdapter(
                data=["Item #{0}".format(i) for i in range(100)],
                cls=label.Label)
    """)


    class ListViewModal(ModalView):
        def __init__(self, **kwargs):
            super(ListViewModal, self).__init__(**kwargs)


    class MainView(GridLayout):

        def __init__(self, **kwargs):
            kwargs['cols'] = 1
            super(MainView, self).__init__(**kwargs)

            listview_modal = ListViewModal()

            self.add_widget(listview_modal)


    if __name__ == '__main__':
        from kivy.base import runTouchApp
        runTouchApp(MainView(width=800))

ListAdapter and DictAdapter
---------------------------

For many uses of a list, the data is more than a simple list of strings.
Selection functionality is also often needed.
:class:`~kivy.adapters.listadapter.ListAdapter` and
:class:`~kivy.adapters.dictadapter.DictAdapter` cover these more elaborate
needs.

:class:`~kivy.adapters.listadapter.ListAdapter` is simpler than
:class:`~kivy.adapters.dictadapter.DictAdapter`, so we can start with it.

See the :class:`~kivy.adapters.listadapter.ListAdapter` docs for details, but
here are synopses of its arguments:

* *data*: strings, class instances, dicts, etc. that form the basis data
  for instantiating views.

* *cls*: a Kivy view that is to be instantiated for each list item. There
  are several built-in types available, including ListItemLabel and
  ListItemButton, or you can make your own class that mixes in the
  required `~kivy.uix.listview.SelectableView`.

* *template*: the name of a Kivy language (kv) template that defines the
  Kivy view for each list item.

.. note::

    Pick only one, cls or template, to provide as an argument.

* *args_converter*: a function that takes a data item object as input, and
  uses it to build and return an args dict, ready
  to be used in a call to instantiate item views using the item view cls
  or template. In the case of cls, the args dict acts as a
  kwargs object. For a template, it is treated as a context
  (ctx), but is essentially similar in form to kwargs usage.

* *selection_mode*: a string for: 'single', 'multiple' or others (See docs).

* *allow_empty_selection*: a boolean, which if False, the default, forces
  there to always be a selection, if there is data
  available. If True, selection happens only as a
  result of user action.

In narrative, we can summarize with:

    A listview's adapter takes data items and uses an args_converter
    function to transform them into arguments for making list item view
    instances, using either a cls or a kv template.

In a graphic, a summary of the relationship between a listview and its
list adapter, looks like this::

    -                    ------------ ListAdapter or DictAdapter ------------
    -                    |                                                  |
    -                    | <list item views> (cls or template) <data items> |
    -   ListView   -->   |                           [args_converter]       |
    -                    |                                                  |
    -                    |           <<< selection handling >>>             |
    -                    |                                                  |
    -                    ----------------------------------------------------

:class:`~kivy.adapters.dictadapter.DictAdapter` has the same arguments and
requirements as :class:`~kivy.adapters.listadapter.ListAdapter`, except:

1) There is an additional argument, sorted_keys, which must meet the
   requirements of normal python dictionary keys.

2) The data argument is, as you would expect, a dict. Keys in the dict
   must include the keys in the sorted_keys argument, but they may form a
   superset of the keys in sorted_keys. Values may be strings, class
   instances, dicts, etc. (The args_converter uses it, accordingly).

3) The args_converter receives an additional arg, the dict key. For
   ListAdapter, the calling signature for an args_converter is:

       args_converter(index, data_item)

   but for DictAdapter, it is:

       args_converter(index, data_item, key)

Using an Args Converter
-----------------------

:class:`~kivy.uix.listview.ListView` allows use of built-in list item views,
such as :class:`~kivy.uix.listview.ListItemButton`, your own custom item view
class, or a custom kv template. Whichever type of list item view is used, an
args_converter function is needed to prepare, per list data item, args for
either a cls or template.

.. note::

    ListItemLabel and ListItemButton, or custom classes like them, and not the
    bare Label nor Button classes, are to be used.

.. warning::

    ListItemButton inherits the `background_normal` and `background_down`
    properties from the Button widget, so the `selected_color` and
    `deselected_color` are not represented faithfully by default.

Here is an args_converter for ListAdapter, for use with the built-in
:class:`~kivy.uix.listview.ListItemButton`, specified as a normal Python
function::

    def args_converter(index, an_obj):
        return {'text': an_obj.some_prop,
                'size_hint_y': None,
                'height': 25}

and as a lambda:

    args_converter = lambda index, an_obj: {'text': an_obj.some_prop,
                                            'size_hint_y': None,
                                            'height': 25}

In the args converter example above, the data item is assumed to be an object
(class instance), hence the reference an_obj.some_prop.

Here is an example of an args converter that works with list data items that
are dicts::

    args_converter = \
            lambda index, obj, key: {'text': key + '-' + obj.some_prop,
                                     'size_hint_y': None,
                                     'height': 25}

So, it is the responsibility of the developer to code the args_converter
according to the data at hand. The index argument can be useful in some
cases, such as when custom labels are needed.

An Example ListView
-------------------

Now, to some example code::

    from kivy.adapters.listadapter import ListAdapter
    from kivy.uix.listview import ListItemButton, ListView

    data = [{'text': str(i), 'is_selected': False} for i in range(100)]

    args_converter = lambda index, rec: {'text': rec['text'],
                                         'size_hint_y': None,
                                         'height': 25}

    list_adapter = ListAdapter(data=data,
                               args_converter=args_converter,
                               cls=ListItemButton,
                               selection_mode='single',
                               allow_empty_selection=False)

    list_view = ListView(adapter=list_adapter)

This listview will show 100 buttons with 0..100 labels. The args converter
function works on dict items (rec, for record) in the data. ListItemButton
views will be instantiated from the args converted by args_converter for each
data item. The listview will only allow single selection -- additional touches
will be ignored. When the listview is first shown, the first item will already
be selected, because allow_empty_selection is False.

:class:`~kivy.uix.listview.ListItemLabel` works much the same way as
:class:`~kivy.uix.listview.ListItemButton`.

Using a Custom Item View Class
------------------------------

The data used in an adapter can be any of the normal Python types, such as
strings, class instances, and dictionaries. It is up to the programmer to
assure that the args_converter has appropriate functionality.

Here we make a simple DataItem class that has the required text and
is_selected properties::

    from kivy.uix.listview import ListItemButton

    class DataItem(object):
        def __init__(self, text='', is_selected=False):
            self.text = text
            self.is_selected = is_selected

    data_items = []
    data_items.append(DataItem(text='cat'))
    data_items.append(DataItem(text='dog'))
    data_items.append(DataItem(text='frog'))

    list_item_args_converter = lambda index, obj: {'text': obj.text,
                                                   'size_hint_y': None,
                                                   'height': 25}

    list_adapter = ListAdapter(data=data_items,
                               args_converter=list_item_args_converter,
                               selection_mode='single',
                               sync_with_model_data=True,
                               allow_empty_selection=False,
                               cls=ListItemButton)

    list_view = ListView(adapter=list_adapter)

The data is set in a :class:`~kivy.adapters.listadapter.ListAdapter` along with
a list item args_converter function above (a lambda) and arguments concerning
selection: only single selection is allowed, and selection in the listview will
sync with the data items. The sync setting means that the is_selected property
for each data item will be set and kept in sync with the list item views. By
having allow_empty_selection=False, when the listview first appears, the first
item, 'cat', will already be selected. The list adapter will instantiate a
:class:`~kivy.uix.listview.ListItemButton` instance for each data item, using
the assigned args_converter.

The list_vew would be added to a view with add_widget() after the last line,
where it is created. See the basic example at the top of this documentation for
an example of add_widget() in the context of a sample app.

You may also use the provided :class:`SelectableDataItem` mixin to make a
custom class. Instead of the manually-constructed DataItem class above,
we could do::

    from kivy.adapters.models import SelectableDataItem

    class DataItem(SelectableDataItem):
        # Add properties here.

:class:`SelectableDataItem` is a simple mixin class that has an is_selected
property.

Using an Item View Template
---------------------------

:class:`~kivy.uix.listview.SelectableView` is another simple mixin class that
has required properties for a list item: text, and is_selected. To make your
own template, mix it in as follows::

    from kivy.uix.listview import ListItemButton
    from kivy.uix.listview import SelectableView

    Builder.load_string("""
    [CustomListItem@SelectableView+BoxLayout]:
        size_hint_y: ctx.size_hint_y
        height: ctx.height
        ListItemButton:
            text: ctx.text
            is_selected: ctx.is_selected
    """)

A class called CustomListItem will be instantiated for each list item. Note
that it is a layout, BoxLayout, and is thus a kind of container. It contains a
:class:`~kivy.uix.listview.ListItemButton` instance.

Using the power of the Kivy language (kv), you can easily build composite list
items. In addition to ListItemButton, you could have a ListItemLabel, or a
custom class you have defined and registered with the system.

An args_converter needs to be constructed that goes along with such a kv
template. For example, to use the kv template above::

    list_item_args_converter = \
            lambda index, rec, key: {'text': key,
                                     'is_selected': rec['is_selected'],
                                     'size_hint_y': None,
                                     'height': 25}
    integers_dict = {str(i): {'is_selected': False} for i in range(100)}

    dict_adapter = DictAdapter(sorted_keys=[str(i) for i in range(100)],
                               data=integers_dict,
                               args_converter=list_item_args_converter,
                               template='CustomListItem')

    list_view = ListView(adapter=dict_adapter)

A dict adapter is created with 1..100 integer strings as sorted_keys, and an
integers_dict as data, a dict with str(i) keys and simple dict as values.
integers_dict has the integer strings as keys and dicts with text and
is_selected properties. The CustomListItem defined above in the
Builder.load_string() call is set as the kv template for the list item views.
The list_item_args_converter lambda function will take each dict in
integers_dict and will return an args dict, ready for passing as the context
(ctx) for the template.

The list_vew would be added to a view with add_widget() after the last line,
where it is created. Again, see the basic example above for add_widget() use.

Using CompositeListItem
-----------------------

The class :class:`~kivy.uix.listview.CompositeListItem` is another option for
building advanced composite list items. The kv language approach has its
advantages, but here we build a composite list view using a straight Kivy
widget method::

    args_converter = lambda index, rec, key: \
            {'text': key,
             'size_hint_y': None,
             'height': 25,
             'cls_dicts': [{'cls': ListItemButton,
                            'kwargs': {'text': key}},
                           {'cls': ListItemLabel,
                            'kwargs': {'text': "x10={0}".format(rec['x10'])}},
                           {'cls': ListItemButton,
                            'kwargs': {'text': str(rec['x100_text'])}}]}

    item_strings = ["{0}".format(index) for index in range(100)]

    integers_dict = \
        { str(i): {'x10': i * 10,
                   'x100_text': 'x100={0}'.format(i * 100),
                   'is_selected': False} for i in range(100)}

    dict_adapter = DictAdapter(sorted_keys=item_strings,
                               data=integers_dict,
                               args_converter=args_converter,
                               selection_mode='single',
                               allow_empty_selection=False,
                               cls=CompositeListItem)

    list_view = ListView(adapter=dict_adapter)

The args_converter is somewhat complicated, so we should go through the
details. Observe in the :class:`~kivy.adapters.dictadapter.DictAdapter`
instantiation that :class:`~kivy.uix.listview.CompositeListItem` instance is
set as the cls to be instantiated for each list item. The args_converter will
make args dicts for this cls.  In the args_converter, the first three items,
text, size_hint_y, and height, are arguments for CompositeListItem itself.
After that you see a cls_dicts list that contains argument sets for each of the
member widgets for this composite: :class:`~kivy.uix.listview.ListItemButton`
and :class:`~kivy.uix.listview.ListItemLabel`. This is a similar approach to
using a kv template described above.

The sorted_keys and data arguments for the dict adapter are the same as in the
previous code example.

For details on how :class:`~kivy.uix.listview.CompositeListItem` works,
examine the code, looking for how parsing of the cls_dicts list and kwargs
processing is done.

Uses for Selection
------------------

What can we do with selection? Combining selection with the system of bindings
in Kivy, we can build a wide range of user interface designs.

We could make data items that contain the names of dog breeds, and connect
the selection of dog breed to the display of details in another view, which
would update automatically on selection. This is done via a binding to
selection::

    list_adapter.bind(selection=callback_function)

where callback_function() does whatever is needed for the update. See the
example called list_master_detail.py, and imagine that the list one the left
would be a list of dog breeds, and the detail view on the right would show
details for a selected dog breed.

In another example, we could set the selection_mode of a listview to
'multiple', and load it with a list of answers to a multiple-choice question.
The question could have several correct answers. A color swatch view could be
bound to selection change, as above, so that it turns green as soon as the
correct choices are made, unless the number of touches exeeds a limit, when the
answer session would be terminated. See the examples that feature thumbnail
images to get some ideas, e.g., list_cascade_dict.py.

In a more involved example, we could chain together three listviews, where
selection in the first controls the items shown in the second, and selection in
the second controls the items shown in the third. If allow_empty_selection were
set to False for these listviews, a dynamic system of selection "cascading"
from one list to the next, would result.

There are so many ways that listviews and Kivy bindings functionality can be
used, that we have only scratched the surface here. For on-disk examples, see
these::

    kivy/examples/widgets/lists/list_*.py

Several examples show the "cascading" behavior described above. Others
demonstrate the use of kv templates and composite list views.

'''

__all__ = ('SelectableView', 'ListItemButton',
           'CompositeListItem', 'ListView', )

from math import ceil, floor

from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger

from kivy.properties import BooleanProperty
from kivy.properties import DictProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty

from kivy.properties import DictOpInfo
from kivy.properties import ListOpInfo

from kivy.uix.abstractview import AbstractView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class SelectableView(ButtonBehavior):
    '''The :class:`~kivy.uix.listview.SelectableView` mixin is used to design
    list item and other classes that are to be instantiated by an adapter to be
    used in a listview.  The :class:`~kivy.adapters.listadapter.ListAdapter`
    and :class:`~kivy.adapters.dictadapter.DictAdapter` adapters are
    selection-enabled. select() and deselect() are to be overridden with
    display code to mark items as selected or not, if desired.

    For children, there are two directions for selection, from parent to
    children, and from a child up to parent. The default for
    carry_selection_to_children is True, so selection of children will follow
    that of the parent. This can be handy is the SelectableView is treated as a
    container, without its own cosmetic selection effects, and the UI
    reflection of selection is done by the children (if the SelectableView
    contains a combination of ListItemButtons and Labels for a listview
    row item, the buttons will show selection of the row).

    For the other direction, depending on the layout, the parent (the
    SelectableView) may get events such as on_release. Or, if children
    are ListItemButtons, they might get the events. In the second case, if
    children are to fire selection for the parent, do something like the
    following on the child:

        on_release: self.parent.trigger_action(duration=0)

    Depending on the need, on_release could be, among other possibilities,
    on_touch_up. SelectableView, the parent, mixes in ButtonBehavior, which has
    the trigger_action() method.
    '''

    index = NumericProperty(-1)
    '''The index into the underlying data list or the data item this view
    represents.

    :data:`index` is a :class:`~kivy.properties.NumericProperty`, default
    to -1.
    '''

    is_selected = BooleanProperty(False)
    '''A SelectableView instance carries this property, which can be optionally
    kept in sync with the equivalent property in the data item it represents.

    :data:`is_selected` is a :class:`~kivy.properties.BooleanProperty`, default
    to False.
    '''

    carry_selection_to_children = BooleanProperty(True)
    '''If true, select() and deselect() are called on children, if these
    methods are defined.

    .. versionadded:: 1.8

    :data:`carry_selection_to_children` is a
    :class:`~kivy.properties.BooleanProperty`, default to True.
    '''

    def __init__(self, **kwargs):
        super(SelectableView, self).__init__(**kwargs)

    def select(self, *args):
        '''The list item is responsible for updating the display for being
        selected, if desired. Subclasses should call super() to assure that
        is_selected is updated.
        '''
        self.is_selected = True

        if self.carry_selection_to_children:
            for c in self.children:
                if hasattr(c, 'select'):
                    c.select(args)

    def deselect(self, *args):
        '''The list item is responsible for updating the display for being
        deselected, if desired. Subclasses should call super() to assure that
        is_selected is updated.
        '''
        self.is_selected = False

        if self.carry_selection_to_children:
            for c in self.children:
                if hasattr(c, 'deselect'):
                    c.deselect(args)


class ListItemButton(SelectableView, Button):
    ''':class:`~kivy.uix.listview.ListItemButton` mixes
    :class:`~kivy.uix.listview.SelectableView` with
    :class:`~kivy.uix.button.Button` to produce a button suitable for use in
    :class:`~kivy.uix.listview.ListView`.
    '''

    selected_color = ListProperty([1., 0., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1., 0., 0., 1].
    '''

    deselected_color = ListProperty([0., 1., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [0., 1., 0., 1].
    '''

    def __init__(self, **kwargs):
        super(ListItemButton, self).__init__(**kwargs)

        # Set Button bg color to be deselected_color.
        self.background_color = self.deselected_color

    def select(self, *args):
        '''The default cosmetic reflection of selection state is the background
        color. To change, subclass ListItemButton and override this method,
        making sure to call super(), as shown, or make a new subclass of
        SelectableView.
        '''
        self.background_color = self.selected_color
        super(ListItemButton, self).select(args)

    def deselect(self, *args):
        '''The default cosmetic reflection of selection state is the background
        color. To change, subclass ListItemButton and override this method,
        making sure to call super(), as shown, or make a new subclass of
        SelectableView.
        '''
        self.background_color = self.deselected_color
        super(ListItemButton, self).deselect(args)

    def __repr__(self):
        return '<%s text=%s>' % (self.__class__.__name__, self.text)


class CompositeListItem(SelectableView, BoxLayout):
    ''':class:`~kivy.uix.listview.CompositeListItem` mixes
    :class:`~kivy.uix.listview.SelectableView` with :class:`BoxLayout` for a
    generic container-style list item.
    '''

    background_color = ListProperty([1, 1, 1, 1])
    '''ListItem sublasses Button, which has background_color, but
    for a composite list item, we must add this property.

    :data:`background_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1, 1, 1, 1].
    '''

    selected_color = ListProperty([1., 0., 0., 1])
    '''
    :data:`selected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [1., 0., 0., 1].
    '''

    deselected_color = ListProperty([.33, .33, .33, 1])
    '''
    :data:`deselected_color` is a :class:`~kivy.properties.ListProperty`,
    default to [.33, .33, .33, 1].
    '''

    bind_selection_from_children = BooleanProperty(True)
    '''The selectable children of CompositeListItem, depending on use, may need
    to fire selection events for the CompositeListItem. If so, set this to True
    so that bindings are created on instantiation of the children.

    .. versionadded:: 1.8

    '''

    representing_cls = ObjectProperty(None)
    '''The component view class that should represent for the
    composite list item in __repr__().

    .. deprecated:: 1.8

         Can be useful in debugging, but for this, use a debugger, the
         inspector, or the Python inspect module.

    :data:`representing_cls` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    def __init__(self, **kwargs):
        super(CompositeListItem, self).__init__(**kwargs)

        # There is an index to the data item this composite list item view
        # represents. Get it from kwargs and pass it along to children in the
        # loop below.
        index = kwargs['index']

        for cls_dict in kwargs['cls_dicts']:
            cls = cls_dict['cls']
            cls_kwargs = cls_dict.get('kwargs', None)

            if cls_kwargs:
                cls_kwargs['index'] = index

                if 'text' not in cls_kwargs:
                    cls_kwargs['text'] = kwargs['text']

                if 'is_representing_cls' in cls_kwargs:
                    self.representing_cls = cls
            else:
                cls_kwargs = {}
                cls_kwargs['index'] = index
                if 'text' in kwargs:
                    cls_kwargs['text'] = kwargs['text']

            child = cls(**cls_kwargs)

            if self.bind_selection_from_children:
                child.bind(on_release=self.on_release_on_child)

            self.add_widget(child)

    def on_release_on_child(self, *args):
        self.trigger_action(duration=0)

    def select(self, *args):
        super(CompositeListItem, self).select(args)
        self.background_color = self.selected_color

    def deselect(self, *args):
        super(CompositeListItem, self).deselect(args)
        self.background_color = self.deselected_color

    def __repr__(self):
        # NOTE: This conditional, and the method itself, is kept here for
        #       backwards compatibility, because representing_cls is
        #       deprecated. When it is removed, remove this __repr__().
        if self.representing_cls is not None:
            return '<%r>, representing <%s>' % (
                self.representing_cls, self.__class__.__name__)
        else:
            return '<%s>' % (self.__class__.__name__)


Builder.load_string('''
<ListView>:
    container: container
    ScrollView:
        pos: root.pos
        on_scroll_y: root._scroll(args[1])
        do_scroll_x: False
        GridLayout:
            cols: 1
            id: container
            size_hint_y: None
''')


class ListView(AbstractView, EventDispatcher):
    ''':class:`~kivy.uix.listview.ListView` is a primary high-level widget,
    handling the common task of presenting items in a scrolling list.
    Flexibility is afforded by use of a variety of adapters to interface with
    data.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    :class:`~kivy.uix.listview.ListView` also subclasses
    :class:`EventDispatcher` for scrolling.  The event *on_scroll_complete* is
    used in refreshing the main view.

    For a simple list of string items, without selection, use
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`. For list items
    that respond to selection, ranging from simple items to advanced
    composites, use :class:`~kivy.adapters.listadapter.ListAdapter`.  For an
    alternate powerful adapter, use
    :class:`~kivy.adapters.dictadapter.DictAdapter`, rounding out the choice
    for designing highly interactive lists.

    :Events:
        `on_scroll_complete`: (boolean, )
            Fired when scrolling completes.
    '''

    divider = ObjectProperty(None)
    '''[TODO] Not used.
    '''

    divider_height = NumericProperty(2)
    '''[TODO] Not used.
    '''

    container = ObjectProperty(None)
    '''The container is a :class:`~kivy.uix.gridlayout.GridLayout` widget held
    within a :class:`~kivy.uix.scrollview.ScrollView` widget.  (See the
    associated kv block in the Builder.load_string() setup). Item view
    instances managed and provided by the adapter are added to this container.
    The container is cleared with a call to clear_widgets() when the list is
    rebuilt by the populate() method. A padding
    :class:`~kivy.uix.widget.Widget` instance is also added as needed,
    depending on the row height calculations.

    :data:`container` is an :class:`~kivy.properties.ObjectProperty`,
    default to None.
    '''

    row_height = NumericProperty(None)
    '''The row_height property is calculated on the basis of the height of the
    container and the count of items.

    :data:`row_height` is a :class:`~kivy.properties.NumericProperty`,
    default to None.
    '''

    item_strings = ListProperty([])
    '''If item_strings is provided, create an instance of
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` with this list
    of strings, and use it to manage a no-selection list.

    :data:`item_strings` is a :class:`~kivy.properties.ListProperty`,
    default to [].
    '''

    scrolling = BooleanProperty(False)
    '''If the scroll_to() method is called while scrolling operations are
    happening, a call recursion error can occur. scroll_to() checks to see that
    scrolling is False before calling populate(). scroll_to() dispatches a
    scrolling_complete event, which sets scrolling back to False.

    :data:`scrolling` is a :class:`~kivy.properties.BooleanProperty`,
    default to False.
    '''

    _index = NumericProperty(0)
    _sizes = DictProperty({})
    _count = NumericProperty(0)

    _wstart = NumericProperty(0)
    _wend = NumericProperty(None, allownone=True)

    __events__ = ('on_scroll_complete', )

    def __init__(self, **kwargs):

        # Check for an adapter argument. If it doesn't exist, we check for
        # item_strings in use with SimpleListAdapter to make a simple list.
        if 'adapter' not in kwargs:

            if 'item_strings' not in kwargs:
                # Could be missing, or it could be that the ListView is
                # declared in a kv file. If kv is in use, and item_strings is
                # declared there, then item_strings will not be set until after
                # __init__(). So, the data=[] set will temporarily serve for
                # SimpleListAdapter instantiation, with the binding to
                # item_strings_changed() handling the eventual set of the
                # item_strings property from the application of kv rules.
                list_adapter = SimpleListAdapter(data=[],
                                                 cls=Label)
            else:
                list_adapter = SimpleListAdapter(data=kwargs['item_strings'],
                                                 cls=Label)
            kwargs['adapter'] = list_adapter

        super(ListView, self).__init__(**kwargs)

        if self.adapter:

            self.adapter.bind(on_data_change=self.data_changed)

        self._trigger_populate = Clock.create_trigger(self._spopulate, -1)
        self._trigger_reset_populate = \
            Clock.create_trigger(self._reset_spopulate, -1)

        self.bind(size=self._trigger_populate,
                  pos=self._trigger_populate,
                  item_strings=self.item_strings_changed,
                  adapter=self.adapter_changed)
                  #adapter=self._trigger_populate)

        #self.adapter.bind(data=self.data_changed)

    def adapter_changed(self, *args):

        if self.adapter:
            Logger.debug(('ListView: '
                          'and the adapter changed to ') + str(self.adapter))
            self.adapter.bind(on_data_change=self.data_changed)

            self._trigger_populate()

    # Reset data when item_strings is set in a kv template, or when if
    # item_strings is changed generally.
    def item_strings_changed(self, *args):
        self.adapter.data = self.item_strings

    def _scroll(self, scroll_y):

        if self.row_height is None:
            return
        self._scroll_y = scroll_y
        scroll_y = 1 - min(1, max(scroll_y, 0))
        container = self.container
        mstart = (container.height - self.height) * scroll_y
        mend = mstart + self.height

        # convert distance to index
        rh = self.row_height
        istart = int(ceil(mstart / rh))
        iend = int(floor(mend / rh))

        istart = max(0, istart - 1)
        iend = max(0, iend - 1)

        if istart < self._wstart:
            rstart = max(0, istart - 10)
            self.populate(rstart, iend)
            self._wstart = rstart
            self._wend = iend
        elif iend > self._wend:
            self.populate(istart, iend + 10)
            self._wstart = istart
            self._wend = iend + 10

    def _spopulate(self, *args):
        self.populate()
        # simulate the scroll again, only if we already scrolled before
        # the position might not be the same, mostly because we don't know the
        # size of the new item.
        if hasattr(self, '_scroll_y'):
            self._scroll(self._scroll_y)

    def _reset_spopulate(self, *args):
        self._wend = None
        self.populate()
        # simulate the scroll again, only if we already scrolled before
        # the position might not be the same, mostly because we don't know the
        # size of the new item.
        if hasattr(self, '_scroll_y'):
            self._scroll(self._scroll_y)

    def populate(self, istart=None, iend=None):

        container = self.container
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()

        # guess only ?
        if iend is not None:

            # fill with a "padding"
            fh = 0
            for x in range(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real item_view
            index = istart
            while index <= iend:
                item_view = self.adapter.get_view(index)
                index += 1
                if item_view is None:
                    continue
                sizes[index] = item_view.height
                container.add_widget(item_view)
        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                sizes[index] = item_view.height
                index += 1
                count += 1
                container.add_widget(item_view)
                available_height -= item_view.height
                real_height += item_view.height

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.height = \
                    real_height / count * self.adapter.get_count()
                if self.row_height is None:
                    self.row_height = real_height / count

    def scroll_to(self, index=0):

        if not self.scrolling:
            self.scrolling = True
            self._index = index
            self.populate()
            self.dispatch('on_scroll_complete')

    def scroll_to_end(self, index=0):

        # TODO: This stops working after a manual scroll.

        if not self.scrolling:
            available_height = self.height
            index = len(self.adapter.data) - 1

            while available_height > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                index -= 1
                available_height -= item_view.height

            self.scroll_to(index + 1)

    def scroll_after_add(self):

        if not self.scrolling:
            available_height = self.height
            index = self._index

            Logger.debug('ListView: self._index = {0}'.format(index))
            Logger.debug('ListView: available_height = {0}'.format(
                                                        available_height))

            while available_height > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                index += 1
                available_height -= item_view.height

            Logger.debug('ListView: available_height = {0}'.format(
                                                        available_height))

            if available_height <= 0:
                self._index += 1

            self.scrolling = True
            self.populate()
            self.dispatch('on_scroll_complete')

    def on_scroll_complete(self, *args):
        self.scrolling = False

    def data_changed(self, *args):

        # list and dict change ops:
        #
        #      OOL == OpObservableList
        #
        #            set ops:
        #
        #                OOL_setitem  - single item set
        #                OOL_setslice - range of items
        #
        #            add ops:
        #
        #                OOL_iadd   - adds items to end
        #                OOL_imul   - adds items to end
        #                OOL_append - adds items to end
        #                OOL_insert - insert
        #                OOL_extend - adds items to end
        #
        #            delete ops:
        #
        #                OOL_delitem  - single item
        #                OOL_delslice - multiple items
        #                OOL_remove   - single item
        #                OOL_pop      - single item
        #
        #            sort ops:
        #
        #                OOL_sort
        #                OOL_reverse
        #
        #       OOD == OpObservableDict
        #
        #            set op:
        #
        #                OOD_setattr     - single item set
        #                    (We do not receive.)
        #                OOD_setitem_set - single item set
        #                    (We receive the OOD op directly.)
        #
        #            add ops:
        #
        #                OOD_setitem_add - single item
        #                OOD_setdefault  - single item
        #                OOD_update      - single or multiple items
        #
        #                    (We receive OOL ops, from changes to
        #                     sorted_keys fired by these):
        #
        #            delete ops:
        #
        #                OOD_delitem     - single item
        #                OOD_pop         - single item
        #                OOD_popitem     - single item
        #                  [NOTE: OOD_popitem is performed as OOL_delitem]
        #                OOD_clear       - all items deleted
        #
        #                    (We receive OOL ops, from changes to
        #                     sorted_keys fired by these):

        # Callbacks could come here from either OOL or OOD, and there could
        # be differences in handling.

        op_info = self.adapter.op_info

        op = op_info.op_name

        if isinstance(op_info, ListOpInfo):
            start_index = op_info.start_index
            end_index = op_info.end_index
            Logger.debug(("ListView: op_info -- {0} "
                          "start_index: {1}, end_index: {2}").format(
                              op, start_index, end_index))
        elif isinstance(op_info, DictOpInfo):
            keys = op_info.keys
            start_index, end_index = self.adapter.additional_op_info
            Logger.debug(("ListView: op_info -- {0} "
                          "keys: {0}, start_index: {1}, end_index: {2}").format(
                              op, keys, start_index, end_index))

        # Otherwise, we may have item_views as children of self.container
        # that should be removed.

        if op in ['OOL_setitem', 'OOD_setitem_set', ]:

            widget_index = -1

            for i, item_view in enumerate(self.container.children):
                if item_view.index == start_index:
                    widget_index = i
                    break

            if widget_index >= 0:
                widget = self.container.children[widget_index]
                self.container.remove_widget(widget)

                item_view = self.adapter.get_view(start_index)
                self.container.add_widget(item_view, widget_index)

        elif op in ['OOL_setslice', ]:

            len_data = len(self.adapter.data)

            slice_indices = range(start_index, end_index + 1)

            len_slice_indices = len(slice_indices)

            widget_indices = []

            for i, item_view in enumerate(self.container.children):
                if item_view.index in slice_indices:
                    widget_indices.append(i)
                    if len(widget_indices) == len(slice_indices):
                        break

            for widget_index in reversed(sorted(widget_indices)):
                widget = self.container.children[widget_index]
                self.container.remove_widget(widget)

            add_index = min(widget_indices)

            for slice_index in slice_indices:
                item_view = self.adapter.get_view(slice_index)
                self.container.add_widget(item_view, add_index)

        elif op in ['OOL_append',
                    'OOL_extend',
                    'OOD_setattr',
                    'OOD_setitem_add',
                    'OOD_setdefault',
                    'OOD_update']:

            self.scroll_to_end()

            #self.scroll_after_add()

            #self.scrolling = True
            #self.populate()
            #self.dispatch('on_scroll_complete')

        elif op in ['OOL_delitem',
                    'OOL_delslice',
                    'OOL_remove',
                    'OOL_pop',
                    'OOD_delitem',
                    'OOD_clear',
                    'OOD_pop', ]:

            # NOTE: There is no OOD_popitem here, because it is performed as
            #       a OOD_delitem.

            deleted_indices = range(start_index, end_index + 1)

            for item_view in self.container.children:
                if (hasattr(item_view, 'index')
                        and item_view.index in deleted_indices):
                    self.container.remove_widget(item_view)

            self.scrolling = True
            self.populate()
            self.dispatch('on_scroll_complete')

        elif op == 'OOL_insert':

            #self.scroll_after_add()
            self.scrolling = True
            self.populate()
            self.dispatch('on_scroll_complete')

        elif op in ['OOL_sort', 'OOL_reverse', 'OOL_set', ]:

            self.container.clear_widgets()

            self.scrolling = True
            self.populate()
            self.dispatch('on_scroll_complete')

        else:

            Logger.debug('ListView: unhandled data change op ' + str(op))
