import threading, time, asyncio, sys

from streamcontroller_plugin_tools import BackendBase 
from StripList import StripList
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from loguru import logger as log
from pyparsing import Any, List

class Backend(BackendBase):

    async def server_loop(self):
        while self.loop:
            await asyncio.sleep(1)
        log.debug("Loop stopped")
        

    async def start_async_osc_server(self, ip, port):
        log.debug("Starting ASYNC Server")
        self.osc_server = osc_server.AsyncIOOSCUDPServer((ip, port), self.dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.osc_server.create_serve_endpoint() 
        await self.server_loop()
        log.debug("Loop stopped")
        transport.close()  # Clean up serve endpoint


    def start_osc_server(self, ip, port):
        log.debug("Starting Server")
        self.osc_server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        log.debug("Serving on {}".format(self.osc_server.server_address))
        thread = threading.Thread(target=self.osc_server.serve_forever)
        thread.start()


    def start_osc_client(self, ip, port):
        log.debug("Starting Client")
        self.osc_client = udp_client.DispatchClient(ip, port)
        self.osc_client.dispatcher = self.dispatcher
        log.debug("Sending on {}".format(self.osc_client._address))
   
    def default_callback(address: str, *osc_arguments: List[Any]) -> None:
        print( "default handler", address, osc_arguments )

    def client_default_callback(address: str, *osc_arguments: List[Any]) -> None:
        print( "client_default handler", address, osc_arguments )

    def print_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        print( "print", address, osc_arguments )

    def reply_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        print( "reply", self.last_path, osc_arguments )
        if self.last_path == "/strip/list":
            if len(osc_arguments) < 7:
                print( "strip_list has not enough arguments" )        
                return
            if len(osc_arguments) < 8:
                print( "strip_list for bus/master/monitor" )        
                self.strip_list.add_strip( type=osc_arguments[0], name=osc_arguments[1], inputs=osc_arguments[2], outputs=osc_arguments[3], mute=osc_arguments[4], solo=osc_arguments[5], ssid=osc_arguments[6])
            else:
                self.strip_list.add_strip( type=osc_arguments[0], name=osc_arguments[1], inputs=osc_arguments[2], outputs=osc_arguments[3], mute=osc_arguments[4], solo=osc_arguments[5], ssid=osc_arguments[6], recenable=osc_arguments[7])


    def toggle_transport_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_transport_event_holder.trigger_event( path, value )

    def toggle_record_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_record_event_holder.trigger_event( path, value )

    def toggle_click_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_click_event_holder.trigger_event( path, value )

    def on_click_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.on_click_event_holder.trigger_event( path, value )

    def toggle_loop_callback(self, path, value ) -> None:
        log.debug( path + " " + str(value) )
        self.frontend.toggle_loop_event_holder.trigger_event( path, value )
        #for some reason, a "/transport:play, 0" is transferred from mixbus. We need to overwirte this
        if value == 1:
            self.toggle_transport_callback("/transport_play", 1)
    
    def marker_callback(self, path, value):
        log.debug( path + " " + value )
        self.frontend.goto_start_event_holder.trigger_event( path, value )
        self.frontend.goto_end_event_holder.trigger_event( path, value )
        self.frontend.goto_next_marker_event_holder.trigger_event( path, value )
        self.frontend.goto_prev_marker_event_holder.trigger_event( path, value )


    def selected_toggle_solo_callback(self, path, value):
        log.debug( path + " " + str(value) )
        self.frontend.selected_toggle_solo_event_holder.trigger_event( path, value )
        
    def selected_toggle_mute_callback(self, path, value):
        log.debug( path + " " + str(value) )
        self.frontend.selected_toggle_mute_event_holder.trigger_event( path, value )

    def selected_toggle_rec_callback(self, path, value):
        log.debug( path + " " + str(value) )
        self.frontend.selected_toggle_rec_event_holder.trigger_event( path, value )

    def selected_toggle_polarity_callback(self, path, value):
        log.debug( path + " " + str(value) )
        self.frontend.selected_toggle_polarity_event_holder.trigger_event( path, value )

    def selected_name_callback(self, path, value):
        log.debug( "\n" + path + " " + str(value) )
        self.selected_strip = value
        #has_recenabled = self.strip_list.has_recenabled(self.selected_strip)
        self.frontend.selected_name_event_holder.trigger_event( path, value )
        #self.frontend.selected_enable_rec_event_holder.trigger_event( has_recenabled )


    def send_message(self, path, params = None):
        log.debug( path + " " +  str(params))
        self.last_path = path
        self.osc_client.send_message( path, params)

    # async def send_message_and_handle_reply(self, path, params):
    #     log.debug( path + " " +  str(params))
    #     await self.osc_client.send_message( path, params)
    #     await self.osc_client.handle_messages()

    # def hrm(self, path, params = ""):
    #      asyncio.run(self.send_message_and_handle_reply( path, params))

    def __init__(self):
        super().__init__()
        self.loop = True
        log.debug("Starting backend")
        self.last_path = ""
        self.dispatcher = Dispatcher()
        self.client_dispatcher = Dispatcher()
        self.client_dispatcher.set_default_handler( self.client_default_callback )
        self.strip_list = StripList( self )
        self.selected_strip = ""

        #self.dispatcher.set_default_handler( self.default_callback )

        self.dispatcher.map("/heartbeat", self.print_callback )
        self.dispatcher.map("/reply", self.reply_callback )
        self.dispatcher.map("/transport_play", self.toggle_transport_callback )
        self.dispatcher.map("/rec_enable_toggle", self.toggle_record_callback )
        self.dispatcher.map("/loop_toggle", self.toggle_loop_callback )
        self.dispatcher.map("/toggle_click", self.toggle_click_callback )
        self.dispatcher.map("/click/level", self.on_click_callback )
        self.dispatcher.map("/marker", self.marker_callback )

        self.dispatcher.map("/select/solo", self.selected_toggle_solo_callback )
        self.dispatcher.map("/select/mute", self.selected_toggle_mute_callback )
        self.dispatcher.map("/select/recenable", self.selected_toggle_rec_callback )
        self.dispatcher.map("/select/polarity", self.selected_toggle_polarity_callback )
        self.dispatcher.map("/select/name", self.selected_name_callback )

        self.start_osc_client('127.0.0.1', 3819)
        asyncio.run(self.start_async_osc_server('127.0.0.1', 8000))

    def on_disconnect(self, conn):
        res = super().on_disconnect(conn)
        log.debug("Stopping backend")
        self.loop = False
        return res


backend = Backend() 