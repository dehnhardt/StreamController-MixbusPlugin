# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from pyparsing import Any, List
from loguru import logger as log
from PIL import Image, ImageEnhance

import os

class ToggleTransport(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_state = -1
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::ToggleTransport",
                                          callback=self.on_transport_change)
        
    def set_icon( self, icon_name ):
        log.debug( "set_icon " + icon_name )
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if not os.path.exists( p ):
            log.error( "icon path does not exists" )
        try: 
            self.set_media(media_path=p)
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        
        log.debug( "set_icon " + icon_name + " - done" )
        
    def on_ready(self) -> None:
        super().on_ready()
        log.debug( "on_ready" )
        self.set_state( 0 )
      
    def set_state( self, state ):
        self.current_state = state
        if state == 0:
            icon_name = "play.png"
            self.set_bottom_label("Play", font_size=16)
        else:
            icon_name = "stop.png"
            self.set_bottom_label("Stop", font_size=16)
        self.set_icon( icon_name )

    def on_tick(self) -> None:
        self.set_state(self.current_state)
        
    def on_key_up(self) -> None:
        pass
    
    def on_key_down(self) -> None:
        try:
            self.plugin_base.backend.send_message("/toggle_roll", 1 )         
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_transport_change(self, *args, **kwargs):
        if len(args) < 3:
            return
        state = args[2]
        self.set_state(state)
