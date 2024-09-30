from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from loguru import logger as log

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw 


class MixerScene(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.scene_number = -1
        self.current_state = ""
        #self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::MixerScene",
        #                                  callback=self.on_value_change)
        
    #def set_state( self, state ):
    #    super().set_state( state )
    #    self.current_state = state
    #    icon_name = "next.png"
    #    if state == "end":
    #        self.set_text("At End")
    #    else:
    #        self.set_text("Goto End")
    #    self.set_icon( icon_name, state != "end" )
            
    def do_action(self) -> None:
        try:
            if self.scene_number > -1:
                self.plugin_base.backend.send_message("/recall_mixer_scene", self.scene_number )    
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        #if len(args) < 3:
        #    return
        #state = args[2]
        log.debug( "on mixer_scene" + str( args ))
        log.debug( "on mixer_scene" + str( kwargs ))
        #self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("x")
        settings = self.get_settings()
        if settings.get("scenenumber") is not None:
            self.scene_number = int(settings.get("scenenumber"))
            self.set_bottom_label("Mixer Scene " + str(self.scene_number) )
        return ok
    
    def get_config_rows(self) -> list:
        self.mixer_scene_entry = Adw.SpinRow.new_with_range(0, 7, 1)
        self.mixer_scene_entry.set_title("Increment by")
        self.mixer_scene_entry.connect("changed", self.on_mixer_scene_number_changed) 
        self.load_config_values()
        return [self.mixer_scene_entry]

    def on_mixer_scene_number_changed(self, namebox):
        settings = self.get_settings()
        self.scene_number = int( self.mixer_scene_entry.get_value())
        settings["scenenumber"] = self.scene_number
        self.set_settings(settings)
        self.set_bottom_label("Scene " + str(self.scene_number) )

    def load_config_values(self):
        settings = self.get_settings()
        self.mixer_scene_entry.set_value(int(settings.get("scenenumber")))
        self.set_bottom_label("Scene " + str(self.scene_number) )