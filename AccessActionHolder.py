
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase

from gi.repository import Gtk


class AccessActionHolder(ActionHolder):
    def __init__(self,
        plugin_base: "PluginBase",
        action_base: ActionBase,
        action_name: str,
        access_action_path: str,
        icon_name: str,
        icon: Gtk.Widget = None,
        min_app_version: str = None,
        action_id: str = None,
        action_id_suffix: str = None,
        action_support = {
            Input.Key: ActionInputSupport.UNTESTED,
            Input.Dial: ActionInputSupport.UNTESTED,
            Input.Touchscreen: ActionInputSupport.UNTESTED
        },
        *args, **kwargs):
        super().__init__ ( plugin_base, action_base, action_name,
            icon,
            min_app_version,
            action_id,
            action_id_suffix,
            action_support,
            *args, **kwargs 
        )
        self.access_action_path = access_action_path
        self.icon_name = icon_name

