import wx
import datetime

class SnapshotDialog(wx.Dialog):
    def __init__(self, parent, vmid, interval, items):
        super(SnapshotDialog, self).__init__(parent, title = f'Snapshots for {vmid}')
        self.exist_names = [item['name'] for item in items]
        
        self.interval_days = wx.SpinCtrl(self, min=0, max=30, initial=interval // 24)
        self.interval_hours = wx.SpinCtrl(self, min=0, max=23, initial=interval % 24)  
        
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list_ctrl.InsertColumn(0, 'Name', width=135)
        self.list_ctrl.InsertColumn(1, 'Description', width=265)
        self.list_ctrl.InsertColumn(2, 'Created', width=140)
        
        for item in items:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item['name'])
            self.list_ctrl.SetItem(index, 1, item['desc'])
            self.list_ctrl.SetItem(index, 2, item['time'].strftime('%Y-%m-%d %H:%M'))
        
        self.ok_button = wx.Button(self, wx.ID_OK, "OK")
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, label="Select Snapshot Interval (days and hours):"), flag=wx.ALL, border=5)
        interval_sizer = wx.BoxSizer(wx.HORIZONTAL)
        interval_sizer.Add(self.interval_days, flag=wx.ALL, border=5)
        interval_sizer.Add(wx.StaticText(self, label="days"), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        interval_sizer.Add(self.interval_hours, flag=wx.ALL, border=5)
        interval_sizer.Add(wx.StaticText(self, label="hours"), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.sizer.Add(interval_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.sizer.Add(wx.StaticText(self, label="Existing Snapshots:"), flag=wx.ALL, border=5)
        self.sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.ok_button, flag=wx.ALL, border=5)
        button_sizer.Add(self.cancel_button, flag=wx.ALL, border=5)

        self.sizer.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizerAndFit(self.sizer)

        self.interval_days.Bind(wx.EVT_SPINCTRL, self.on_interval_change)
        self.interval_hours.Bind(wx.EVT_SPINCTRL, self.on_interval_change)

    def on_interval_change(self, event):
        if self.interval_hours.GetValue() == 0 and self.interval_days.GetValue() == 0:
            # If the user selects 0 hours, force it to 1 hour
            self.interval_hours.SetValue(1)

    def get_interval(self):
        days = self.interval_days.GetValue()
        hours = self.interval_hours.GetValue()
        return days * 24 + hours

