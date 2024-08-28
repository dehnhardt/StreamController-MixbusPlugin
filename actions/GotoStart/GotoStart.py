from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class GotoStart(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = ""
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::GotoStart",
                                          callback=self.on_value_change)
        
    def set_state( self, state ):
        super().set_state( state )
        self.current_state = state
        icon_name = "previous.png"
        if state == "start":
            self.set_text("At Start")
        else:
            self.set_text("Goto Start")
        self.set_icon( icon_name, state != "start" )
            
    def on_key_down(self) -> None:
        try:
            self.plugin_base.backend.send_message("/goto_start", 1 )    
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on goto_start - status " + str( state ))
        self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("x")
        return ok