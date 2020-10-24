#!/usr/bin/env python3
"""
Hello World, but with more meat.
"""

import os
from datetime import datetime
import struct

import wx
import serial
import wxSerialConfigDialog
from pymavlink.dialects.v20 import archer
from pymavlink import mavutil


class ViewerFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(ViewerFrame, self).__init__(*args, **kw)

        self.mav = None

        # create a panel in the frame
        pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        st = wx.StaticText(pnl, label="Recent messages")
        font = st.GetFont()
        font.PointSize += 3
        font = font.Bold()
        st.SetFont(font)

        self.st_heartbeat = wx.StaticText(pnl, label=self.labelHeartbeat(None))
        self.st_battery = wx.StaticText(pnl, label=self.labelBattery(None))

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, wx.SizerFlags().DoubleBorder())
        sizer.Add(self.st_heartbeat, wx.SizerFlags().Border())
        sizer.Add(self.st_battery, wx.SizerFlags().Border())
        pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("No serial connection selected")

        self.serial = serial.Serial()
        self.serial.timeout = 0.5  # make sure that the alive event can be checked from time to time

        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    @staticmethod
    def labelHeartbeat(msg):
        base_text = "ARCHER_HEARTBEAT time_boot_ms: {}ms , status: {}, sync_pwm: {}us"
        if msg is None:
            return base_text.format("", "", "")
        else:
            return base_text.format(msg.time_boot_ms, msg.status, msg.sync_pwm)

    @staticmethod
    def labelBattery(msg):
        base_text = "ARCHER_BATTERY voltage: {}mV , main: {}cA, tail1: {}cA, tail2: {}cA"
        if msg is None:
            return base_text.format("", "", "", "")
        else:
            return base_text.format(msg.voltage, msg.current_motor_main,
                                    msg.current_motor_tail1, msg.current_motor_tail2)

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        settingsItem = fileMenu.Append(-1, "&Serial settings\tCtrl+E",
                                       "Set up serial connection")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT, "&Exit\tCtrl+Q", "Close the program")

        editMenu = wx.Menu()
        rawItem = editMenu.Append(-1, "&Send raw values\tCtrl+R", "Send unscaled ADC inputs")
        scaledItem = editMenu.Append(-1, "&Send scaled values\tCtrl+Shift+R", "Send ADC inputs scaled for used units")

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, "&About", "Shows program information")

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnPortSettings, settingsItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, lambda evt: self.OnRaw(evt, True), rawItem)
        self.Bind(wx.EVT_MENU, lambda evt: self.OnRaw(evt, False), scaledItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnRaw(self, event, set_raw):
        parm_type = mavutil.mavlink.MAV_PARAM_TYPE_UINT8
        name = "WUT_SEND_RAW".encode('ascii')
        vstr = struct.pack(">xxxB", int(1 if set_raw else 0))
        vfloat, = struct.unpack(">f", vstr)

        msg = self.mav.param_set_encode(1, 158, name, vfloat, parm_type)
        self.serial.write(msg.pack(self.mav))

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("OBLOT Viewer\n\n" +
                      "GUI for use with custom PCBs designed for UAVs built at " +
                      "Faculty of Power and Aeronautical Engineering of Warsaw University of Technology\n\n" +
                      "Made by Marek S. Łukasiewicz in 2020",
                      "About OBLOT Viewer",
                      wx.OK | wx.ICON_INFORMATION)

    def OnPortSettings(self, event):  # wxGlade: TerminalFrame.<event_handler>
        """
        Show the port settings dialog. The reader thread is stopped for the
        settings change.
        """
        if event is not None:  # will be none when called on startup
            # self.StopThread()
            self.serial.close()
        ok = False
        # while not ok:
        if not ok:
            with wxSerialConfigDialog.SerialConfigDialog(
                    self,
                    -1,
                    "",
                    show=wxSerialConfigDialog.SHOW_BAUDRATE,
                    baudrate=57600,
                    serial=self.serial) as dialog_serial_cfg:
                dialog_serial_cfg.CenterOnParent()
                result = dialog_serial_cfg.ShowModal()
            # open port if not called on startup, open it on startup and OK too
            if result == wx.ID_OK or event is not None:
                try:
                    self.serial.open()
                except serial.SerialException as e:
                    with wx.MessageDialog(self, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)as dlg:
                        dlg.ShowModal()
                else:
                    # self.StartThread()
                    self.SetStatusText("Serial connection on {} [{}, {}, {}, {}{}{}]".format(
                        self.serial.portstr,
                        self.serial.baudrate,
                        self.serial.bytesize,
                        self.serial.parity,
                        self.serial.stopbits,
                        ' RTS/CTS' if self.serial.rtscts else '',
                        ' Xon/Xoff' if self.serial.xonxoff else '',
                    ))
                    ok = True
            else:
                # on startup, dialog aborted
                # self.alive.clear()
                ok = True

            logs_dir = 'logs'
            root_dir = os.path.dirname(os.path.abspath(__file__))
            if not os.path.exists(os.path.join(root_dir, logs_dir)):
                os.makedirs(os.path.join(root_dir, logs_dir), 0o777)

            filename = 'archer-serial-reader-output-' + datetime.now().strftime('%Y%m%dT%H%M%S.bin')
            self.mav = archer.MAVLink(open(os.path.join(root_dir, logs_dir, filename), 'wb'))

            self.timer.Start(100)

    def OnTimer(self, event):
        try:
            data = self.serial.read_all()
            # if len(data) > 0:
            #     print(' '.join('{:02x}'.format(b) for b in data))
            msgs = self.mav.parse_buffer(data)
            if msgs is not None and len(msgs) > 0:
                for msg in msgs:
                    msgId = msg.get_msgId()
                    if msgId == archer.MAVLINK_MSG_ID_ARCHER_HEARTBEAT:
                        self.st_heartbeat.SetLabelText(self.labelHeartbeat(msg))
                    elif msgId == archer.MAVLINK_MSG_ID_ARCHER_BATTERY:
                        self.st_battery.SetLabelText(self.labelBattery(msg))
                    else:
                        print(msg)

                    self.mav.send(msg)
        except Exception as e:
            self.SetStatusText(str(e))


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = ViewerFrame(None, title='OBLOT Viewer', size=(500, 250))
    frm.Show()
    app.MainLoop()
