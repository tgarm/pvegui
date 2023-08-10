import wx

class InputDialog(wx.Dialog):
    def __init__(self, parent, title, items):
        super(InputDialog, self).__init__(parent, title=title)

        self.exist_names = []
        self.name_text = wx.TextCtrl(self, value="", size=(400, -1))
        self.description_text = wx.TextCtrl(self, value="", style=wx.TE_MULTILINE, size=(400, 90))

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list_ctrl.InsertColumn(0, 'Name')
        self.list_ctrl.InsertColumn(1, 'Description')

        for item in items:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item['name'])
            self.list_ctrl.SetItem(index, 1, item['desc'])
            self.exist_names.append(item['name'])

        self.ok_button = wx.Button(self, wx.ID_OK, "OK")
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, label="Name:"), flag=wx.ALL, border=5)
        self.sizer.Add(self.name_text, flag=wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(wx.StaticText(self, label="Description:"), flag=wx.ALL, border=5)
        self.sizer.Add(self.description_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.ok_button, flag=wx.ALL, border=5)
        button_sizer.Add(self.cancel_button, flag=wx.ALL, border=5)

        self.sizer.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizerAndFit(self.sizer)
        self.name_text.Bind(wx.EVT_TEXT, self.on_name_text_change)

    def get_input(self):
        return self.name_text.GetValue(), self.description_text.GetValue()


    def is_name_unique(self, name):
        return name not in self.exist_names

    def on_name_text_change(self, event):
        name = self.name_text.GetValue()
        
        if self.is_name_unique(name):
            self.name_text.SetForegroundColour(wx.BLACK)
            self.ok_button.Enable()
        else:
            self.name_text.SetForegroundColour(wx.Colour(255, 0, 0))  # Set text color to red
            self.ok_button.Disable()

        self.name_text.Refresh()
