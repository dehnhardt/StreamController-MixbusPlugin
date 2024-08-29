from src.backend.PluginManager.ActionBase import ActionBase
from loguru import logger as log
from PIL import Image


import os

class MixbusActionBase( ActionBase ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init = False
        self.current_state =""

    def set_icon( self, icon_name, active = True ):
        log.debug( "set_icon " + icon_name + ", active: " + str(active))
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if not os.path.exists( p ):
            log.error( "icon path does not exists" )
        try: 
            image = Image.open(fp=p)
            if not active:
                background = Image.new(mode="RGBA", size=image.size, color=(220, 220, 220, 0))
                log.debug("use disabled icon")
                ni=Image.blend(background, image, 0.4)
            else:
                ni = image
            self.set_media(image=ni)
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        log.debug( "set_icon " + icon_name + " - done" )
              
    def set_text( self, text ):
        self.set_bottom_label( text, font_size=16)

    def set_state(self, state ):
        if self.current_state == state:
            return
        self.current_state = state

    def on_value_change(self, *args, **kwargs):
        if not self.init:
            self.init = True
