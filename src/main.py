# Edit by Chemical118

import os
import sys

from ryven.main.nodes_package import NodesPackage

from ryven.main.utils import abs_path_from_package_dir
from ryven.NENV import init_node_env
from ryven.NWENV import init_node_widget_env

# # change directory to this file's location
# os.chdir(os.path.dirname(os.path.realpath(__file__)))

# turn off for debugging
REDIRECT_CONSOLE_OUTPUT = True


def run(qt_app=None, qt_api='pyside2',
        show_dialog=True, gui_parent=None, window_title='Ryven',
        window_theme_name='dark', flow_theme=None,
        redirect_console_output=REDIRECT_CONSOLE_OUTPUT):

    # QtPy API
    os.environ['QT_API'] = qt_api

    # init environment
    os.environ['RYVEN_MODE'] = 'gui'
    init_node_env()
    init_node_widget_env()

    # import gui sources
    from ryven.gui.main_console import init_main_console
    from ryven.gui.startup_dialog.StartupDialog import StartupDialog
    from ryven.gui.main_window import MainWindow
    from ryven.gui.styling.window_theme import apply_stylesheet

    # init qt application
    if qt_app is None:
        from qtpy.QtWidgets import QApplication
        app = QApplication(sys.argv)
    else:
        app = qt_app

    # register fonts
    from qtpy.QtGui import QFontDatabase
    db = QFontDatabase()
    db.addApplicationFont(abs_path_from_package_dir('resources/fonts/poppins/Poppins-Medium.ttf'))
    db.addApplicationFont(abs_path_from_package_dir('resources/fonts/source_code_pro/SourceCodePro-Regular.ttf'))
    db.addApplicationFont(abs_path_from_package_dir('resources/fonts/asap/Asap-Regular.ttf'))

    # auto startup dialog
    t = NodesPackage('ProRF')
    editor_init_config = {'action': 'open project', 'required packages': [NodesPackage('ProRF')],
                          'content': {'general info': {'type': 'Ryven project file', 'ryven version': 'v3.1'},
                                      'required packages': [{'name': 'ProRF', 'dir': os.path.dirname(os.path.abspath(__file__)) + '\\src\\ProRF'}],
                                      'scripts': [{'title': 'ProRF GUI', 'variables': {}, 'flow': {}, 'GID': 1}]}}

    window_theme = apply_stylesheet('dark')

    # adjust flow theme if not set
    if flow_theme is None:
        flow_theme = 'pure dark' if window_theme.name == 'dark' else 'pure light'

    # init main console
    console_stdout_redirect, \
    console_errout_redirect = init_main_console(window_theme)

    # init main window
    editor = MainWindow(editor_init_config, window_title, window_theme, flow_theme, parent=gui_parent)
    editor.show()

    if qt_app is None:
        if redirect_console_output:  # redirect console output
            from contextlib import redirect_stdout, redirect_stderr

            with redirect_stdout(console_stdout_redirect), \
                    redirect_stderr(console_errout_redirect):

                # run
                editor.print_info()
                sys.exit(app.exec_())
        else:
            # run
            editor.print_info()
            sys.exit(app.exec_())
    else:
        return editor


if __name__ == '__main__':
    run()
