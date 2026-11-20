import threading, time, asyncio, sys

from streamcontroller_plugin_tools import BackendBase 
from StripList import StripList
from pythonosc import udp_client, osc_server
from pythonosc.osc_message import OscMessage
from pythonosc.dispatcher import Dispatcher
from loguru import logger as log
from const import ( SETTING_SERVER_IP, SETTING_SERVER_PORT, SETTING_CLIENT_IP, SETTING_CLIENT_PORT)

from typing import Any, List

# Seconds without a /heartbeat before Mixbus is considered gone
HEARTBEAT_TIMEOUT = 3
# Seconds between attempts to register with Mixbus while it is gone; the last value repeats
RETRY_DELAYS = (3, 5, 10)
# Number of mixer scene slots Mixbus reports names for
MIXER_SCENE_COUNT = 8
# Size of the trigger grid Mixbus reports: routes (columns) and clip slots per route (rows)
TRIGGER_ROUTE_COUNT = 8
TRIGGER_ROW_COUNT = 8
# Trigger slot states as reported by Mixbus
TRIGGER_EMPTY = -1

class Backend(BackendBase):

    async def server_loop(self):
        loop = asyncio.get_running_loop()
        retry_attempt = 0
        next_retry = 0.0
        while self.loop:
            await asyncio.sleep(1)
            now = time.monotonic()
            if now - self.heartbeat <= HEARTBEAT_TIMEOUT:
                retry_attempt = 0
                continue

            if self.connected:
                self.connected = False
                next_retry = now
            if not self.offline_reported:
                log.info("Mixbus/Ardour is not answering - waiting for it")
                self.offline_reported = True
            if now < next_retry:
                continue

            # Mixbus forgets the surface when it restarts, so it has to be registered again.
            # The frontend call blocks, so keep it out of the loop that receives OSC messages.
            try:
                await loop.run_in_executor(None, self.frontend.init_daw)
            except Exception as e:
                log.error("Could not register with Mixbus: {}", e)
            next_retry = time.monotonic() + RETRY_DELAYS[min(retry_attempt, len(RETRY_DELAYS) - 1)]
            retry_attempt += 1
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
        self.osc_server = osc_server.ThreadingOSCUDPServer((ip, port, True), self.dispatcher)
        log.debug("Serving on {}".format(self.osc_server.server_address))
        thread = threading.Thread(target=self.osc_server.serve_forever)
        thread.start()


    def start_osc_client(self, ip, port):
        log.debug("Starting Client")
        self.osc_client = udp_client.DispatchClient(ip, port)
        self.osc_client.dispatcher = self.dispatcher
        log.debug("Sending on {}".format(self.osc_client._address))
   
    def default_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        log.debug( "default handler {} {}", address, osc_arguments )

    def heartbeat_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        self.heartbeat = time.monotonic()
        if not self.connected:
            self.connected = True
            self.offline_reported = False
            log.info("Connected to Mixbus/Ardour")
            # /set_surface gets no reply, so only the first heartbeat shows that Mixbus took the registration
            self.send_message("/strip/list")

    def client_default_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        log.debug( "client_default handler {} {}", address, osc_arguments )

    def print_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        log.debug( "print {} {}", address, osc_arguments )

    def reply_callback(self, address: str, *osc_arguments: List[Any]) -> None:
        log.debug( "reply {} {}", self.last_path, osc_arguments )
        if self.last_path == "/strip/list":
            if len( osc_arguments ) == 4:
                log.debug( "End of striplist")
                self.strip_list.enable()
            if len(osc_arguments) < 7:
                log.debug( "strip_list has not enough arguments" )        
                return
            if len(osc_arguments) < 8:
                log.debug( "strip_list for bus/master/monitor" )        
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
        log.debug( path + " " + str(value) )
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
        has_recenabled = self.strip_list.has_recenabled(self.selected_strip)
        self.frontend.selected_name_event_holder.trigger_event( path, value )
        self.frontend.selected_enable_rec_event_holder.trigger_event( has_recenabled )


    def trigger_grid_callback(self, path, progress, *states) -> None:
        # Mixbus repeats this message while the transport moves, so only pass on real changes
        route = int(path.split("/")[2])
        states = tuple(int(state) for state in states)
        if self.trigger_states.get(route) == states:
            return
        self.trigger_states[route] = states
        log.debug( "{} {}", path, states )
        self.frontend.trigger_grid_event_holder.trigger_event( path, states )

    def trigger_bank_callback(self, path, total_routes, route_start, total_triggers, row_start) -> None:
        bank = (int(route_start), int(row_start))
        if bank == self.trigger_bank:
            return
        self.trigger_bank = bank
        log.debug( "{} {}", path, bank )
        self.frontend.trigger_bank_event_holder.trigger_event( path, bank )

    def get_trigger_bank(self) -> tuple:
        return self.trigger_bank

    def get_trigger_state(self, route: int, row: int) -> int:
        states = self.trigger_states.get(route, ())
        return states[row] if 0 <= row < len(states) else TRIGGER_EMPTY

    def mixer_scene_name_callback(self, path, name = "") -> None:
        log.debug( path + " " + str(name) )
        self.scene_names[int(path.split("/")[2])] = name
        self.frontend.mixer_scene_name_event_holder.trigger_event( path, name )

    def get_mixer_scene_name(self, scene: int) -> str:
        return self.scene_names.get(scene, "")

    def send_message(self, path, params = None):
        log.debug( path + " " +  str(params))
        self.last_path = path
        self.osc_client.send_message( path, params)

    def send_message_and_handle_reply(self, path, params = None):
        log.debug( path + " " +  str(params))
        self.osc_client.send_message( path, params)
        res=OscMessage(self.osc_client._sock.recv(4096))
        log.debug( str(res) )
        
    # def hrm(self, path, params = ""):
    #      asyncio.run(self.send_message_and_handle_reply( path, params))

    def __init__(self):
        super().__init__()
        self.loop = True
        # Set before the OSC server starts, because /heartbeat can arrive at any time afterwards
        self.heartbeat = time.monotonic()
        self.connected = False
        self.offline_reported = False
        self.scene_names = {}
        self.trigger_states = {}
        self.trigger_bank = (0, 0)
        log.debug("Starting backend")
        self.last_path = ""
        self.dispatcher = Dispatcher()
        self.client_dispatcher = Dispatcher()
        self.client_dispatcher.set_default_handler( self.client_default_callback )
        self.strip_list = StripList( self )
        self.selected_strip = ""

        #self.dispatcher.set_default_handler( self.default_callback )

        self.dispatcher.map("/heartbeat", self.heartbeat_callback )
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

        self.dispatcher.map( "/trigger_grid/bank", self.trigger_bank_callback )
        for route in range(TRIGGER_ROUTE_COUNT):
            self.dispatcher.map( "/trigger_grid/{}/state".format(route), self.trigger_grid_callback )

        for scene in range(MIXER_SCENE_COUNT):
            self.dispatcher.map( "/mixer_scene/{}/name".format(scene), self.mixer_scene_name_callback )

        self.start_osc_client(
            self.get_setting( SETTING_CLIENT_IP, '127.0.0.1'), 
            self.get_setting( SETTING_CLIENT_PORT, 3819 ) )
        asyncio.run(self.start_async_osc_server( 
            self.get_setting( SETTING_SERVER_IP, '127.0.0.1'), 
            self.get_setting( SETTING_SERVER_PORT, 8000 ) ) )

    def on_disconnect(self, conn):
        res = super().on_disconnect(conn)
        log.debug("Stopping backend")
        self.loop = False
        return res
    
    def get_setting(self, key: str, default=None):
        return self.frontend.get_settings().get(key, default)



backend = Backend() 