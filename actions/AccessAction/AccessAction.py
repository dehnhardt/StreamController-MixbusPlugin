from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase

from loguru import logger as log


class AccessAction(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.current_state = -1
            
    def do_action(self) -> None:
        action = self.plugin_base.action_holders[self.action_id].access_action_path
        log.debug( "ActionSuffix: " + action )
        try:
            self.plugin_base.backend.send_message("/access_action/" + action, None )
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        
    def on_ready(self):
        ok = super().on_ready()
        self.set_icon( self.plugin_base.action_holders[self.action_id].icon_name )
        self.set_text( self.action_name )
        return ok