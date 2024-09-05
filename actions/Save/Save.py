from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class Save(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = -1
        
    def set_state( self, state ):
        self.current_state = state
        icon_name = "save.png"
        self.set_icon( icon_name, state )
        self.set_text( self.action_name )
            
    def do_action(self) -> None:
        try:
            self.plugin_base.backend.send_message("/save_state", 1 )         
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    def on_ready(self):
        ok = super().on_ready()
        self.set_state(1)
        return ok