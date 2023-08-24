#!/usr/bin/env python3
import wx

from input_dialog import InputDialog

import libpve
import netconf

pve = libpve.LibPVE()

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(600, 400))

        self.panel = wx.Panel(self)

        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list_ctrl.InsertColumn(0, 'ID')
        self.list_ctrl.InsertColumn(1, 'Name')
        self.list_ctrl.InsertColumn(2, 'Size')
        self.list_ctrl.InsertColumn(3, 'Status')
        self.list_ctrl.InsertColumn(4, 'Snapshots')

        self.start_stop_button = wx.Button(self.panel, label='Start/Stop')
        self.start_stop_button.Disable()
        self.start_stop_button.Bind(wx.EVT_BUTTON, self.on_start_stop_button_click)

        self.snapshot_button = wx.Button(self.panel, label='Snapshot')
        self.snapshot_button.Disable()
        self.snapshot_button.Bind(wx.EVT_BUTTON, self.on_snapshot_button_click)

        self.clone_button = wx.Button(self.panel, label='Clone')
        self.clone_button.Disable()
        self.clone_button.Bind(wx.EVT_BUTTON, self.on_clone_button_click)

        load_button = wx.Button(self.panel, label='Reload')
        load_button.Bind(wx.EVT_BUTTON, self.on_load_button_click)

        ip_button = wx.Button(self.panel, label='IP Settings')
        ip_button.Bind(wx.EVT_BUTTON, self.on_ip_button_click)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.start_stop_button, flag=wx.ALL, border=5)
        button_sizer.Add(self.snapshot_button, flag=wx.ALL, border=5)
        button_sizer.Add(self.clone_button, flag=wx.ALL, border=5)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(ip_button, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.main_sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.main_sizer.Add(load_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.main_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)

        self.panel.SetSizer(self.main_sizer) 

        self.create_menu_bar()

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_item_deselected)

    def create_menu_bar(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit", "Exit the application")
        menu_bar.Append(file_menu, "File")

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "About", "About this application")
        menu_bar.Append(help_menu, "Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def list_vms(self):
        pve.list()
        self.update_listview(pve.vms)

    def update_listview(self, data):
        self.list_ctrl.DeleteAllItems()
        for item in data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(item['id']))
            self.list_ctrl.SetItem(index, 1, item['name'])
            self.list_ctrl.SetItem(index, 2, f'{item["ram"]}/{item["bootdisk_gb"]}')
            self.list_ctrl.SetItem(index, 3, item['status'])
            if item['id'] in pve.snaps:
                cnt = len(pve.snaps[item['id']])
                self.list_ctrl.SetItem(index, 4, str(cnt)) 
            else:
                self.list_ctrl.SetItem(index, 4, '-')

        self.main_sizer.Layout()

    def on_ip_button_click(self, event):
        dlg = netconf.NetworkConfigDialog(self)
        result = dlg.ShowModal()

        dlg.Destroy()

    def on_load_button_click(self, event):
        self.list_vms()

    def on_item_selected(self, event):
        selected_index = event.GetIndex()
        if selected_index != -1:
            item = pve.vms[selected_index]
            status = item['status']
            self.start_stop_button.Enable()
            self.clone_button.Enable()
            if status == 'running':
                self.start_stop_button.SetLabel('Stop')
                self.snapshot_button.Disable()
            else:
                self.start_stop_button.SetLabel('Start')
                self.snapshot_button.Enable()

    def on_item_deselected(self, event):
        self.start_stop_button.SetLabel('Start/Stop')
        self.start_stop_button.Disable()
        self.snapshot_button.Disable()
        self.clone_button.Disable()

    def on_start_stop_button_click(self, event):
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index != -1:
            item = pve.vms[selected_index]
            selected_id = item['id']
            if item['status']=='running':
                pve.stop_vm(selected_id)
            else:
                print('start vm')
                pve.start_vm(selected_id)
            self.list_vms()
            
    def on_snapshot_button_click(self, event):
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_id = self.list_ctrl.GetItemText(selected_index)
            pve.list_snapshots(selected_id)
            idg = InputDialog(self, title=f'Create Snapshot for VM {selected_id}', items=pve.snaps[selected_id])
            if idg.ShowModal() == wx.ID_OK:
                name, desc = idg.get_input()
                pve.snapshot(selected_id, name, desc)
            idg.Destroy()
            self.list_vms()

    def on_clone_button_click(self, event):
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_id = self.list_ctrl.GetItemText(selected_index)
            wx.MessageBox(f"Clone clicked for item with ID: {selected_id}", "Clone Button Clicked")

    def on_exit(self, event):
        self.Close()

    def on_about(self, event):
        wx.MessageBox("PVE Simple GUI\n\nCreated by DCZJ/BT", "About", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, title='ListView Example')
    frame.Show()
    app.MainLoop()

