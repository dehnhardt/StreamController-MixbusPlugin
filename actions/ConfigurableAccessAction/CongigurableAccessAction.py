from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from loguru import logger as log

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw 


class ConfigurableAccessAction(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = -1
        self.name =""
        self.action = ""
            
    def on_key_down(self) -> None:
        log.debug( "ActionSuffix: " + self.action )
        try:
            self.plugin_base.backend.send_message("/access_action/" + self.action, None )
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        
    def on_ready(self):
        ok = super().on_ready()
        settings = self.get_settings()
        if settings:
            if settings['namebox'] is not None:
                self.name = settings['namebox']
            if settings['actionbox'] is not None:
                self.action = settings['actionbox']
        self.set_text( self.name )
        return ok
    
    def get_config_rows(self) -> list:
        self.actionbox = Adw.EntryRow( title = "Action")

        self.namebox = Adw.EntryRow( title = "Name")

        self.load_config_values()
        self.actionbox.connect("changed", self.on_actionbox_value_changed) 
        self.namebox.connect("changed", self.on_namebox_value_changed) 

        return [self.actionbox, self.namebox]
    
    def on_actionbox_value_changed(self, actionbox):
        settings = self.get_settings()
        t = actionbox.get_text()
        settings["actionbox"] = t
        self.action = t
        self.set_settings(settings)

    def on_namebox_value_changed(self, namebox):
        settings = self.get_settings()
        t = namebox.get_text()
        settings["namebox"] = t
        self.name = t
        self.set_label(t)
        self.set_settings(settings)
    
    def load_config_values(self):
        settings = self.get_settings()
        self.actionbox.set_text(settings.get("actionbox", ""))
        self.namebox.set_text(settings.get("namebox", ""))

