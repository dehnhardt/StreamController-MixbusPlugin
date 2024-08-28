from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class GoToNextMarker(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = False
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::GotoNextMarker",
                                          callback=self.on_value_change)
        
    def set_state( self, state ):
        super().set_state( state )
        self.current_state = False
        icon_name = "right.png"
        self.set_icon( icon_name, state != "end" )
        self.set_text( state )
            
    def on_key_down(self) -> None:
        try:
            self.plugin_base.backend.send_message("/next_marker", 1 )
            self.current_state = True
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        #if not self.current_state:
        #    return
        #super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on goto_next_marker - status " + str( state ))
        self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("")
        return ok