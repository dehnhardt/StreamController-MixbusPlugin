from src.backend.PluginManager.ActionBase import ActionBase
from loguru import logger as log

import os

class MixbusActionBase( ActionBase ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init = False

    def set_icon( self, icon_name, active = True ):
        log.debug( "set_icon " + icon_name )
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if not active:
            log.debug("use disabled icon")
        if not os.path.exists( p ):
            log.error( "icon path does not exists" )
        try: 
            self.set_media(media_path=p)
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        log.debug( "set_icon " + icon_name + " - done" )
              
    def set_text( self, text ):
        self.set_top_label( text, font_size=16)

    def on_value_change(self, *args, **kwargs):
        if not self.init:
            self.init = True