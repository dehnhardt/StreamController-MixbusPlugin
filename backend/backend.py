import threading

from streamcontroller_plugin_tools import BackendBase 
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from loguru import logger as log
from pyparsing import Any, List

class Backend(BackendBase):

    def start_osc_server(self, ip, port):
        self.dispatcher.map("/transport_play", print)
        log.debug("Starting Server")
        self.osc_server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        log.debug("Serving on {}".format(self.osc_server.server_address))
        thread = threading.Thread(target=self.osc_server.serve_forever)
        thread.start()


    def start_osc_client(self, ip, port):
        log.debug("Starting Client")
        self.osc_client = udp_client.SimpleUDPClient(ip, port)
        log.debug("Sending on {}".format(self.osc_client._address))
        self.osc_client.send_message("/set_surface", 0 )
   
    def default_callback(address: str, *osc_arguments: List[Any]) -> None:
        print( "default handler", address, osc_arguments )

    def heartbeat_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        pass

    def transport_callback(self, path, value ) -> None:
        self.frontend.toggle_transport_event_holder.trigger_event( path, value )
        pass

    def send_message(self, path, params):
        self.osc_client.send_message( path, params)

    def __init__(self):
        super().__init__()
        log.debug("Starting backend")
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler( self.default_callback )
        self.dispatcher.map( "/heartbeat", self.heartbeat_callback )
        self.dispatcher.map("/transport_play", self.transport_callback )
        self.start_osc_server('127.0.0.1', 8000)
        self.start_osc_client('127.0.0.1', 3819)


backend = Backend() 