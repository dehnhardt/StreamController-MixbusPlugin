#from src.backend.PluginManager.ActionBase import ActionBase
from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class ToggleTransport(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = -1
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::ToggleTransport",
                                          callback=self.on_transport_change)
        
    def set_state( self, state ):
        self.current_state = state
        if state == 0:
            icon_name = "play.png"
            self.set_bottom_label("Play", font_size=16)
        else:
            icon_name = "stop.png"
            self.set_bottom_label("Stop", font_size=16)
        self.set_icon( icon_name )
            
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
        log.debug( "on transport change - status" + str( state ))
        self.set_state(state)
