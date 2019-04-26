"""The view-control widget set for constructing the active pipeline.

The Construct Pipeline view-control consists of widgets responsible for
constructing the active pipeline by inserting, deleting, or moving elements
within the active pipeline.
"""

import PyQt5.QtWidgets as qw

from el_model import SpikeElement
import config


class ConstructPipelineView(qw.QGroupBox):
    """QGroupBox containing the view-control widget set

    No public methods other than constructor.  All other activites
    of object are triggered by user interaction with sub widgets.
    """

    def __init__(self, pipeline_model, element_model):
        super().__init__("Construct Pipeline")

        self._pipeline_model = pipeline_model
        self._pipeline_view = qw.QListView(self)
        self._element_model = element_model

        self._init_ui()

    def _init_ui(self):
        """Assembles the individual widgets into the widget-set.

        The ConstructPipelineView consists of three separate UI assemblies
        stacked top to bottom: element selection, pipeline element list view,
        and pipeline element manipulation controls (move up, delete, move down)
        """
        # Lay out view from top to bottom of group box
        self.setLayout(qw.QVBoxLayout())

        self.layout().addWidget(self._element_insertion())
        self.layout().addWidget(self._pipeline_list())
        self.layout().addWidget(self._pipeline_commands())

        """This funky bit of code is an example of how a class method
        with a specific signature can be bound to an instance of that class
        using a type index, in this case QModelIndex"""
        # treeView.clicked[QModelIndex].connect(self.clicked)

    def _element_insertion(self):
        """Select for and insert elements into pipeline."""

        ui_frame = qw.QFrame()
        ui_frame.setLayout(qw.QHBoxLayout())

        # Out of order declaration needed as forward reference
        ele_cbx = qw.QComboBox(self)

        stage_cbx = qw.QComboBox()
        ui_frame.layout().addWidget(stage_cbx)

        # Change ele_cbx contents when user makes stage_cbx selection
        def stage_cbx_changed(index):
            ele_cbx.clear()
            for element in SpikeElement.available_elements():
                # stage_cbx items store type ID associated w/ name
                if element.type == stage_cbx.itemData(index):
                    # ele_cbx items store element object w/ name
                    ele_cbx.addItem(element.name, element)
        stage_cbx.currentIndexChanged.connect(stage_cbx_changed)

        # Must come after currentIndexChanged.connect to invoke callback
        stage_cbx.addItem('Extractors', config.EXTRACTOR)
        stage_cbx.addItem('Pre-Processors', config.PRE_PROCESSOR)
        stage_cbx.addItem('Sorters', config.SORTER)
        stage_cbx.addItem('Post-Processors', config.POST_PROCESSOR)

        # Layout after stage_cbx, but declared first as fwd reference
        ui_frame.layout().addWidget(ele_cbx)

        add_button = qw.QPushButton("Add Element")

        def _add_element_clicked():
            # Takes advantage of actual element reference stored in ele_cbx
            self._pipeline_model.add_element(ele_cbx.currentData())
        add_button.clicked.connect(_add_element_clicked)

        ui_frame.layout().addWidget(add_button)

        return ui_frame

    def _pipeline_list(self):
        # MVC in action - connect View (widget) to Model
        self._pipeline_view.setModel(self._pipeline_model)

        self._pipeline_view.setSelectionMode(
            qw.QAbstractItemView.SingleSelection)

        # Links element (ce_view) and pipeline (cp_view) views
        def list_selection_changed(selected, deselected):
            if selected.indexes():
                # Retrieve selected element from pipeline model
                element = self._get_selected_element()
                # Link selected element to element property editor
                self._element_model.element = element
            else:
                self._element_model.element = None
        self._pipeline_view.selectionModel().selectionChanged.connect(
            list_selection_changed)

        return self._pipeline_view

    def _pipeline_commands(self):
        ui_frame = qw.QFrame()
        ui_frame.setLayout(qw.QHBoxLayout())

        # Move Up element button and associated action
        mu_btn = qw.QPushButton("Move Up")
        ui_frame.layout().addWidget(mu_btn)

        def move_up_clicked():
            element = self._get_selected_element()
            if element is None:
                config.status_bar.showMessage(
                    "Nothing to move up", config.TIMEOUT)
            else:
                self._pipeline_model.move_up(element)
        mu_btn.clicked.connect(move_up_clicked)

        # Move Down element button and associated action
        md_btn = qw.QPushButton("Move Down")
        ui_frame.layout().addWidget(md_btn)

        def move_down_clicked():
            element = self._get_selected_element()
            if element is None:
                config.status_bar.showMessage(
                    "Nothing to move down", config.TIMEOUT)
            else:
                self._pipeline_model.move_down(element)
        md_btn.clicked.connect(move_down_clicked)

        # Delete element button and associated action
        de_btn = qw.QPushButton("Delete")
        ui_frame.layout().addWidget(de_btn)

        def delete_clicked():
            element = self._get_selected_element()
            if element is None:
                config.status_bar.showMessage(
                    "Nothing to delete", config.TIMEOUT)
            else:
                self._pipeline_model.delete(element)
        de_btn.clicked.connect(delete_clicked)

        return ui_frame

    def _get_selected_element(self):
        """ Convenience function to retrieve selected element in pipe view"""
        element = None
        model = self._pipeline_view.selectionModel()
        if model.hasSelection():
            index = model.selectedIndexes()[0]
            element = self._pipeline_model.data(index, config.ELEMENT_ROLE)
        return element
