import threading, time

from streamcontroller_plugin_tools import BackendBase 
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from loguru import logger as log
from pyparsing import Any, List

class Backend(BackendBase):

    def start_osc_server(self, ip, port):
        log.debug("Starting Server")
        self.osc_server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        log.debug("Serving on {}".format(self.osc_server.server_address))
        thread = threading.Thread(target=self.osc_server.serve_forever)
        thread.start()


    def start_osc_client(self, ip, port):
        log.debug("Starting Client")
        self.osc_client = udp_client.SimpleUDPClient(ip, port)
        log.debug("Sending on {}".format(self.osc_client._address))
        time.sleep(2)
        self.osc_client.send_message("/set_surface", [0, 127, 8211] )
   
    def default_callback(address: str, *osc_arguments: List[Any]) -> None:
        print( "default handler", address, osc_arguments )
        pass

    def heartbeat_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        pass

    def transport_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_transport_event_holder.trigger_event( path, value )

    def record_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_record_event_holder.trigger_event( path, value )

    def loop_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_loop_event_holder.trigger_event( path, value )
        #for some reason, a "/transport:play, 0" is transferred from mixbus. We need to overwirte this
        if value == 1:
            self.transport_callback("/transport_play", 1)
    
    def marker_callback(self, path, value):
        log.debug( path + " " + value )
        self.frontend.goto_start_event_holder.trigger_event( path, value )
        self.frontend.goto_end_event_holder.trigger_event( path, value )
        self.frontend.goto_next_marker_event_holder.trigger_event( path, value )
        self.frontend.goto_prev_marker_event_holder.trigger_event( path, value )
        
    def send_message(self, path, params):
        self.osc_client.send_message( path, params)

    def __init__(self):
        super().__init__()
        log.debug("Starting backend")
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler( self.default_callback )
        self.dispatcher.map("/heartbeat", self.heartbeat_callback )
        self.dispatcher.map("/transport_play", self.transport_callback )
        self.dispatcher.map("/rec_enable_toggle", self.record_callback )
        self.dispatcher.map("/loop_toggle", self.loop_callback )
        self.dispatcher.map("/marker", self.marker_callback )
        self.start_osc_server('127.0.0.1', 8000)
        self.start_osc_client('127.0.0.1', 3819)

backend = Backend() 