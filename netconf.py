import wx
import json

class NetworkConfigDialog(wx.Dialog):
    def __init__(self, parent, config_data):
        super(NetworkConfigDialog, self).__init__(parent, title='Network Config')
        self.config_data = config_data.copy()

        self.init_ui()
        self.SetSize(500,500)

    def init_ui(self):
        # Create widgets
        self.ip_choice = wx.Choice(self, choices=["DHCP", "Static IP"])
        self.ip_choice.Bind(wx.EVT_CHOICE, self.on_ip_choice)
        self.ip_address_label = wx.StaticText(self, label="IP Address:")
        self.ip_address_text = wx.TextCtrl(self)
        self.netmask_label = wx.StaticText(self, label="Netmask:")
        self.netmask_text = wx.TextCtrl(self)
        self.gateway_label = wx.StaticText(self, label="Gateway:")
        self.gateway_text = wx.TextCtrl(self)
        self.dns_label = wx.StaticText(self, label="DNS Servers:")
        self.dns_text = wx.TextCtrl(self)

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
        input_grid.Add(self.dns_text, pos=(row, 2))
        
        row += 1
        input_grid.Add((10, 10), pos=(row, 0))  # Empty spacer
        input_grid.Add(self.save_button, pos=(row, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.layout.Add(input_grid, flag=wx.ALIGN_CENTER)
        self.SetSizerAndFit(self.layout)

        self.update_visibility()  # Initial visibility setup
        self.SetSizerAndFit(self.layout)

    def on_ip_choice(self, event):
        self.update_visibility()

    def update_visibility(self):
        is_static_ip = self.ip_choice.GetStringSelection() == "Static IP"
        self.ip_address_label.Show(is_static_ip)
        self.ip_address_text.Show(is_static_ip)
        self.netmask_label.Show(is_static_ip)
        self.netmask_text.Show(is_static_ip)
        self.gateway_label.Show(is_static_ip)
        self.gateway_text.Show(is_static_ip)
        self.Layout()  # Update layout

    def on_save(self, event):
        ip_mode = self.ip_choice.GetStringSelection()
        ip_address = self.ip_address_text.GetValue()
        netmask = self.netmask_text.GetValue()
        gateway = self.gateway_text.GetValue()
        dns_servers = self.dns_text.GetValue()

        self.config_data.update({
                "ip_mode": ip_mode,
                "ip_address": ip_address,
                "netmask": netmask,
                "gateway": gateway,
                "dns_servers": dns_servers.splitlines(),  # Split by lines to store multiple DNS servers
                })
        self.EndModal(wx.ID_OK)


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(600, 600))
        
        self.panel = wx.Panel(self)
        self.config_data = {
            "ip_mode": "DHCP",
            "ip_address": "",
            "netmask": "",
            "gateway": "",
            "dns_servers": [],
        }

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
        dlg = NetworkConfigDialog(self, self.config_data.copy())
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            self.config_data = dlg.config_data
            print("Modified configuration data:", self.config_data)

        dlg.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, "Network Configuration")
    frame.Show()
    app.MainLoop()





