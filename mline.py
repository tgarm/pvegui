import wx

class EditableLinesWidget(wx.Panel):
    def __init__(self, parent, num_lines=3, lines=None):
        super().__init__(parent)
        
        if lines is None:
            lines = [""] * num_lines
        
        while len(lines)<num_lines:
            lines.append('')

        self.line_textctrls = []

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        for line in lines:
            line_textctrl = wx.TextCtrl(self, value=line)
            self.line_textctrls.append(line_textctrl)
            main_sizer.Add(line_textctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
    
    def get_lines(self):
        return [textctrl.GetValue() for textctrl in self.line_textctrls]
    
    def set_lines(self, lines):
        for textctrl, line in zip(self.line_textctrls, lines):
            textctrl.SetValue(line)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Editable Lines Widget Example", size=(400, 300))
        
        self.panel = wx.Panel(self)
        self.lines_widget = EditableLinesWidget(self.panel, num_lines=5)
        
        load_button = wx.Button(self.panel, label="Load Lines")
        load_button.Bind(wx.EVT_BUTTON, self.on_load_button)
        
        save_button = wx.Button(self.panel, label="Save Lines")
        save_button.Bind(wx.EVT_BUTTON, self.on_save_button)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.lines_widget, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(load_button, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 10)
        main_sizer.Add(save_button, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 5)
        
        self.panel.SetSizer(main_sizer)
    
    # ... (Rest of the MainFrame class code)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

