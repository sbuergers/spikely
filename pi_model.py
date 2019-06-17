""" Model associated with user constructed pipeline of elements.

Supports the main UI using MVC pattern semantics.  This class proxies the
actual concatenation (pipeline) of SpikeInterface element space of extractors,
pre-processors, sorters, and post-processors.
"""

import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw

import copy
# import threading

import config


class SpikePipelineModel(qc.QAbstractListModel):
    """Used by UI to display pipeline of elements in a decoupled fashion"""

    def __init__(self, element_model):
        """TBD."""
        super().__init__()

        # Underlying data structure proxied by model
        self._elements = []

        self._decorations = [
            qg.QIcon("bin/EXTR.png"),
            qg.QIcon("bin/PREP.png"),
            qg.QIcon("bin/SORT.png"),
            qg.QIcon("bin/POST.png")
        ]

    # Methods sub-classed from QAbstractListModel
    def rowCount(self, parent):
        return len(self._elements)

    def data(self, mod_index, role=qc.Qt.DisplayRole):
        """ Retrieves data facet (role) from model based on positional index"""
        result = None

        if mod_index.isValid() and mod_index.row() < len(self._elements):
            element = self._elements[mod_index.row()]
            if role == qc.Qt.DisplayRole or role == qc.Qt.EditRole:
                result = element.name
            elif role == qc.Qt.DecorationRole:
                result = self._decorations[element.interface_id]
            elif role == config.ELEMENT_ROLE:
                result = element

        return result

    # Convenience methods used by class APIs
    def _has_instance(self, interface_id):
        for element in self._elements:
            if element.interface_id == interface_id:
                return True
        """Generator expression equivalent for future reference
        return sum(1 for ele in self._elements if
        ele.interface_id == interface_id)"""

    def _swap(self, list, pos1, pos2):
        list[pos1], list[pos2] = list[pos2], list[pos1]

    # Methods for other parts of Spikely to manipulate pipeline
    def run(self):
        """Call SpikeInterface APIs on elements in pipeline"""
        try:
            input_payload = None
            element_count = len(self._elements)
            '''
            progress = qw.QProgressDialog(
                'Running the pipeline...', 'Cancel', 0,
                element_count, config.main_window)
            progress.setMinimumDuration(0)
            progress.setWindowModality(qc.Qt.WindowModal)
            '''
            for i in range(0, element_count):
                # progress.setValue(i)
                next_element = (
                    self._elements[i+1] if i < (element_count - 1) else None
                )
                input_payload = self._elements[i].run(
                    input_payload, next_element
                )
            # progress.setValue(element_count)
        except KeyError:
            qw.QMessageBox.warning(
                config.main_window, 'Run Failure',
                'One or more invalid element parameter values.  Please ensure '
                'all parameter values are set properly for all elements in '
                'the pipeline.')
        except Exception as e:
            qw.QMessageBox.warning(
                config.main_window, 'Run Failure', e)
        else:
            msg = ('Run successful' if element_count > 0 else
                   'Nothing to run')
            config.status_bar.showMessage(msg, config.STATUS_MSG_TIMEOUT)

    def clear(self):
        """Removes all elements from pipeline"""
        if len(self._elements):
            self.beginResetModel()
            self._elements.clear()
            self.endResetModel()
        else:
            config.status_bar.showMessage('Nothing to clear',
                                          config.STATUS_MSG_TIMEOUT)

    def add_element(self, element):
        """ Adds element at top of stage associated w/ element interface_id"""
        # Only allow one Extractor or Sorter
        if (element.interface_id == config.EXTRACTOR or
                element.interface_id == config.SORTER):
            if self._has_instance(element.interface_id):
                config.status_bar.showMessage(
                    "Only one instance of that element type allowed",
                    config.STATUS_MSG_TIMEOUT)
                return
        # A bit hacky since it assumes order of interface_id constants
        i = 0
        while (i < len(self._elements) and
                element.interface_id >= self._elements[i].interface_id):
            i += 1
        self.beginInsertRows(qc.QModelIndex(), i, i)
        # Need a deep copy of element to support multi-instance element use
        self._elements.insert(i, copy.deepcopy(element))
        self.endInsertRows()

    def move_up(self, element):
        i = self._elements.index(element)
        # Elements confined to their stage
        if (i > 0 and self._elements[i].interface_id
                == self._elements[i-1].interface_id):
            self.beginMoveRows(qc.QModelIndex(), i, i, qc.QModelIndex(), i-1)
            self._swap(self._elements, i, i-1)
            self.endMoveRows()
        else:
            config.status_bar.showMessage(
                "Cannot move element any higher", config.STATUS_MSG_TIMEOUT)

    def move_down(self, element):
        i = self._elements.index(element)
        # Elements confined to their stage
        if (i < (len(self._elements) - 1) and
                self._elements[i].interface_id
                == self._elements[i+1].interface_id):
            # beginMoveRows behavior is fubar if move down from source to dest
            self.beginMoveRows(qc.QModelIndex(), i+1, i+1, qc.QModelIndex(), i)
            self._swap(self._elements, i, i+1)
            self.endMoveRows()
        else:
            config.status_bar.showMessage(
                "Cannot move element any lower", config.STATUS_MSG_TIMEOUT)

    def delete(self, element):
        index = self._elements.index(element)
        self.beginRemoveRows(qc.QModelIndex(), index, index)
        self._elements.pop(index)
        self.endRemoveRows()