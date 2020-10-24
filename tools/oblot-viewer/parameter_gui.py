import tkinter as tk
from tkinter import ttk


class ParameterGUI:
    def __init__(self, master, name_style_string, name, value):
        self.master = master
        self.name_style_string = name_style_string
        self.name = name
        self.value = value
        self.name_var = tk.StringVar(master, name)
        self.value_var = tk.StringVar(master, value)
        self.name_label = ttk.Label(self.master, textvar=self.name_var, style=self.name_style_string)
        self.value_combobox = ttk.Combobox(self.master, textvariable=self.value_var,
                                           values=('0', '1'), state='readonly')
        self.value_var.trace_add('write', lambda *args: ParameterGUI.on_edit(self, args))

    def layout(self, order):
        self.name_label.grid(column=0, row=order, sticky='w')
        self.value_combobox.grid(column=1, row=order, sticky='w')

    def on_edit(self, *args):
        if str(self.value) != self.value_var.get():
            self.name_var.set('* ' + self.name + ' *')
        else:
            self.name_var.set(self.name)
