import sys
import pkg_resources

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg

import spikely as sl
from spikely import file_menu
from spikely import config as cfg

from spikely.version import __version__


class SpikelyMainWindow(qw.QMainWindow):
# Parent UI for application delegates to subwindow views/models
    def __init__(self):
        super().__init__()

        # Subwindows Views need underlying Model references
        self._parameter_model = sl.ParameterModel()
        self._pipeline_model = sl.PipelineModel(
            self._parameter_model)
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("spikely")
        self.setGeometry(100, 100, 1152, 472)

        spikely_png_path = pkg_resources.resource_filename(
            'spikely.resources', 'spikely.png')

        self.setWindowIcon(qg.QIcon(spikely_png_path))
        self.statusBar().addPermanentWidget(
            qw.QLabel("Version " + __version__))

        menu_bar = self.menuBar()
        menu = file_menu.create_file_menu(self, self._pipeline_model)
        menu_bar.addMenu(menu)

        main_frame = qw.QFrame()
        self.setCentralWidget(main_frame)
        main_frame.setLayout(qw.QVBoxLayout())

        # Push subwindows down - create negative space below menu bar
        main_frame.layout().addStretch(1)

        pipe_param_splitter = qw.QSplitter()
        pipe_param_splitter.setChildrenCollapsible(False)

        # Subwindows for element pipeline and current element parameters
        pipe_param_splitter.addWidget(sl.PipelineView(
            self._pipeline_model, self._parameter_model))
        pipe_param_splitter.addWidget(sl.ParameterView(
            self._pipeline_model, self._parameter_model))
        pipe_param_splitter.setSizes([328, 640])
        main_frame.layout().addWidget(pipe_param_splitter)

        # Subwindow at bottom for pipeline operations (run, clear, queue)
        main_frame.layout().addWidget(sl.OperationView(
            self._pipeline_model, self._parameter_model))


def launch_spikely():
    app = qw.QApplication(sys.argv)
    cfg.main_window = SpikelyMainWindow()
    cfg.status_bar = cfg.main_window.statusBar()
    cfg.main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch_spikely()
