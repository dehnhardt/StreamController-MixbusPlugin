from src.backend.PluginManager.ActionBase import ActionBase
from loguru import logger as log
from PIL import Image, ImageDraw
from abc import ABCMeta, abstractmethod

import os

class MixbusActionBase( ActionBase ):
    __metaclass__=ABCMeta
    @abstractmethod
    def do_action(self) -> None:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init = False
        self.current_state =""
        self.enabled = True

    def set_icon( self, icon_name, status = 1 ):
        log.debug( "set_icon " + icon_name + ", active: " + str(status))
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if not os.path.exists( p ):
            log.error( "icon path does not exists" )
        try: 
            image = Image.open(fp=p)
            if status == -1:
                self.enabled = False
                draw = ImageDraw.Draw(image)
                margin = 50
                draw.line((margin, margin, image.size[0]-margin, image.size[1]-margin), fill=(255, 255, 255, 150), width=20)
                draw.line((margin, image.size[1]-margin, image.size[0]-margin, margin), fill=(255, 255, 255, 150), width=20)
                background = Image.new(mode="RGBA", size=image.size, color=(220, 220, 220, 0))
                ni=Image.blend(background, image, 0.4)
            elif status == 0:
                self.enabled = True
                background = Image.new(mode="RGBA", size=image.size, color=(220, 220, 220, 0))
                log.debug("use disabled icon")
                ni=Image.blend(background, image, 0.4)
            else:
                self.enabled = True
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

    def on_key_down(self) ->None:
        if self.enabled:
            self.do_action()
