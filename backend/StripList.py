from dataclasses import dataclass

@dataclass
class Strip:
    type: str = ""
    name: str = ""
    inputs: int = 0
    outputs: int = 0
    mute: bool = False
    solo: bool = False
    has_recenable: bool = False
    recenable: bool = False


class StripList:

    def __init__(self, backend):
        self.strip_list = dict()

    def add_strip( self, type, name, inputs, outputs, mute, solo, ssid, recenable = None):
        has_recenable = False
        if type in ("AT", "MT"):
            has_recenable = True
        self.strip_list[name] = Strip( type, name, inputs, outputs, mute, solo, has_recenable, recenable )

    def get_Strip( self, name ) -> Strip:
        s = self.strip_list[name]
        if s is not None:
            return s
        else:
            return Strip()
        
    def has_recenabled( self, name ) -> bool:
        return self.get_Strip(name).has_recenable