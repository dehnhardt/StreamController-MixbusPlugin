from plugins.org_dehnhardt_MixbusPlugin.MixbusActionBase import MixbusActionBase
from loguru import logger as log


class ToggleClick(MixbusActionBase):
    def __init__(self, *args, **kwargs):
        log.debug( "__init__")
        super().__init__(*args, **kwargs)
        self.click = False
        self.current_state = -1
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::ToggleClick",
                                          callback=self.on_value_change)
        self.plugin_base.connect_to_event(event_id="org_dehnhardt_MixbusPlugin::OnClick",
                                          callback=self.on_click)
        
    def set_state( self, state ):
        super().set_state( state )
        icon_name = "metronome.png"
        if state == 0:
            self.set_text("Off")
        else:
            self.set_text("On")
        self.set_icon( icon_name, state )
            
    def on_key_down(self) -> None:
        try:
            self.plugin_base.backend.send_message("/toggle_click", 1 )         
        except Exception as e:
            log.error(e)
            self.show_error()
            return
    
    async def on_value_change(self, *args, **kwargs):
        super().on_value_change(*args, **kwargs)
        if len(args) < 3:
            return
        state = args[2]
        log.debug( "on click change - status " + str( state ))
        self.set_state(state)

    async def on_click(self, *args, **kwargs):
        if len(args) < 3:
            return
        if self.click:
            self.set_top_label(text="O", color=(220, 20, 20, 0))
        else:
            self.set_top_label(text="")
        self.click = not self.click

    def on_ready(self):
        ok = super().on_ready()
        self.set_state(0)
        return ok