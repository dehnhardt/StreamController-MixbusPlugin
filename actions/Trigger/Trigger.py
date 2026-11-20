from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from PIL import Image
from loguru import logger as log

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw

from plugins.org_dehnhardt_MixbusPlugin.backend.const import SETTING_TRIGGER_ROUTE as SETTING_ROUTE, SETTING_TRIGGER_ROW as SETTING_ROW

# Slot states as reported by Mixbus
STATE_EMPTY = -1
STATE_STOPPED = 0
STATE_PLAYING = 1


class Trigger(MixbusActionBase):
    """
    Starts the clip in one slot of the Mixbus/Ardour trigger grid.
    Route and row are shown as in Mixbus (counting from 1); Mixbus itself counts from 0.
    """

    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.route = 1
        self.row = 1
        # Offset of the Mixbus trigger bank (route, row); the grid is reported relative to it
        self.bank = (0, 0)
        self.current_state = None
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::TriggerGrid",
                                          callback=self.on_grid_change)
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::TriggerBank",
                                          callback=self.on_bank_change)

    def set_state( self, state ):
        if state == self.current_state:
            return
        self.current_state = state
        self.show_position()
        if state == STATE_EMPTY:
            # An empty slot shows nothing and ignores key presses
            self.enabled = False
            self.set_media(image=Image.new("RGBA", (256, 256), (0, 0, 0, 0)))
        else:
            self.set_icon( "play.png", 1 if state == STATE_PLAYING else 0 )

    def show_position(self) -> None:
        self.set_text( "{}:{}".format(self.route + self.bank[0], self.row + self.bank[1]) )

    def do_action(self) -> None:
        try:
            self.plugin_base.backend.send_message("/trigger_bang", [self.route - 1, self.row - 1] )
        except Exception as e:
            log.error(e)
            self.show_error()

    def on_key_up(self) -> None:
        # Slots that launch while held need to see the release
        if self.enabled:
            try:
                self.plugin_base.backend.send_message("/trigger_unbang", [self.route - 1, self.row - 1] )
            except Exception as e:
                log.error(e)

    async def on_grid_change(self, event_id, path, states) -> None:
        # path looks like /trigger_grid/<route>/state with route counting from 0
        try:
            if int(path.split("/")[2]) == self.route - 1 and self.row - 1 < len(states):
                self.set_state(states[self.row - 1])
        except Exception as e:
            log.debug("Could not show trigger state: {}", e)

    async def on_bank_change(self, event_id, path, bank) -> None:
        try:
            self.bank = (int(bank[0]), int(bank[1]))
            self.show_position()
        except Exception as e:
            log.debug("Could not show trigger bank: {}", e)

    def update_state(self) -> None:
        try:
            self.bank = tuple(self.plugin_base.backend.get_trigger_bank())
            self.set_state(self.plugin_base.backend.get_trigger_state(self.route - 1, self.row - 1))
        except Exception as e:
            log.debug("Trigger state not available yet: {}", e)

    def on_ready(self):
        ok = super().on_ready()
        settings = self.get_settings()
        self.route = max(1, int(settings.get(SETTING_ROUTE, 1)))
        self.row = max(1, int(settings.get(SETTING_ROW, 1)))
        self.current_state = None
        self.set_state(STATE_EMPTY)
        self.update_state()
        return ok

    def get_config_rows(self) -> list:
        settings = self.get_settings()
        self.route_entry = Adw.SpinRow.new_with_range(1, 8, 1)
        self.route_entry.set_title("Route")
        self.route_entry.set_value(max(1, int(settings.get(SETTING_ROUTE, 1))))
        self.row_entry = Adw.SpinRow.new_with_range(1, 8, 1)
        self.row_entry.set_title("Row")
        self.row_entry.set_value(max(1, int(settings.get(SETTING_ROW, 1))))
        self.route_entry.connect("notify::value", self.on_position_changed)
        self.row_entry.connect("notify::value", self.on_position_changed)
        return [self.route_entry, self.row_entry]

    def on_position_changed(self, *args):
        settings = self.get_settings()
        self.route = int(self.route_entry.get_value())
        self.row = int(self.row_entry.get_value())
        settings[SETTING_ROUTE] = self.route
        settings[SETTING_ROW] = self.row
        self.set_settings(settings)
        self.current_state = None
        self.update_state()
