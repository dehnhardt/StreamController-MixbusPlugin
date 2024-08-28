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
from .actions.ToggleRecord.ToggleRecord import ToggleRecord
from .actions.ToggleLoop.ToggleLoop import ToggleLoop
from .actions.GotoStart.GotoStart import GotoStart
from .actions.GotoEnd.GotoEnd import GotoEnd
from .actions.GotoNextMarker.GotoNextMarker import GoToNextMarker
from .actions.GotoPrevMarker.GotoPrevMarker import GoToPrevMarker

class MixbusPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        log.debug("MixbusPlugin started")
        self.launch_backend(os.path.join(self.PATH, "backend", "backend.py"), open_in_terminal=True, venv_path=os.path.join(self.PATH, "backend", ".venv"))
        self.wait_for_backend(10)
        
        # Register plugin
        self.register(
            plugin_name = "Harrison Mixbus",
            github_repo = "https://github.com/StreamController/PluginTemplate",
            plugin_version = "1.0.0",
            app_version = "1.0.0-alpha"
        )

        ## Register actions

        # ToggleTransport
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

        self.add_event_holder(self.toggle_transport_event_holder)

        # ToggleRecord
        self.toggle_record_action_holder = ActionHolder(
            plugin_base = self,
            action_base = ToggleRecord,
            action_id_suffix = "ToggleRecord",
            action_name = "Toggle Record",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.toggle_record_action_holder)

        self.toggle_record_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::ToggleRecord",
            plugin_base = self
        )

        self.add_event_holder(self.toggle_record_event_holder)

        # ToggleLoop
        self.toggle_loop_action_holder = ActionHolder(
            plugin_base = self,
            action_base = ToggleLoop,
            action_id_suffix = "ToggleLoop",
            action_name = "Toggle Loop",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.toggle_loop_action_holder)

        self.toggle_loop_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::ToggleLoop",
            plugin_base = self
        )

        self.add_event_holder(self.toggle_loop_event_holder)

        # Goto start
        self.goto_start_action_holder = ActionHolder(
            plugin_base = self,
            action_base = GotoStart,
            action_id_suffix = "GotoStart",
            action_name = "Go to Start",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.goto_start_action_holder)

        self.goto_start_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::GotoStart",
            plugin_base = self
        )

        self.add_event_holder(self.goto_start_event_holder)

        # Goto end
        self.goto_end_action_holder = ActionHolder(
            plugin_base = self,
            action_base = GotoEnd,
            action_id_suffix = "GotoEnd",
            action_name = "Go to End",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.goto_end_action_holder)

        self.goto_end_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::GotoEnd",
            plugin_base = self
        )

        self.add_event_holder(self.goto_end_event_holder)

        # Goto prev marker
        self.goto_prev_marker_action_holder = ActionHolder(
            plugin_base = self,
            action_base = GoToPrevMarker,
            action_id_suffix = "GotoPrevMarker",
            action_name = "Go to Prev Marker",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.goto_prev_marker_action_holder)

        self.goto_prev_marker_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::GotoPrevMarker",
            plugin_base = self
        )

        self.add_event_holder(self.goto_prev_marker_event_holder)

        # Goto next marker
        self.goto_next_marker_action_holder = ActionHolder(
            plugin_base = self,
            action_base = GoToNextMarker,
            action_id_suffix = "GotoNextMarker",
            action_name = "Go to Next Marker",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.goto_next_marker_action_holder)

        self.goto_next_marker_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::GotoNextMarker",
            plugin_base = self
        )

        self.add_event_holder(self.goto_next_marker_event_holder)

    def get_connected(self):
        try:
            return self.backend.get_connected()
        except Exception as e:
            log.error(e)
            return False
