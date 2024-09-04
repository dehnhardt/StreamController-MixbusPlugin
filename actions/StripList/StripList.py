import time

from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class StripList(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = -1
        #We have no feedback here..
        # self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::Save",
        #                                   callback=self.on_value_change)
        
    def set_state( self, state ):
        self.current_state = state
        icon_name = "Duplicate.png"
        self.set_icon( icon_name, state )
        self.set_text( self.action_name )
            
    def on_key_down(self) -> None:
        try:
            #self.plugin_base.backend.send_message_and_handle_reply("/strip/list" )
            self.plugin_base.backend.send_message("/strip/list" )
            time.sleep(2)

        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    # async def on_value_change(self, *args, **kwargs):
    #     super().on_value_change(*args, **kwargs)
    #     if len(args) < 3:
    #         return
    #     state = args[2]
    #     log.debug( "on save - status " + str( state ))
    #     self.set_state(state)

    def on_ready(self):
        ok = super().on_ready()
        self.set_state(1)
        return ok