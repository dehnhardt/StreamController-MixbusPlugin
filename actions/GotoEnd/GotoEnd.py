from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class GotoEnd(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = ""
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::GotoEnd",
                                          callback=self.on_value_change)
        
    def set_state( self, state ):
        super().set_state( state )
        self.current_state = state
        if state == "end":
            icon_name = "FF.png"
            self.set_text("At End")
        else:
            icon_name = "FF.png"
            self.set_text("")
        self.set_icon( icon_name, state != "end" )
            
    def on_key_down(self) -> None:
        try:
            self.plugin_base.backend.send_message("/goto_end", 1 )    
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on goto_end - status " + str( state ))
        self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("x")
        return ok