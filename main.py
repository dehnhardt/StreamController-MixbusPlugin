import os
import time

from PIL import Image

from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.EventHolder import EventHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

from loguru import logger as log

# Import actions
from .actions.GotoEnd.GotoEnd import GotoEnd
from .actions.GotoNextMarker.GotoNextMarker import GoToNextMarker
from .actions.GotoPrevMarker.GotoPrevMarker import GoToPrevMarker
from .actions.GotoStart.GotoStart import GotoStart
from .actions.ToggleClick.ToggleClick import ToggleClick
from .actions.ToggleLoop.ToggleLoop import ToggleLoop
from .actions.ToggleRecord.ToggleRecord import ToggleRecord
from .actions.ToggleTransport.ToggleTransport import ToggleTransport
from .actions.Save.Save import Save
from .actions.Undo.Undo import Undo
from .actions.Redo.Redo import Redo
from .actions.StripList.StripList import StripList

from .actions.MixerScene.MixerScene import MixerScene

from .actions.SelectedToggleSolo.SelectedToggleSolo import SelectedToggleSolo
from .actions.SelectedToggleMute.SelectedToggleMute import SelectedToggleMute
from .actions.SelectedToggleRec.SelectedToggleRec import SelectedToggleRec
from .actions.SelectedTogglePolarity.SelectedTogglePolarity import SelectedTogglePolarity
from .actions.SelectedName.SelectedName import SelectedName
from .actions.SelectedSpill.SelectedSpill import SelectedSpill

from .actions.AccessAction.AccessAction import AccessAction
from .actions.ConfigurableAccessAction.CongigurableAccessAction import ConfigurableAccessAction

from plugins.org_dehnhardt_MixbusPlugin.AccessActionHolder import AccessActionHolder
from plugins.org_dehnhardt_MixbusPlugin.backend.const import (
    FEEDBACK_VALUE_STRIP_BUTTONS,
    FEEDBACK_VALUE_STRIP_CONTROLS,
    FEEDBACK_VALUE_MASTER_SECTION,
    FEEDBACK_VALUE_SELECT_ONLY_FEEDBACK,
    FEEDBACK_VALUE_USE_SLASH_REPLY,
    FEEDBACK_VALUE_REPORT_TRIGGER_STATUS,
    FEEDBACK_VALUE_REPORT_MIXER_SCENE,
    SETTING_ENABLE_TRIGGERS, 
    SETTING_ENABLE_MIXER_SCENES )
from typing import Dict, Any

class MixbusPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        log.debug("MixbusPlugin started")
        self.launch_backend(os.path.join(self.PATH, "backend", "backend.py"), open_in_terminal=True, venv_path=os.path.join(self.PATH, "backend", ".venv"))
        self.wait_for_backend(5)

        # Register plugin
        self.register(
            plugin_name = "Harrison Mixbus",
            github_repo = "https://github.com/dehnhardt/StreamController-MixbusPlugin",
            plugin_version = "1.0.0",
            app_version = "1.0.0-alpha"
        )

        self.register_actions()
        self.init_daw()

    def init_daw( self ):

        settings = self.get_settings()
        feedback = FEEDBACK_VALUE_STRIP_BUTTONS + FEEDBACK_VALUE_STRIP_CONTROLS + FEEDBACK_VALUE_MASTER_SECTION + FEEDBACK_VALUE_SELECT_ONLY_FEEDBACK + FEEDBACK_VALUE_USE_SLASH_REPLY
        self.enable_triggers = settings.get(SETTING_ENABLE_MIXER_SCENES)
        self.enable_mixer_scenes = settings.get(SETTING_ENABLE_MIXER_SCENES)

        if settings.get(SETTING_ENABLE_TRIGGERS):
            feedback = feedback + FEEDBACK_VALUE_REPORT_TRIGGER_STATUS

        if settings.get(SETTING_ENABLE_MIXER_SCENES):
            feedback = feedback + FEEDBACK_VALUE_REPORT_MIXER_SCENE


        log.debug("************* MixbusPlugin /strip/list")
        self.backend.send_message("/strip/list")
        time.sleep(2)

        log.debug("************* MixbusPlugin /set_surface: feedback: " + str(feedback))
        #self.backend.send_message("/set_surface", [0, 127, 63] )
        #self.backend.send_message("/set_surface", [0, 127, 24595] )
        #self.backend.send_message("/set_surface", [0, 127, 57363] )
        #self.backend.send_message("/set_surface", [0, 127, 90131] )
        self.backend.send_message("/set_surface", [0, 127, feedback] )

    def register_actions(self):
        log.debug( "start register actions")

        # ToggleClick
        self.toggle_click_action_holder = ActionHolder(
            plugin_base = self,
            action_base = ToggleClick,
            action_id_suffix = "ToggleClick",
            action_name = "ToggleClick",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.toggle_click_action_holder)

        self.toggle_click_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::ToggleClick",
            plugin_base = self
        )

        self.add_event_holder(self.toggle_click_event_holder)

        self.on_click_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::OnClick",
            plugin_base = self
        )
        self.add_event_holder(self.on_click_event_holder)

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

        # Save
        self.save_action_holder = ActionHolder(
            plugin_base = self,
            action_base = Save,
            action_id_suffix = "Save",
            action_name = "Save",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )

        self.add_action_holder(self.save_action_holder)
        # we have no feedback here...

        # Undo
        self.undo_action_holder = ActionHolder(
            plugin_base = self,
            action_base = Undo,
            action_id_suffix = "Undo",
            action_name = "Undo",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )

        self.add_action_holder(self.undo_action_holder)
        # we have no feedback here...

        # Redo
        self.redo_action_holder = ActionHolder(
            plugin_base = self,
            action_base = Redo,
            action_id_suffix = "Redo",
            action_name = "Redo",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )

        self.add_action_holder(self.redo_action_holder)
        # we have no feedback here...

        # StripList
        self.strip_list_action_holder = ActionHolder(
            plugin_base = self,
            action_base = StripList,
            action_id_suffix = "StripList",
            action_name = "Strip List",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )

        self.add_action_holder(self.strip_list_action_holder)
        # we have no feedback here...

        ## Selected Strip Actions

        # SelectedToggleSolo
        self.selected_toggle_solo_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedToggleSolo,
            action_id_suffix = "SelectedToggleSolo",
            action_name = "Toggle Solo",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.selected_toggle_solo_action_holder)

        self.selected_toggle_solo_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedToggleSolo",
            plugin_base = self
        )

        self.add_event_holder(self.selected_toggle_solo_event_holder)

        # SelectedToggleMute
        self.selected_toggle_mute_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedToggleMute,
            action_id_suffix = "SelectedToggleMute",
            action_name = "Toggle Mute",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.selected_toggle_mute_action_holder)

        self.selected_toggle_mute_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedToggleMute",
            plugin_base = self
        )

        self.add_event_holder(self.selected_toggle_mute_event_holder)

        # SelectedToggleRec
        self.selected_toggle_rec_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedToggleRec,
            action_id_suffix = "SelectedToggleRec",
            action_name = "Toggle Rec",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.selected_toggle_rec_action_holder)

        self.selected_toggle_rec_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedToggleRec",
            plugin_base = self
        )
        self.add_event_holder(self.selected_toggle_rec_event_holder)

        self.selected_enable_rec_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectEnableRec",
            plugin_base = self
        )
        self.add_event_holder(self.selected_enable_rec_event_holder)

        # SelectedTogglePolarity
        self.selected_toggle_polarity_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedTogglePolarity,
            action_id_suffix = "SelectedTogglePolarity",
            action_name = "Toggle Polarity",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.selected_toggle_polarity_action_holder)

        self.selected_toggle_polarity_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedTogglePolarity",
            plugin_base = self
        )

        self.add_event_holder(self.selected_toggle_polarity_event_holder)

        # SelectedName
        self.selected_name_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedName,
            action_id_suffix = "SelectedName",
            action_name = "Strip Name",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.selected_name_action_holder)

        self.selected_name_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedName",
            plugin_base = self
        )

        self.add_event_holder(self.selected_name_event_holder)

        # SelectedName
        self.selected_spill_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SelectedSpill,
            action_id_suffix = "SelectedSpill",
            action_name = "Spill",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        
        self.add_action_holder(self.selected_spill_action_holder)

        self.selected_spill_event_holder = EventHolder(
            event_id = "org_dehnhardt_MixbusPlugin::SelectedSpill",
            plugin_base = self
        )

        self.add_event_holder(self.selected_spill_event_holder)

        ## Mixbus / Ardour Mixer Scenes
        self.mixer_scene_action_holder = ActionHolder(
            plugin_base = self,
            action_base = MixerScene,
            action_id_suffix = "MixerScene_x",
            action_name = "Mixer Scene",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.mixer_scene_action_holder)

        #self.mixer_scene_name_event_holder = EventHolder(
        #    event_id = "org_dehnhardt_MixbusPlugin::MixerSceneName",
        #    plugin_base = self
        #)

        #self.add_event_holder(self.mixer_scene_name_event_holder)


        ## Mixbus / Ardour AccessActions

        # Add Strip
        self.add_strip_action_holder = AccessActionHolder(
            plugin_base = self,
            action_base = AccessAction,
            action_id_suffix = "AddTrackBus",
            action_name = "Ad Strip",
            icon_name = "add_strip.png",
            access_action_path="Main/AddTrackBus",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.add_strip_action_holder)

        # Quick Export
        self.quick_export_action_holder = AccessActionHolder(
            plugin_base = self,
            action_base = AccessAction,
            action_id_suffix = "QuickExport",
            action_name = "Quick Exp.",
            icon_name = "export.png",
            access_action_path="Main/QuickExport",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.quick_export_action_holder)

        # LUA Action
        self.lua1_action_holder = AccessActionHolder(
            plugin_base = self,
            action_base = AccessAction,
            action_id_suffix = "LuaAction3",
            action_name = "Mixer Strip Configuration",
            icon_name = "export.png",
            access_action_path="LuaAction/script-3",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.lua1_action_holder)

        # Configurable Ardour/Mixbus actions
        self.configurable_action_holder = ActionHolder(
            plugin_base = self,
            action_base = ConfigurableAccessAction,
            action_id_suffix = "LuaAction_x",
            action_name = "Configurable Action",
            action_support={Input.Key: ActionInputSupport.SUPPORTED}
        )
        self.add_action_holder(self.configurable_action_holder)


        log.debug("************* Actions registered")


    def get_connected(self):
        try:
            return self.backend.get_connected()
        except Exception as e:
            log.error(e)
            return False
