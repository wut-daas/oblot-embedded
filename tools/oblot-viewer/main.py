#!/usr/bin/env python3

import os
from datetime import datetime
import struct

import tkinter as tk
from tkinter import ttk
import serial
from pymavlink.dialects.v20 import archer
from pymavlink import mavutil

from utils import *
from parameter_gui import ParameterGUI

root = tk.Tk()
root.title('OBLOT Viewer')

main_frame = ttk.Frame(root, padding="3")

top_frame = ttk.Frame(main_frame)

title_style = ttk.Style()
title_style.configure("Title.Label", font=(None, '14'))
title_label = ttk.Label(top_frame, text='OBLOT Viewer     ', style="Title.Label")

serial_conn = serial.Serial()
mav = None
heartbeat_text = tk.StringVar(root, heartbeat_format(None))
battery_text = tk.StringVar(root, battery_format(None))

serial_ports_available = list_serial_ports()
serial_port = tk.StringVar()
serial_port_combobox = ttk.Combobox(top_frame, textvariable=serial_port,
                                    values=serial_ports_available[1], state='readonly', width=30)

serial_baud = tk.StringVar(root, '57600')
serial_bauds_available = serial_conn.BAUDRATES
serial_baud_combobox = ttk.Combobox(top_frame, textvariable=serial_baud,
                                    values=serial_bauds_available, state='readonly', width=30)

parameters = list()


def read_serial():
    global serial_conn
    global mav
    try:
        data = serial_conn.read_all()
        # if len(data) > 0:
        #     print(' '.join('{:02x}'.format(b) for b in data))
        msgs = mav.parse_buffer(data)
        if msgs is not None and len(msgs) > 0:
            for msg in msgs:
                msgId = msg.get_msgId()
                if msgId == archer.MAVLINK_MSG_ID_ARCHER_HEARTBEAT:
                    heartbeat_text.set(heartbeat_format(msg))
                elif msgId == archer.MAVLINK_MSG_ID_ARCHER_BATTERY:
                    battery_text.set(battery_format(msg))
                elif msgId == archer.MAVLINK_MSG_ID_PARAM_VALUE:
                    vstr = struct.pack(">f", msg.param_value)
                    vbyte, = struct.unpack(">xxxB", vstr)
                    print('received {}: {}'.format(msg.param_id, vbyte))

                    try:
                        parm = next(p for p in parameters if p.name == msg.param_id)
                        parm.value = str(int(vbyte))
                        parm.on_edit(None)
                    except StopIteration:
                        print('New parameter ' + msg.param_id)
                        parameters.append(ParameterGUI(parameter_frame, 'Name.Label', msg.param_id, int(vbyte)))

                        for order, param in enumerate(parameters):
                            param.layout(order)

                    msg.param_id = msg.param_id.encode('ascii')  # Re-encode for sending to file
                else:
                    print(msg)

                mav.send(msg)
    except Exception as e:
        print('exception: ' + str(e))

    global root
    root.after(100, read_serial)


def connect():
    port_name = ''
    for name in serial_ports_available[0]:
        if name in serial_port.get():
            port_name = name
            break

    global serial_conn
    serial_conn = serial.Serial(port_name, baudrate=int(serial_baud.get()))

    logs_dir = 'logs'
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root_dir, logs_dir)):
        os.makedirs(os.path.join(root_dir, logs_dir), 0o777)

    filename = 'archer-serial-reader-output-' + datetime.now().strftime('%Y%m%dT%H%M%S.bin')
    global mav
    mav = archer.MAVLink(open(os.path.join(root_dir, logs_dir, filename), 'wb'))

    global root
    root.after(100, read_serial)


serial_button = ttk.Button(top_frame, text="Connect", command=connect)

message_frame = ttk.Frame(main_frame)

name_style = ttk.Style()
name_style.configure("Name.Label", font=(None, '9', 'bold'))
heartbeat_name_label = ttk.Label(message_frame, text='ARCHER_HEARTBEAT', style="Name.Label")
heartbeat_values_label = ttk.Label(message_frame, textvariable=heartbeat_text)
battery_name_label = ttk.Label(message_frame, text='ARCHER_BATTERY', style="Name.Label")
battery_values_label = ttk.Label(message_frame, textvariable=battery_text)

paramcontrol_frame = ttk.Frame(main_frame)
parameter_frame = ttk.Frame(main_frame)
parameters.append(ParameterGUI(parameter_frame, 'Name.Label', 'WUT_SEND_RAW', '0'))


def write_params():
    for param in parameters:
        if str(param.value) != param.value_var.get():
            parm_type = mavutil.mavlink.MAV_PARAM_TYPE_UINT8
            name = param.name.encode('ascii')
            vstr = struct.pack(">xxxB", int(1 if param.value_var.get() == '1' else 0))
            vfloat, = struct.unpack(">f", vstr)

            global mav
            global serial_conn
            msg = mav.param_set_encode(1, 158, name, vfloat, parm_type)
            serial_conn.write(msg.pack(mav))

            print('sent {}: {}'.format(param.name, vstr))


def refresh_params():
    msg = mav.param_request_list_encode(1, 158)
    serial_conn.write(msg.pack(mav))


paramcontrol_write_button = ttk.Button(paramcontrol_frame, text="Write params", command=write_params)
paramcontrol_refresh_button = ttk.Button(paramcontrol_frame, text="Refresh params", command=refresh_params)
paramcontrol_save_button = ttk.Button(paramcontrol_frame, text="Save param file",
                                      command=NotImplemented, state='disabled')
paramcontrol_load_button = ttk.Button(paramcontrol_frame, text="Load param file",
                                      command=NotImplemented, state='disabled')

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.grid(column=0, row=0, sticky='nsew')
main_frame.columnconfigure(0, weight=1)

top_frame.grid(column=0, row=0, sticky='we', ipady=12)
top_frame.columnconfigure(0, weight=1)
title_label.grid(column=0, row=0, rowspan=2, sticky='w')
serial_port_combobox.grid(column=1, row=0)
serial_baud_combobox.grid(column=1, row=1)
serial_button.grid(column=2, row=0, rowspan=2, sticky='nsew')

message_frame.grid(column=0, row=1, sticky='we', ipady=12)
message_frame.columnconfigure(0, weight=1)
heartbeat_name_label.grid(column=0, row=0, sticky='w')
heartbeat_values_label.grid(column=0, row=1, sticky='w')
battery_name_label.grid(column=0, row=2, sticky='w')
battery_values_label.grid(column=0, row=3, sticky='w')

paramcontrol_frame.grid(column=0, row=2, sticky='we', ipady=12)
paramcontrol_frame.columnconfigure(0, weight=1)
paramcontrol_frame.columnconfigure(1, weight=1)
paramcontrol_write_button.grid(column=0, row=0, sticky='nsew')
paramcontrol_refresh_button.grid(column=1, row=0, sticky='nsew')
paramcontrol_save_button.grid(column=0, row=1, sticky='nsew')
paramcontrol_load_button.grid(column=1, row=1, sticky='nsew')

parameter_frame.grid(column=0, row=3, sticky='we', ipady=12)
parameter_frame.columnconfigure(0, weight=1)
parameter_frame.columnconfigure(1, weight=1)
for order, param in enumerate(parameters):
    param.layout(order)

root.mainloop()
