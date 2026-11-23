from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from loguru import logger as log

from src.backend.DeckManagement.InputIdentifier import Input

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw 

# Background of the key whose scene was recalled last
ACTIVE_SCENE_COLOR = [20, 90, 160, 255]
NO_COLOR = [0, 0, 0, 0]


class MixerScene(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        # As shown in the Mixbus scene list (1-based); Mixbus itself counts from 0
        self.scene_number = -1
        self.current_state = ""
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::MixerSceneName",
                                          callback=self.on_scene_name_change)
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::MixerSceneActive",
                                          callback=self.on_active_scene_change)
        
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
        # A short press recalls the scene
        try:
            if self.scene_number >= 1:
                self.plugin_base.backend.send_message("/recall_mixer_scene", self.scene_number - 1 )
                self.plugin_base.set_active_mixer_scene(self.scene_number)
        except Exception as e:
            log.error(e)
            self.show_error()
            return

    def store_scene(self) -> None:
        # A long press stores the current mixer state in this scene; Mixbus names a new scene with a timestamp
        try:
            if self.scene_number >= 1:
                self.plugin_base.backend.send_message("/store_mixer_scene", self.scene_number - 1 )
                self.plugin_base.set_active_mixer_scene(self.scene_number)
        except Exception as e:
            log.error(e)
            self.show_error()

    def on_key_down(self) -> None:
        # Recall on release, so a long press does not recall first
        pass

    def event_callback(self, event, data = None):
        if event == Input.Key.Events.SHORT_UP:
            if self.enabled:
                self.do_action()
        elif event == Input.Key.Events.HOLD_START:
            self.store_scene()
        else:
            super().event_callback(event, data)
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        #if len(args) < 3:
        #    return
        #state = args[2]
        log.debug( "on mixer_scene" + str( args ))
        log.debug( "on mixer_scene" + str( kwargs ))
        #self.set_state(state)

    def show_scene_name(self, name: str) -> None:
        self.set_center_label(name or "(empty)", font_size=14)

    def update_scene_name(self) -> None:
        if self.scene_number < 1:
            return
        try:
            self.show_scene_name(self.plugin_base.backend.get_mixer_scene_name(self.scene_number - 1))
        except Exception as e:
            log.debug("Mixer scene name not available yet: {}", e)

    async def on_scene_name_change(self, event_id, path, name = "") -> None:
        # path looks like /mixer_scene/<n>/name with n counting from 0
        try:
            if int(path.split("/")[2]) == self.scene_number - 1:
                self.show_scene_name(name)
        except Exception as e:
            log.debug("Could not show mixer scene name: {}", e)

    def update_highlight(self) -> None:
        active = self.scene_number >= 1 and self.plugin_base.active_mixer_scene == self.scene_number
        self.set_background_color(ACTIVE_SCENE_COLOR if active else NO_COLOR)

    async def on_active_scene_change(self, event_id, scene) -> None:
        try:
            self.update_highlight()
        except Exception as e:
            log.debug("Could not highlight mixer scene: {}", e)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("x")
        self.set_background_icon("mixer-page.png")
        settings = self.get_settings()
        if settings.get("scenenumber") is not None:
            self.scene_number = max(1, int(settings.get("scenenumber")))
            self.set_text("Scene " + str(self.scene_number) )
            self.update_scene_name()
            self.update_highlight()
        return ok
    
    def get_config_rows(self) -> list:
        self.mixer_scene_entry = Adw.SpinRow.new_with_range(1, 8, 1)
        self.mixer_scene_entry.set_title("Mixer Scene")
        self.load_config_values()
        self.mixer_scene_entry.connect("notify::value", self.on_mixer_scene_number_changed)
        return [self.mixer_scene_entry]

    def on_mixer_scene_number_changed(self, *args):
        settings = self.get_settings()
        self.scene_number = int( self.mixer_scene_entry.get_value())
        settings['scenenumber'] = self.scene_number
        self.set_settings(settings)
        self.set_text("Scene " + str(self.scene_number) )
        self.update_scene_name()
        self.update_highlight()

    def load_config_values(self):
        settings = self.get_settings()
        self.mixer_scene_entry.set_value(max(1, int(settings.get("scenenumber", 1))))