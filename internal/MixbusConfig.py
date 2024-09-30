import gi

from ..internal.PluginConfig import PluginConfigWindow
from ..backend.const import (SETTING_SERVER_IP, SETTING_SERVER_PORT, SETTING_CLIENT_IP, SETTING_CLIENT_PORT, SETTING_ENABLE_TRIGGERS,SETTING_ENABLE_MIXER_SCENES )

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Pango

import re
import socket
from loguru import logger as log


class IpEntryRow(Adw.PreferencesRow):
    __gsignals__ = {
        'ip-changed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = label
        self.ip_boxes: dict[int, (Gtk.Entry, Gtk.EventControllerFocus)] = {}

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.set_child(self.main_box)

        self.build()

    def build(self):
        self.label = Gtk.Label(label=self.label, margin_start=10)
        self.main_box.append(self.label)

        self.ip_numbers_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=5, margin_bottom=5,
                                      margin_end=10)
        self.main_box.append(self.ip_numbers_box)

        self.focus_controller = Gtk.EventControllerFocus()

        for i in range(4):
            entry = Gtk.Entry(max_length=4, input_purpose=Gtk.InputPurpose.NUMBER, name=f"ip-box-{i}")
            controller = Gtk.EventControllerFocus(name=f"ip-box-controller-{i}")

            entry.add_controller(controller)

            self.ip_boxes[i] = (entry, controller)
            self.ip_numbers_box.append(entry)

            if i < 3:
                self.ip_numbers_box.append(Gtk.Label(label=".", vexpand=True))

        self.connect_events()

    def connect_events(self):
        for _, (ip_box, controller) in self.ip_boxes.items():
            ip_box.connect("activate", self.ip_box_enter_pressed)
            ip_box.connect("changed", self.ip_text_changed)
            controller.connect("leave", self.ip_changed)


    def disconnect_events(self):
        try:
            for _, (ip_box, controller) in self.ip_boxes.items():
                ip_box.disconnect_by_func(self.ip_box_enter_pressed)
                ip_box.disconnect_by_func(self.ip_text_changed)
                controller.disconnect_by_func(self.ip_changed)
        except:
            pass

    def ip_box_enter_pressed(self, entry: Gtk.Entry):
        for key, (ip_box, _) in self.ip_boxes.items():
            if ip_box.get_name() != entry.get_name():
                continue

            new_key = key + 1
            if new_key < len(self.ip_boxes):
                self.ip_boxes.get(new_key)[0].grab_focus()
                break
        self.ip_changed()

    def ip_text_changed(self, entry: Gtk.Entry):
        ip_text = entry.get_text()
        dot_index = ip_text.find(".")

        if len(ip_text) <= 0 or dot_index < 0:
            return

        self.disconnect_events()

        ip_text = ip_text.replace(".", "")

        for key, (ip_box, _) in self.ip_boxes.items():
            if ip_box.get_name() != entry.get_name():
                continue

            new_key = key + 1
            if new_key < len(self.ip_boxes):
                self.ip_boxes.get(new_key)[0].grab_focus()
                break

        entry.set_text(ip_text)
        self.connect_events()
        self.ip_changed()

    def ip_changed(self, *args):
        self.emit('ip-changed', self.get_ip())

    def get_ip(self) -> str:
        out = ""
        for key, (ip_box, _) in self.ip_boxes.items():
            out += ip_box.get_text()

            if key < 3:
                out += "."
        return out

    def set_ip(self, ip_address: str):
        self.disconnect_events()

        regex = r'(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})'

        match = re.match(regex, ip_address)

        for i in range(1, 5):
            if match:
                self.ip_boxes[i - 1][0].set_text(match.group(i))
            else:
                self.ip_boxes[i - 1][0].set_text("0")

        self.connect_events()
        self.emit('ip-changed', self.get_ip())


class MixbusConfigWindow(PluginConfigWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 400)

    def build(self):
        # Network entry connections

        # Server Connections
        # IP 
        self.server_ip_address = IpEntryRow( "Server IP Address")
        self.server_ip_address.connect("ip-changed", self.server_ip_changed)

        # Port
        self.server_port = Adw.SpinRow.new_with_range(0, 65535, 1)
        self.server_port.set_title("Server Port")
        self.server_port.connect("changed", self.server_port_changed)

        # Client Connections
        # IP 
        self.client_ip_address = IpEntryRow( "Client IP Address")
        self.client_ip_address.connect("ip-changed", self.client_ip_changed)

        # Port
        self.client_port = Adw.SpinRow.new_with_range(0, 65535, 1)
        self.client_port.set_title("Client Port")
        self.client_port.connect("changed", self.client_port_changed)

        self.enable_triggers = Adw.SwitchRow()
        self.enable_triggers.set_title("Enable Trigger Page")
        self.enable_triggers.connect( "notify::active", self.enable_triggers_changed )

        self.enable_mixer_scenes = Adw.SwitchRow()
        self.enable_mixer_scenes.set_title("Enable Mixer Scenes")
        self.enable_mixer_scenes.connect( "notify::active", self.enable_mixer_scenes_changed )

        # Add Normal UI Elements
        self.append( self.server_ip_address)
        self.append( self.server_port)
        self.append( self.client_ip_address)
        self.append( self.client_port)

        self.append( self.enable_triggers)
        self.append( self.enable_mixer_scenes)

    def load_config_ui(self):
        settings = self.plugin_base.get_settings()

        self.server_ip_address.set_ip(settings.get(SETTING_SERVER_IP, "127.0.0.1"))
        self.server_port.set_value(settings.get(SETTING_SERVER_PORT, 8000))

        self.client_ip_address.set_ip(settings.get(SETTING_CLIENT_IP, "127.0.0.1"))
        self.client_port.set_value(settings.get(SETTING_CLIENT_PORT, 8000))

        self.enable_mixer_scenes.set_active( settings.get(SETTING_ENABLE_MIXER_SCENES, False))
        self.enable_triggers.set_active( settings.get(SETTING_ENABLE_TRIGGERS, False))

    def server_ip_changed(self, entry, ip_address):
        settings = self.plugin_base.get_settings()

        settings[SETTING_SERVER_IP] = ip_address
        self.plugin_base.set_settings(settings)

    def server_port_changed(self, *args):
        settings = self.plugin_base.get_settings()

        settings[SETTING_SERVER_PORT] = int(self.server_port.get_value())
        self.plugin_base.set_settings(settings)

    def client_ip_changed(self, entry, ip_address):
        settings = self.plugin_base.get_settings()

        settings[SETTING_CLIENT_IP] = ip_address
        self.plugin_base.set_settings(settings)

    def client_port_changed(self, *args):
        settings = self.plugin_base.get_settings()

        settings[SETTING_CLIENT_PORT] = int(self.client_port.get_value())
        self.plugin_base.set_settings(settings)        
    
    def enable_triggers_changed(self, *args):
        settings = self.plugin_base.get_settings()

        settings[SETTING_ENABLE_TRIGGERS] = self.enable_triggers.get_active()
        self.plugin_base.set_settings(settings)        

    def enable_mixer_scenes_changed(self, *args):
        settings = self.plugin_base.get_settings()

        settings[SETTING_ENABLE_MIXER_SCENES] = self.enable_mixer_scenes.get_active()
        self.plugin_base.set_settings(settings)        
