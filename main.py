from functools import partial
import os

from pyparsing import Any, List


from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.EventHolder import EventHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

from loguru import logger as log

# Import actions
from .actions.ToggleTransport.ToggleTransport import ToggleTransport

class MixbusPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        log.debug("MixbusPlugin started")
        self.launch_backend(os.path.join(self.PATH, "backend", "backend.py"), open_in_terminal=True, venv_path=os.path.join(self.PATH, ".venv"))
        
        # Register plugin
        self.register(
            plugin_name = "Harrison Mixbus",
            github_repo = "https://github.com/StreamController/PluginTemplate",
            plugin_version = "1.0.0",
            app_version = "1.0.0-alpha"
        )

        ## Register actions
        self.toggle_transport_action_holder = ActionHolder(
            plugin_base = self,
            action_base = ToggleTransport,
            action_id_suffix = "ToggleTransport",
            action_name = "ToggleTransport",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.toggle_transport_action_holder)

        self.toggle_transport_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::ToggleTransport",
            plugin_base = self
        )

        #self.toggle_transport_event_holder.add_listener(self.transport_callback)
        self.add_event_holder(self.toggle_transport_event_holder)

    def get_connected(self):
        try:
            return self.backend.get_connected()
        except Exception as e:
            log.error(e)
            return False
