from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class SelectedToggleMute(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = 0
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::SelectedToggleMute",
                                          callback=self.on_value_change)
        
    def set_state( self, state ):
        self.current_state = state
        icon_name = "mute.png"
        if state == 0:
            self.set_text("Off")
        else:
            self.set_text("On")
        self.set_icon( icon_name, state )
            
    def do_action(self) -> None:
        try:
            val = abs(self.current_state - 1)
            log.debug("/select/mute " + str(val) )
            self.plugin_base.backend.send_message("/select/mute", val ) 
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on selected mute change - status " + str( state ))
        self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state(0)
        return ok