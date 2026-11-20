from src.backend.PluginManager.ActionBase import ActionBase
from loguru import logger as log
from PIL import Image, ImageDraw
from abc import ABCMeta, abstractmethod

import os

# Opacity of the icons of inactive (status 0) actions. The icon is blended with a transparent
# background, so on the (black) key background this directly is the brightness of the icon.
DISABLED_ICON_OPACITY = 0.7

ICON_NORMAL = "normal"
ICON_INACTIVE = "inactive"
ICON_UNAVAILABLE = "unavailable"
ICON_FADED = "faded"

# Small, translucent icon shown behind the labels of a key
FADED_ICON_OPACITY = 0.65
FADED_ICON_SCALE = 0.75

# Rendered icons by (path, modification time, variant). The modification time makes edited icons show up without a restart.
_icon_cache: dict = {}

def _render_icon(path: str, variant: str) -> Image.Image:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    if variant == ICON_NORMAL:
        return image
    if variant == ICON_FADED:
        small = image.resize((int(image.width * FADED_ICON_SCALE), int(image.height * FADED_ICON_SCALE)), Image.Resampling.LANCZOS)
        small.putalpha(small.getchannel("A").point(lambda a: int(a * FADED_ICON_OPACITY)))
        faded = Image.new(mode="RGBA", size=image.size, color=(0, 0, 0, 0))
        faded.paste(small, ((image.width - small.width) // 2, (image.height - small.height) // 2))
        return faded
    background = Image.new(mode="RGBA", size=image.size, color=(220, 220, 220, 0))
    if variant == ICON_UNAVAILABLE:
        draw = ImageDraw.Draw(image)
        margin = 50
        draw.line((margin, margin, image.size[0]-margin, image.size[1]-margin), fill=(255, 255, 255, 150), width=20)
        draw.line((margin, image.size[1]-margin, image.size[0]-margin, margin), fill=(255, 255, 255, 150), width=20)
        return Image.blend(background, image, 0.4)
    return Image.blend(background, image, DISABLED_ICON_OPACITY)

def get_icon_image(path: str, variant: str) -> Image.Image:
    key = (path, os.path.getmtime(path), variant)
    image = _icon_cache.get(key)
    if image is None:
        image = _render_icon(path, variant)
        _icon_cache[key] = image
    return image

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
            if status == -1:
                variant = ICON_UNAVAILABLE
            elif status == 0:
                variant = ICON_INACTIVE
            else:
                variant = ICON_NORMAL
            self.enabled = variant != ICON_UNAVAILABLE
            self.set_media(image=get_icon_image(p, variant))
        except Exception as e:
            log.error(e)
            self.show_error()
            return
        log.debug( "set_icon " + icon_name + " - done" )

    def set_background_icon( self, icon_name ):
        p = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        log.debug( "set_background_icon " + icon_name )
        try:
            self.set_media(image=get_icon_image(p, ICON_FADED))
        except Exception as e:
            log.error(e)
            self.show_error()

    def set_text( self, text ):
        #color = 
        self.set_top_label( text, font_size=14, color=(255,224,102,255))
        #self.set_top_label( text, font_size=14)

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

    def on_ready(self):
        self.set_state("")
        return super().on_ready()
