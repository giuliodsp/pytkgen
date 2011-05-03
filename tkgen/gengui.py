#
# Copyright (c) 2011. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301  USA

from Tkconstants import W, E, N, S
from Tkinter import Tk, IntVar, StringVar
import Tkinter
import json


'''
Simple class which wraps Tk and uses some JSON to construct a GUI...

Created on Apr 21, 2011

@author: tmetsch
'''
class Generator(object):

    menu = None

    def initialize(self, filename, title='Tk'):
        """
        Initialize a Tk root and created the UI from a JSON file.

        Returns the Tk root.
        """
        self.root = Tk()
        self.root.title(title)

        ui_file = open(filename)
        ui = json.load(ui_file)

        self.create_widgets(self.root, ui)

        return self.root

    def create_widgets(self, parent, items):
        """
        Creates a set of Tk widgets.
        """
        for name in items.keys():
            current = items[name]
            if isinstance(current, dict) and not self._contains_list(current) and not self._contains_dict(current):
                self._create_widget(name, parent, current)

            elif isinstance(current, dict) and self._contains_list(current):
                widget = self._create_widget(name, parent, current)

                self.create_widgets(widget, current)
            elif isinstance(current, dict) and self._contains_dict(current):
                widget = self._create_widget(name, parent, current)

                self.create_widgets(widget, current)
            elif isinstance(current, list):
                for item in current:
                    self.create_widgets(parent, {name:item})

    def _contains_dict(self, items):
        """
        Checks if a set of items contains a dictionary.

        items -- The set of items to test.
        """
        result = False
        for item in items.keys():
            if isinstance(items[item], dict):
                result = True
                break
        return result

    def _contains_list(self, items):
        """
        Checks if a set of items contains a list.

        items -- The set of items to test.
        """
        result = False
        for item in items.keys():
            if isinstance(items[item], list) and item is not item.lower():
                # the .lower check ensures that I can have attribute lists
                result = True
                break
        return result

    def _create_widget(self, name, parent, desc):
        """
        Tries to resolve the widget from Tk and create it.

        Returns the newly created widget.

        name -- Name of the widget.
        parent -- The parent widget.
        desc -- Dictionary containing the description for this widget.
        """
        row, column, columnspan, rowweight, colweight, options = self._get_options(desc)

        try:
            widget_factory = getattr(Tkinter, name)
        except AttributeError:
            try:
                import ttk
                widget_factory = getattr(ttk, name)
            except AttributeError:
                raise AttributeError('Neither Tkinter nor ttk have a widget named: ', name)

        widget = widget_factory(parent, **options)

        widget.grid(row=row,
                    column=column,
                    columnspan=columnspan,
                    sticky=N + E + W + S,
                    padx=2,
                    pady=2)

        # propaget size settings when needed.
        if 'width' in options or 'height' in options:
            widget.grid_propagate(0)

        # set parent weight of the cells
        if rowweight > 0:
            parent.rowconfigure(row, weight=rowweight)
        if colweight > 0:
            parent.columnconfigure(column, weight=colweight)

        return widget

    def _get_options(self, dictionary):
        """
        Extracts the needed options from a dictionary.

        dictionary -- Dictionary with all the options in it.
        """
        options = {}
        row = 0
        column = 0
        colspan = 1
        rowweight = 0
        colweight = 0

        if 'row' in dictionary:
            row = dictionary['row']
            dictionary.pop('row')
        if 'column' in dictionary:
            column = dictionary['column']
            dictionary.pop('column')
        if 'columnspan' in dictionary:
            colspan = dictionary['columnspan']
            dictionary.pop('columnspan')
        if 'rowweight' in dictionary:
            rowweight = dictionary['rowweight']
            dictionary.pop('rowweight')
        if 'colweight' in dictionary:
            colweight = dictionary['colweight']
            dictionary.pop('colweight')
        if 'weight' in dictionary:
            colweight = dictionary['weight']
            rowweight = dictionary['weight']
            dictionary.pop('weight')
        for key in dictionary.keys():
            if not isinstance(dictionary[key], dict) and not isinstance(dictionary[key], list):
                options[str(key)] = str(dictionary[key])
            elif isinstance(dictionary[key], list) and key == key.lower():
                # so we have an attribute list...
                options[str(key)] = str(dictionary[key])

        return row, column, colspan, rowweight, colweight, options

    def _find_by_name(self, parent, name):
        """
        Recursively find a item by name.

        Needs to be recursive because of frames in frames in frames in ... :-)
        """
        items = parent.children
        result = None
        if name in items.keys():
            return items[name]
        else:
            for key in items.keys():
                if hasattr(items[key],
                           'children') and len(items[key].children) > 0:
                    result = self._find_by_name(items[key], name)
                    if result is not None:
                        break

        return result

    ##
    # Rest is public use :-)
    ##

    def button(self, name, cmd, focus=False):
        """
        Associate a Tk widget with a function.

        name -- Name of the widget.
        cmd -- The command to trigger.
        focus -- indicates wether this item has the focus.
        """
        item = self._find_by_name(self.root, name)
        item.config(command=cmd)

        if focus:
            item.focus_set()

    def checkbox(self, name, focus=False):
        """
        Associates a IntVar with a checkbox.

        name -- Name of the Checkbox.
        focus -- indicates wether this item has the focus.
        """
        c = IntVar()
        item = self._find_by_name(self.root, name)
        item.config(variable=c)

        if focus:
            item.focus_set()

        return c

    def entry(self, name, key=None, cmd=None, focus=False):

        """
        Returns the text of a TK widget.

        name -- Name of the Tk widget.
        key -- Needed if a key should be bound to this instance.
        cmd -- If key is defined cmd needs to be defined - will be triggered when the key is pressed.
        focus -- Indicates wether this entry should take focus.
        """
        v = StringVar()

        item = self._find_by_name(self.root, name)
        item.config(textvariable=v)

        if focus:
            item.focus_set()

        if key is not None and cmd is not None:
            item.bind(key, cmd)

        return v

    def label(self, name):
        """
        Associate a StringVar with a label.

        name -- Name of the Label.
        """
        v = StringVar()
        item = self._find_by_name(self.root, name)
        item.config(textvariable=v)
        return v

    def toplevel(self, filename, title='Dialog'):
        """
        Open a Toplevel widget.

        parent -- The parent notebook widget instance.
        title -- The title for the dialog.
        """
        dialog = Tkinter.Toplevel()
        dialog.title(title)
        ui_file = open(filename)
        dialog_def = json.load(ui_file)
        self.create_widgets(dialog, dialog_def)
        dialog.grid()

    def notebook(self, parent, filename, name='Tab'):
        """
        Add a tab to a tkk notebook widget.

        parent -- The parent notebook widget instance.
        filename -- The file which describes the content of the tab.
        name -- The name of the tab.
        """
        frame = Tkinter.Frame()
        ui_file = open(filename)
        tab1_def = json.load(ui_file)
        self.create_widgets(frame, tab1_def)
        parent.add(frame, text=name)

    def treeview(self, treeview, name, values, parent='', index=0):
        """
        Adds an item to a treeview.

        treeview -- The treeview to add the items to.
        name -- The name of the value.
        values -- The values itself.
        parent -- Default will create root items, specify a parent to create a leaf.
        index -- If index < current # of items - insert at the top (Default: 0).
        """
        return treeview.insert(parent, index, text=name, values=values)

    def find(self, name):
        """
        Find a Tk widget by name and return it.
        """
        result = self._find_by_name(self.root, name)
        if result is None:
            raise KeyError('Tkinter widget with name "' + name + '" not found.')
        return result

    def create_menu(self, commands, name=None, parent=None, popup=False):
        """
        Creates a menu(entry) if non is available. Returns the created menu so you can define submenus.

        commands -- dict with 'label':'command' structure.
        name -- Needs to be provided if it is a dropdown or submenu.
        parent -- Needs to be provided if it is a submenu.
        popup -- indicates if it is an popup menu or not (Default: False)
        """
        if self.menu is None and popup is False:
            # If no menu exists create one and add it to the Tk root.
            self.menu = Tkinter.Menu(self.root)
            self.root.config(menu=self.menu)

        if name is None and parent is None and popup is False and len(commands.keys()) > 0:
            # Just create a Menu entry.
            for key in commands:
                self.menu.add_command(label=key, command=commands[key])
            return self.menu
        elif name is not None and popup is False and len(commands.keys()) > 0:
            if parent is None:
                # Create a top-level drop down menu.
                tmp_menu = Tkinter.Menu(self.menu)
                self.menu.add_cascade(label=name, menu=tmp_menu)
            else:
                # Create a submenu.
                tmp_menu = Tkinter.Menu(parent)
                parent.add_cascade(label=name, menu=tmp_menu)

            for key in commands:
                tmp_menu.add_command(label=key, command=commands[key])

            return tmp_menu
        elif popup is True and len(commands.keys()) > 0:
            tmp_menu = Tkinter.Menu(self.root)
            for key in commands:
                tmp_menu.add_command(label=key, command=commands[key])

            return tmp_menu
        else:
            raise AttributeError('Invalid parameters provided')
