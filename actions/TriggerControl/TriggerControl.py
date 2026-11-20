from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from loguru import logger as log

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from plugins.org_dehnhardt_MixbusPlugin.backend.const import (
    SETTING_TRIGGER_COMMAND as SETTING_COMMAND, SETTING_TRIGGER_STEP as SETTING_STEP,
    TRIGGER_ROWS_UP as ROWS_UP, TRIGGER_ROWS_DOWN as ROWS_DOWN, TRIGGER_STOP_ALL as STOP_ALL )

# command -> (title in the config, label on the key, icon)
COMMANDS = {
    ROWS_UP: ("Rows up", "Up", "up.png"),
    ROWS_DOWN: ("Rows down", "Down", "down.png"),
    STOP_ALL: ("Stop all clips", "Stop All", "stop.png"),
}


class TriggerControl(MixbusActionBase):
    """
    Controls the trigger grid: scrolls the visible clip rows or stops all clips.
    """

    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.command = ROWS_DOWN
        self.step = 3

    def do_action(self) -> None:
        try:
            if self.command == ROWS_UP:
                self.plugin_base.backend.send_message("/tbank_step_row", -self.step )
            elif self.command == ROWS_DOWN:
                self.plugin_base.backend.send_message("/tbank_step_row", self.step )
            elif self.command == STOP_ALL:
                # 1 = stop immediately, 0 = at the end of the bar
                self.plugin_base.backend.send_message("/trigger_stop_all", 1 )
        except Exception as e:
            log.error(e)
            self.show_error()

    def load_settings(self) -> None:
        settings = self.get_settings()
        command = settings.get(SETTING_COMMAND, ROWS_DOWN)
        self.command = command if command in COMMANDS else ROWS_DOWN
        self.step = max(1, int(settings.get(SETTING_STEP, 3)))

    def show_command(self) -> None:
        _, label, icon = COMMANDS[self.command]
        self.set_icon( icon )
        self.set_text( label )

    def on_ready(self):
        ok = super().on_ready()
        self.load_settings()
        self.show_command()
        return ok

    def get_config_rows(self) -> list:
        self.load_settings()
        self.command_entry = Adw.ComboRow(title="Command")
        self.command_entry.set_model(Gtk.StringList.new([title for title, _, _ in COMMANDS.values()]))
        self.command_entry.set_selected(list(COMMANDS).index(self.command))
        self.step_entry = Adw.SpinRow.new_with_range(1, 8, 1)
        self.step_entry.set_title("Rows per step")
        self.step_entry.set_value(self.step)
        self.command_entry.connect("notify::selected", self.on_config_changed)
        self.step_entry.connect("notify::value", self.on_config_changed)
        return [self.command_entry, self.step_entry]

    def on_config_changed(self, *args):
        settings = self.get_settings()
        self.command = list(COMMANDS)[self.command_entry.get_selected()]
        self.step = int(self.step_entry.get_value())
        settings[SETTING_COMMAND] = self.command
        settings[SETTING_STEP] = self.step
        self.set_settings(settings)
        self.show_command()
