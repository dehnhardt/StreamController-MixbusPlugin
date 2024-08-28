from src.backend.PluginManager.ActionBase import ActionBase
from loguru import logger as log

import os

class MixbusActionBase( ActionBase ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_icon( self, icon_name ):
        log.debug( "set_icon " + icon_name )
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if not os.path.exists( p ):
            log.error( "icon path does not exists" )
        try: 
            self.set_media(media_path=p)
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        log.debug( "set_icon " + icon_name + " - done" )
              
