import importlib
import os

aliases = {
    'qt4': 'qt',
    'gtk2': 'gtk',
}

backends = [
    "qt",
    "qt5",
    "qt6",
    "gtk",
    "gtk2",
    "gtk3",
    "gtk4",
    "tk",
    "wx",
    "pyglet",
    "glut",
    "osx",
    "asyncio",
]

registered = {}

def register(name, inputhook):
    """Register the function *inputhook* as an event loop integration."""
    registered[name] = inputhook


class UnknownBackend(KeyError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return ("No event loop integration for {!r}. "
                "Supported event loops are: {}").format(self.name,
                                    ', '.join(backends + sorted(registered)))


def set_qt_api(gui):
    """Sets the `QT_API` environment variable if it isn't already set."""

    qt_api = os.environ.get("QT_API", None)

    from IPython.external.qt_loaders import (
        QT_API_PYQT,
        QT_API_PYQT5,
        QT_API_PYQT6,
        QT_API_PYSIDE,
        QT_API_PYSIDE2,
        QT_API_PYSIDE6,
        QT_API_PYQTv1,
        loaded_api,
    )

    loaded = loaded_api()

    qt_env2gui = {
        QT_API_PYSIDE: "qt4",
        QT_API_PYQTv1: "qt4",
        QT_API_PYQT: "qt4",
        QT_API_PYSIDE2: "qt5",
        QT_API_PYQT5: "qt5",
        QT_API_PYSIDE6: "qt6",
        QT_API_PYQT6: "qt6",
    }
    if loaded is not None and gui != "qt":
        if qt_env2gui[loaded] != gui:
            print(
                f"Cannot switch Qt versions for this session; will use {qt_env2gui[loaded]}."
            )
            return

    if qt_api is not None and gui != "qt":
        if qt_env2gui[qt_api] != gui:
            print(
                f'Request for "{gui}" will be ignored because `QT_API` '
                f'environment variable is set to "{qt_api}"'
            )
    else:
        if gui == "qt5":
            try:
                import PyQt5  # noqa

                os.environ["QT_API"] = "pyqt5"
            except ImportError:
                try:
                    import PySide2  # noqa

                    os.environ["QT_API"] = "pyside2"
                except ImportError:
                    os.environ["QT_API"] = "pyqt5"
        elif gui == "qt6":
            try:
                import PyQt6  # noqa

                os.environ["QT_API"] = "pyqt6"
            except ImportError:
                try:
                    import PySide6  # noqa

                    os.environ["QT_API"] = "pyside6"
                except ImportError:
                    os.environ["QT_API"] = "pyqt6"
        elif gui == "qt":
            # Don't set QT_API; let IPython logic choose the version.
            if "QT_API" in os.environ.keys():
                del os.environ["QT_API"]
        else:
            print(f'Unrecognized Qt version: {gui}. Should be "qt5", "qt6", or "qt".')
            return


def get_inputhook_name_and_func(gui):
    if gui in registered:
        return gui, registered[gui]

    if gui not in backends:
        raise UnknownBackend(gui)

    if gui in aliases:
        return get_inputhook_name_and_func(aliases[gui])

    gui_mod = gui
    if gui.startswith("qt"):
        set_qt_api(gui)
        gui_mod = "qt"

    mod = importlib.import_module("IPython.terminal.pt_inputhooks." + gui_mod)
    return gui, mod.inputhook
