from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class SelectedName(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = ""
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::SelectedName",
                                          callback=self.on_value_change)
        
    def set_state( self, state ):
        self.current_state = state
        self.set_center_label(state)
                
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on selected name change - status " + str( state ))
        self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state("")
        return ok