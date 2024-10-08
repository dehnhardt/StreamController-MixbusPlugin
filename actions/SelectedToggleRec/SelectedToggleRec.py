from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class SelectedToggleRec(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = 0
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::SelectedToggleRec",
                                          callback=self.on_value_change)
        
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::SelectEnableRec",
                                          callback=self.on_enble)

        
    def set_state( self, state ):
        self.current_state = state
        icon_name = "record_strip.png"
        if state == 1:
            self.set_text("On")
        else:
            self.set_text("Off")
        self.set_icon( icon_name, state )
            
    def do_action(self) -> None:
        try:
            val = abs(self.current_state - 1)
            log.debug("/select/rec " + str(val) )
            self.plugin_base.backend.send_message("/select/recenable", val ) 
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on selected rec change - status " + str( state ))
        self.set_state(state)

    async def on_enble(self, lala, enabled):
        if enabled:
            self.set_state(self.state)
            log.debug( "is enabled")
        else:
            self.set_state(-1)
            log.debug( "is disabled")

    def on_ready(self):
        ok = super().on_ready()
        self.set_state(0)
        return ok