from collections import OrderedDict
from functools import partial

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from .dep_resolv import dependency_graph, calculate_dependencies

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = str


#
# Helper functions functions to setup the GUI
#


class SiQtMixin(object):
    """A mixin to extend ``QtWidgets.QMainWindow``

    This class adds a few convinient functions to
    ``QtWidgets.QMainWindow`` to add actions and generate menus
    """

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,
                      signal="triggered"):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtWidgets.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def menu_generator(self, name, label, elements):
        """Generate menu"""
        # File menu
        self.menu[name] = self.menuBar().addMenu("&"+label)
        self.menu[name].elmts = elements

        def show_menu(action):
            def f(value):
                if value:
                    action.setDisabled(False)
                    action.setEnabled(True)
                else:
                    action.setDisabled(True)
                    action.setEnabled(False)

            return f

        idx = 1
        for key, menu_el in elements.items():
            if menu_el is None:
                self.menu[name].addSeparator()
                continue

            pars = self.menu[name].elmts[key]

            if name == 'view':
                pars['slot'] = self.on_view_handler(key)
                if idx < 10:
                    pars['shortcut'] = 'Ctrl+{}'.format(idx)

            if 'slot' not in pars:
                pars['slot'] = getattr(self, 'on_'+key)

            tpars = pars.copy()
            for tkey in ['depends', 'enabled']:
                if tkey in tpars:
                    del tpars[tkey]
            action = self.create_action(**tpars)
            # has some dependecies meaning can't be used initially
            if pars['depends']:

                action.setDisabled(True)

            if 'enabled' in pars and not pars['enabled']:
                action.setDisabled(True)

            self.menu[name].addAction(action)

            pars['qtobject'] = action
            pars['show'] = show_menu(action)
            idx += 1

    def set_dep_flag_recursive(self, key, value, sync=False):
        """ Change status for a dependent field,
        and pull all the fields that are dependent on it.
        """
        self.dep_flags[key] = value
        for dkey in dependency_graph(key, self.dep_graph):
            self.dep_flags[dkey] = False
        if sync:
            calculate_dependencies(self)


class SiqtItem(dict):
    """A thin wrapper around any QtObject

    Supports dependencies, a straightforward way of getting / setting
    value.
    """

    def __init__(self, qtobj, position=None,
                 depends=[], dtype=str, layout=None, **args):
        if isinstance(qtobj, str):
            # when given a string, convert to a label
            qtobj = QtWidgets.QLabel(qtobj)
        self.dtype = dtype
        if isinstance(qtobj, QtWidgets.QLineEdit) and dtype != str:
            if dtype in [float]:  # , np.float]:
                validator = QtGui.QDoubleValidator()
                qtobj.setValidator(validator)
                args['validator'] = validator
            elif dtype in [int]:  # , np.int]:
                validator = QtGui.QIntValidator()
                qtobj.setValidator(validator)
                args['validator'] = validator
        if isinstance(qtobj, QtWidgets.QComboBox) and 'choices' in args:
            args['choices'] = OrderedDict(args['choices'])
            for key, val in args['choices'].items():
                qtobj.addItem(QString(key), val)

        super().__init__(qtobj=qtobj, depends=depends, **args)
        if layout is not None and position is not None:
            layout.addWidget(qtobj, *position)

    @classmethod
    def with_layout(cls, layout):
        """ Pre-initialize SiqtItem with layout """
        return partial(cls, layout=layout)

    def set_text(self, value):
        value = QString(str(value))
        self['qtobj'].setText(value)

    def set_choices(self, choices):
        control = self['qtobj']
        if not isinstance(control,
                          (QtWidgets.QComboBox, QtWidgets.QListWidget)):
            raise NotImplementedError('set_choices is only valid '
                                      'for a QComboBox element')

        control.blockSignals(True)
        if isinstance(control, QtWidgets.QComboBox):
            choices = OrderedDict(choices)
            for idx in range(control.count()):
                control.removeItem(0)

            for key, val in choices.items():
                control.addItem(key, val)
        elif isinstance(control, QtWidgets.QListWidget):
            control.clear()
            for key in sorted(choices):
                control.addItem(key)

        self['choices'] = choices
        control.blockSignals(False)

    def set_value(self, value):
        qtobj = self['qtobj']
        if isinstance(qtobj, QtWidgets.QCheckBox):
            if value:
                value = QtCore.Qt.Checked
            else:
                value = QtCore.Qt.Unchecked
            qtobj.setCheckState(value)
        elif isinstance(qtobj, (QtWidgets.QComboBox, QtWidgets.QListWidget)):
            self.set_choices(value)
        elif isinstance(qtobj, QtWidgets.QSlider):
            raise NotImplementedError
        else:
            qtobj.setText(str(value))

    @property
    def value(self):
        """Get the value of the QtObject"""
        qtobj = self['qtobj']
        if isinstance(qtobj, QtWidgets.QCheckBox):
            return qtobj.isChecked()
        elif isinstance(qtobj, QtWidgets.QComboBox):
            key = str(qtobj.currentText())
            return self['choices'][key]
        elif isinstance(qtobj, QtWidgets.QSlider):
            return self.dtype(qtobj.value())
        elif isinstance(qtobj, QtWidgets.QListWidget):
            return [str(el.text()) for el in qtobj.selectedItems()]
        else:
            val = str(qtobj.text())
            if not val and self.dtype != str:
                val = 0
            return self.dtype(val)

    def __getattr__(self, name):
        """Fallback to the original qtobject methods
        if the method was not explicitly defined"""

        return getattr(self['qtobj'],  name)
