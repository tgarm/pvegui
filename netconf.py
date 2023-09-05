import wx
import json
import re
import ipaddress

from network_interfaces import InterfacesFile, Auto, Allow, ValidationError

import resolv
import mline

class NetworkConfigDialog(wx.Dialog):
    def __init__(self, parent):
        super(NetworkConfigDialog, self).__init__(parent, title='Network Config')
        self.config_data = self.load_vmbr0()

        self.init_ui()
        self.SetSize(500,500)

    def load_vmbr0(self, path='/etc/network/interfaces'):
        f = InterfacesFile(path)

        vmbr = f.get_iface('vmbr0')
        cfg = {
            "ip_mode": "DHCP",
            "ip_address": "",
            "gateway": "",
            "dns_servers": [],
        }
        if vmbr.method == 'static':
            cfg['ip_mode'] = 'Static'
            cfg['ip_address'] = vmbr.address
            cfg['gateway'] = vmbr.gateway
        elif vmbr.method == 'dhcp':
            cfg['ip_mode'] = 'DHCP'
        
        print(f'vmbr: {dir(vmbr)}')
        self.resolv = resolv.parse_resolv_conf('/etc/resolv.conf')
        if self.resolv.get('nameserver')!=None:
            print(f'dns_server={self.resolv["nameserver"]}')
            cfg['dns_servers'] = self.resolv['nameserver']
        return cfg

    def save_vmbr0(self, cfg, path='/etc/network/interfaces'):
        f = InterfacesFile(path)

        vmbr = f.get_iface('vmbr0')
        if cfg['ip_mode'] == 'Static':
            vmbr.method = 'static'
            vmbr.address = cfg['ip_address']
            vmbr.gateway = cfg['gateway']
        elif cfg['ip_mode'] == 'DHCP':
            vmbr.method = 'dhcp'
        f.save()
        self.resolv['nameserver'] = cfg['dns_servers']
        resolv.write_resolv_conf(self.resolv)

    def init_ui(self):
        modes=["DHCP", "Static"]
        textSize = (180,-1)
        self.ip_choice = wx.Choice(self, choices=modes)
        self.ip_choice.Bind(wx.EVT_CHOICE, self.on_ip_choice)
        self.ip_choice.SetSelection(modes.index(self.config_data['ip_mode']))
        if self.config_data['ip_mode']!='DHCP':
            ip_address, netmask = self.parse_ip_and_netmask(self.config_data['ip_address'])
        else:
            ip_address = '192.168.1.1'
            netmask = '255.255.255.0'

        self.ip_address_label = wx.StaticText(self, label="IP Address:")
        self.ip_address_text = wx.TextCtrl(self, value=str(ip_address), size=textSize)
        self.netmask_label = wx.StaticText(self, label="Netmask:")
        self.netmask_text = wx.TextCtrl(self, value=netmask, size=textSize)
        self.gateway_label = wx.StaticText(self, label="Gateway:")
        self.gateway_text = wx.TextCtrl(self, value=self.config_data['gateway'], size=textSize)
        self.dns_label = wx.StaticText(self, label="DNS Servers:")
        self.dns_text = mline.EditableLinesWidget(self, num_lines=2, lines=self.config_data['dns_servers'])

        self.save_button = wx.Button(self, label="Save Configuration")
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

        # Layout
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.layout.Add(wx.StaticText(self, label="Network Interface Configuration"), flag=wx.ALIGN_CENTER)

        input_grid = wx.GridBagSizer(hgap=10, vgap=10)
        
        row = 0
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.ip_choice, pos=(row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        row += 1
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.ip_address_label, pos=(row, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.ip_address_text, pos=(row, 2))
        
        row += 1
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.netmask_label, pos=(row, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.netmask_text, pos=(row, 2))
        
        row += 1
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.gateway_label, pos=(row, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.gateway_text, pos=(row, 2))
        
        row += 1
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.dns_label, pos=(row, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.dns_text, pos=(row, 2), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        
        self.layout.Add(input_grid, flag=wx.ALIGN_CENTER)
        self.layout.Add(self.save_button,flag=wx.ALIGN_CENTER)
        self.SetSizerAndFit(self.layout)

        self.update_visibility()  # Initial visibility setup
        self.SetSizerAndFit(self.layout)

    def on_ip_choice(self, event):
        self.update_visibility()

    def validate_ip(self, ip):
        ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return re.match(ip_pattern, ip)

    def update_visibility(self):
        is_static_ip = self.ip_choice.GetStringSelection().startswith("Static")
        self.ip_address_label.Show(is_static_ip)
        self.ip_address_text.Show(is_static_ip)
        self.netmask_label.Show(is_static_ip)
        self.netmask_text.Show(is_static_ip)
        self.gateway_label.Show(is_static_ip)
        self.gateway_text.Show(is_static_ip)
        self.Layout()  # Update layout

    def parse_ip_and_netmask(self, input_string):
        parts = input_string.split("/")
        if len(parts) == 1:
            ip_str = parts[0]
            netmask = None  # No netmask provided
        elif len(parts) == 2:
            ip_str, netmask = parts
        else:
            raise ValueError("Invalid input format")

        print(f'ipstr:{ip_str}')
        ip = ipaddress.ip_address(ip_str)

        if netmask is not None:
            netmask = str(ipaddress.ip_network(f"0.0.0.0/{netmask}", strict=False).netmask)  # Convert netmask object to string

        return ip, netmask

    def netmask_to_cidr(self, netmask):
        # Convert netmask in dotted decimal format to CIDR notation
        netmask_parts = netmask.split(".")
        if len(netmask_parts) != 4:
            raise ValueError("Invalid netmask format")

        cidr = sum([bin(int(part)).count("1") for part in netmask_parts])
        return cidr

    def combine_ip_and_netmask(self, ip, netmask):
        if isinstance(netmask, str):
            netmask = self.netmask_to_cidr(netmask)

        return f"{ip}/{netmask}"

    def on_save(self, event):
        ip_mode = self.ip_choice.GetStringSelection()
        ip_address = self.ip_address_text.GetValue()

        if not self.validate_ip(ip_address):
            wx.MessageBox("Invalid IP address format.", "Error", wx.OK | wx.ICON_ERROR)
            return

        netmask = self.netmask_text.GetValue()
        gateway = self.gateway_text.GetValue()
        dns_servers = self.dns_text.get_lines()

        self.config_data.update({
                "ip_mode": ip_mode,
                "ip_address": self.combine_ip_and_netmask(ip_address, netmask),
                "gateway": gateway,
                "dns_servers": dns_servers
                })
        self.save_vmbr0(self.config_data)
        self.EndModal(wx.ID_OK)

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(600, 600))
        
        self.panel = wx.Panel(self)
        self.init_ui()

    def init_ui(self):
        self.config_button = wx.Button(self.panel, label="Configure Network")
        self.config_button.Bind(wx.EVT_BUTTON, self.show_config_dialog)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(self.panel, label="Main Application"), flag=wx.ALIGN_CENTER)
        main_sizer.Add(self.config_button, flag=wx.ALIGN_CENTER)

        self.panel.SetSizerAndFit(main_sizer)
        self.Center()

    def show_config_dialog(self, event):
        dlg = NetworkConfigDialog(self)
        result = dlg.ShowModal()

        dlg.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, "Network Configuration")
    frame.Show()
    app.MainLoop()





