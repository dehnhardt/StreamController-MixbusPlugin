import globals as gl
from src.Signals import Signals

from loguru import logger as log

from ..backend.const import (
    SETTING_TRIGGER_ROUTE as SETTING_ROUTE, SETTING_TRIGGER_ROW as SETTING_ROW,
    SETTING_TRIGGER_COMMAND as SETTING_COMMAND, SETTING_TRIGGER_STEP as SETTING_STEP,
    TRIGGER_ROWS_UP as ROWS_UP, TRIGGER_ROWS_DOWN as ROWS_DOWN, TRIGGER_STOP_ALL as STOP_ALL )

PAGE_NAME = "Mixbus Triggers"
PLUGIN_ID = "org_dehnhardt_MixbusPlugin"
# Mixbus reports 8 routes (columns) in its trigger grid
MAX_ROUTES = 8


def _key(action: str, settings: dict) -> dict:
    return {"states": {"0": {
        "actions": [{"id": "{}::{}".format(PLUGIN_ID, action), "settings": settings}],
        "image-control-action": 0,
        "label-control-actions": [0, 0, 0],
        "background-control-action": 0,
    }}}


def build_trigger_page(rows: int, cols: int) -> dict:
    """
    Clip slots fill the deck except for the last column, which holds the controls:
    rows up, rows down and stop all. Keys are named "<column>x<row>".
    """
    clip_cols = min(cols - 1, MAX_ROUTES) if cols > 1 else min(cols, MAX_ROUTES)
    keys = {}
    for col in range(clip_cols):
        for row in range(rows):
            keys["{}x{}".format(col, row)] = _key("Trigger", {SETTING_ROUTE: col + 1, SETTING_ROW: row + 1})

    if cols > 1:
        controls = [(ROWS_UP, rows), (ROWS_DOWN, rows), (STOP_ALL, 1)]
        for row, (command, step) in enumerate(controls[:rows]):
            keys["{}x{}".format(cols - 1, row)] = _key("TriggerControl", {SETTING_COMMAND: command, SETTING_STEP: step})
    return {"keys": keys}


def create_trigger_page() -> str:
    """Creates the trigger page for the first connected deck and returns a message for the user."""
    controllers = gl.deck_manager.deck_controller if gl.deck_manager is not None else []
    if not controllers:
        return "Connect a deck first"
    rows, cols = controllers[0].deck.key_layout()
    try:
        path = gl.page_manager.add_page(PAGE_NAME, build_trigger_page(rows, cols))
    except FileExistsError:
        return "A page named '{}' already exists".format(PAGE_NAME)
    except Exception as e:
        log.error(e)
        return "Could not create the page: {}".format(e)
    gl.page_manager.update_dict_of_pages_with_path(path)
    gl.page_manager.reload_pages_with_path(path)
    gl.signal_manager.trigger_signal(Signals.PageAdd, path)
    return "Created page '{}' for a {}x{} deck".format(PAGE_NAME, cols, rows)
