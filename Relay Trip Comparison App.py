import math
import tkinter as tk
from tkinter import filedialog,ttk, messagebox, Toplevel
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import simpledialog, messagebox
import numpy as np
import comtrade
from tkinter import filedialog, Toplevel, Listbox, END
import re
import sys
from matplotlib.widgets import Slider, SliderBase
import mplcursors
from tkinter import font as tkFont  # 用于字体定义

class Parameters:#Ibias calculation parameters
    def __init__(self):##Ip is primary side current, Is is secondary side current

        self.Idiff=None
        self.A=None
        self.Ip=None
        self.Is=None
        self.K1=1 #defulat K1 and K2 are 1
        self.K2=1 
class Ibiascal(Parameters):
    """There are 7 methods to calculate the bias current"""

    def __init__(self):
        super().__init__()
        self.Ibias = []  # Initialize Ibias as an empty list

    def Ibias1(self):
        """Calculate Ibias using Method 1 (Siemens relay, GEC/AREVA)"""
        self.Ibias = [(abs(ip) + abs(is_value)) / self.K1 for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias2(self):
        """Calculate Ibias using Method 2 (ABB relay series, AEG relay series)"""
        self.Ibias = [(ip - is_value) / self.K1 for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias3(self):
        """Calculate Ibias using Method 3 (GE Multilin Series)"""
        self.Ibias = [(abs(ip) + abs(is_value) * self.K2) / self.K1 for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias4(self):
        """Calculate Ibias using Method 4 (ABB relay series, Siemens relay series, GE relay, ELIN relay series)"""
        self.Ibias = [max(abs(ip), abs(is_value)) for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias5(self):
        """Calculate Ibias using Method 5 (The smaller one value)"""
        self.Ibias = [min(abs(ip), abs(is_value)) for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias6(self):
        """Calculate Ibias using Method 6 (ABB relay series RET316, NSE differential relay)"""
        self.Ibias = [math.sqrt(abs(ip * is_value * math.cos(self.A))) for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias

    def Ibias7(self):
        """Calculate Ibias using Method 7 (ZIV transformer differential relays)"""
        self.Ibias = [(abs(ip) + abs(is_value) - abs(self.Idiff)) / self.K1 for ip, is_value in zip(self.Ip, self.Is)]
        return self.Ibias
class Difftest:
    def __init__(self, root):
    
        self.root = root
        self.root.title("Relay Trip Comparison App")
        self.slopes = []  # Initialize slopes as an empty list
        self.bases = []   # Initialize bases as an empty list
        self.pick_up = None
        self.Highest = None
        self.df = None
        self.parameters = Parameters()  # Create an instance of the Parameters class
        self.data_array1 = [None, None, None]
        self.data_array2 = [None, None, None]
        self.rec=None
        self.file_path = None
        self.data = None
        self.special_data = {}
        self.method=1
        self.comtrade_listboxes = []
        self.comtrade_dataframes = [None, None] 
        self.cfg_file_paths = ["", ""]
        self.dat_file_paths = ["", ""]
        self.max_selections = 3
        self.loader_window = None

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14)  # 调整字体大小为14
        self.root.option_add("*Font", default_font)

        # 使用Frame增加一层布局，以便更灵活地控制边距和排列
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Other attributes
        #self.create_widgets()
        self.create_buttons()

    def create_buttons(self):
            self.plot_canvas = tk.Canvas(self.root)
            self.plot_canvas.pack(side='left', fill='x', expand=True)
            # 定义按钮并紧密排列
            buttons = [
                ("Plot Standard Trip", self.plot_standardtrip),
                ("Load COMTRADE file", self.create_loader_window),
                ("Select Current", self.select_current),
                ("Plot real trip curve", self.plot_real_trip),
                ("Load RIO File", self.load_file),
                ("Show RIO File Content", self.show_data),
                ("Show Real Time Change", self.plot_realtime_datas),
            ]

            for text, command in buttons:
                btn = tk.Button(self.main_frame, text=text, command=command)
                # fill='x'使按钮宽度随窗口变化，padx和pady增加间距，使布局更紧密
                btn.pack(fill='x', expand=True, pady=5)

    def create_widgets(self):
        # Create canvas for plotting
        self.plot_canvas = tk.Canvas(self.root)
        self.plot_canvas.pack(side='left', fill='x', expand=True)

        # File input button for trip_action_curve CSV
        '''self.btn_load_csv = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.btn_load_csv.pack(side='right', expand=True, fill='y', pady=5)'''

        # Plot Standard trip and Real trip button
        '''self.btn_plot_curve = tk.Button(self.root, text="Plot Standard Trip and Real trip", command=self.plot_datas)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)'''

        # Plot Standard trip
        self.btn_plot_curve = tk.Button(self.root, text="Plot Standard Trip", command=self.plot_standardtrip)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)

        # New button to show and modify parameters
        '''self.btn_show_parameters = tk.Button(self.root, text="Show/Modify Parameters", command=self.show_modify_parameters)
        self.btn_show_parameters.pack(side='top', expand=True, fill='x', pady=5)'''

        # Dropdown menu for Ibias calculation method
        '''self.ibias_method_var = tk.StringVar()
        self.ibias_method_var.set("Method 1")  # Default method
        ibias_method_options = ["Method 1", "Method 2", "Method 3", "Method 4", "Method 5", "Method 6", "Method 7"]
        ibias_method_menu = tk.OptionMenu(self.root, self.ibias_method_var, *ibias_method_options)
        ibias_method_menu.pack(side='top', expand=True, fill='x', pady=5)'''
        # Load Comtrade file 
        self.btn_plot_curve = tk.Button(self.root, text="Load COMTRADE file", command=self.create_loader_window)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
        #Show COMTRADE file 
        self.btn_plot_curve = tk.Button(self.root, text="Select Current", command=self.select_current)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
        #Plot Real Trip curve
        self.btn_plot_curve = tk.Button(self.root, text="Plot real trip curve", command=self.plot_real_trip)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
        # Add button for loading RIO file
        self.btn_load_rio = tk.Button(self.root, text="Load RIO File", command=self.load_file)
        self.btn_load_rio.pack(side='top', expand=True, fill='x', pady=5)

        # Add button for showing RIO file content
        self.btn_show_rio = tk.Button(self.root, text="Show RIO File Content", command=self.show_data)
        self.btn_show_rio.pack(side='top', expand=True, fill='x', pady=5)

        self.btn_show_rio = tk.Button(self.root, text="Show Real Time Change", command=self.plot_realtime_datas)
        self.btn_show_rio.pack(side='top', expand=True, fill='x', pady=5)

    def log_to_file(self,message):
        with open('C:/Users/DavZha01/OneDrive - OMICRON electronics GmbH/Part-Time Project/debug_log.txt', 'a') as log_file:
            print(message, file=log_file)#debug file

    def rearrange_Ibias_values(self, Ibias_values):
        # 确保 Ibias_values 的长度是 3 的倍数
        if len(Ibias_values) % 3 != 0:
            print("Error: The length of Ibias_values is not a multiple of 3.")
            return []

        # 计算每组的长度
        group_length = len(Ibias_values) // 3

        # 将 Ibias_values 分成三组
        Ibias_values_grouped = [Ibias_values[i:i + group_length] for i in range(0, len(Ibias_values), group_length)]

        return Ibias_values_grouped
    def calculate_Ibias(self):
        try:
            print("Starting calculate_Ibias...")
            if not self.data_array1 or not self.data_array2:
                raise ValueError("Data arrays are empty or not set")

            #self.log_to_file(f"data_array1: {self.data_array1}")
            #self.log_to_file(f"data_array2: {self.data_array2}") #for debug,show data in txt file 

            Ip_values = [item for sublist in self.data_array1 for item in sublist]
            Is_values = [item for sublist in self.data_array2 for item in sublist]

            '''self.log_to_file(f"Ip_values: {Ip_values}")
            self.log_to_file(f"Is_values: {Is_values}")'''

            ibias_calculator = Ibiascal()
            ibias_calculator.Ip = self.calculate_rms_values(Ip_values)
            ibias_calculator.Is = self.calculate_rms_values(Is_values)

    
            print(f"Selected Ibias calculation method: {self.method}")

            # Call the appropriate Ibias calculation method
            if self.method == 1:
                ibias_calculator.Ibias1()
            elif self.method == 2:
                ibias_calculator.Ibias2()
            elif self.method == 3:
                ibias_calculator.Ibias3()
            elif self.method == 4:
                ibias_calculator.Ibias4()
            elif self.method == 5:
                ibias_calculator.Ibias5()
            elif self.method == 6:
                ibias_calculator.Ibias6()
            elif self.method == 7:
                ibias_calculator.Ibias7()

            Ibias_values = ibias_calculator.Ibias
            self.log_to_file(f"Calculated Ibias_values: {Ibias_values}")

            self.Ibias=self.rearrange_Ibias_values(Ibias_values)
            self.log_to_file(f"Calculated self.Ibias_values: {self.Ibias}")
            #result_array = list(zip(Ibias_values))
            #self.log_to_file(f"Result Array: {result_array}")

            #self.Ibias = result_array
            print("Ibias saved successfully.")
            messagebox.showinfo("Success", "Ibias saved successfully.")
            #return result_array
    
        except ValueError as e:
            print(f"Error converting to float: {e}")
    def calculate_Idiff(self):
        print("Starting calculate_Idiff...")
        if len(self.data_array1) >= 3 and len(self.data_array2) >= 3:
            self.Idiff = []
            #self.log_to_file(f"data_array1: {self.data_array1}")
            #self.log_to_file(f"data_array2: {self.data_array2}")

            for i in range(3):
                Ip_sublist = self.calculate_rms_values(self.data_array1[i])
                Is_sublist = self.calculate_rms_values(self.data_array2[i])
                self.log_to_file(f"Processing sublist {i}: Ip_sublist = {Ip_sublist}, Is_sublist = {Is_sublist}")

                Idiff_sublist = [ip - is_value for ip, is_value in zip(Ip_sublist, Is_sublist)]
                self.Idiff.append(Idiff_sublist)
                self.log_to_file(f"Calculated Idiff_sublist: {Idiff_sublist}")

            self.log_to_file(f"Final Idiff: {self.Idiff}")
            print("Idiff saved successfully.")
            messagebox.showinfo("Success", "Idiff saved successfully.")
        else:
            print("Error: Not enough sublists to calculate Idiff")
            messagebox.showinfo("Error: Not enough sublists to calculate Idiff")
    def calculate_rms_values(self,data_list):
        def calculate_rms(values):
            squared_values = np.square(values)
            mean_of_squares = np.mean(squared_values)
            rms_value = np.sqrt(mean_of_squares)
            return rms_value

        return np.array([calculate_rms(data_list[:i+1]) for i in range(len(data_list))])
    
    def plot_realtime_datas(self):
        # Clear the previous plot
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        
        self.fig = Figure(figsize=(6, 4))
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        trigger_time_text = f"Trigger Time: {self.trigger_time}"

        if self.line!=(0,0):
            # First segment: self.start to self.line
            x1=self.start[0]
            y1=self.start[1]
            x2=self.line[0]
            y2=self.line[1]
            x3=self.stop[0]
            y3=self.stop[1]
            print(f"First segment points: x1 = {x1}, x2 = {x2}, x3 = {x3}")  # Print x1 and x2 for first segment
            print(f" x2 = {x2}")
            slope1 = (y2 - y1) / (x2 - x1)
            intercept1 = y1 - slope1 * x1
            x_values1 = np.linspace(x1, x2, 500)
            y_values1 = slope1 * x_values1 + intercept1
            y_values1 = np.clip(y_values1, self.pick_up, self.Highest)
            self.ax.plot(x_values1, y_values1, color='black')

            # Second segment: self.line to self.stop
            x3, y3 = self.stop
            slope2 = (y3 - y2) / (x3 - x2)
            intercept2 = y2 - slope2 * x2
            x_values2 = np.linspace(x2, x3+10, 1000)
            y_values2 = slope2 * x_values2 + intercept2
            y_values2 = np.clip(y_values2, self.pick_up, self.Highest)
            self.ax.plot(x_values2, y_values2, color='black')

        else:
            # Single segment: self.start to self.stop
            x1 = self.start[0]
            y1=self.start[1]
            x2=self.stop[0]
            y2=self.stop[1]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            x_values = np.linspace(x1, x2+10, 1000)
            y_values = slope * x_values + intercept
            y_values = np.clip(y_values, self.pick_up, self.Highest)
            self.ax.plot(x_values, y_values, color='black')
    

        # Plotting the initial data
        self.lines = []  # Store line objects for updating
        for i in range(3):  # Assuming there are exactly 3 curves
            line, = self.ax.plot(self.Ibias[i], self.Idiff[i], label=f'Phase {i+1} current, {trigger_time_text}')
            self.lines.append(line)

        # Setup the legend, labels
        self.ax.legend()
        self.ax.set_xlabel('Ibias')
        self.ax.set_ylabel('Idiff')

        time_array = np.array(self.time)

        # Slider setup
        axcolor = 'lightgoldenrodyellow'
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
        self.slider = Slider(ax_slider, 'Time', time_array.min(), time_array.max(), valinit=time_array.max())

        # Update plot based on slider
        self.slider.on_changed(self.update_plot)

        # Embedding figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_plot(self, val):
        selected_time = self.slider.val
        mask = self.time <= selected_time

        for i, line in enumerate(self.lines):
            line.set_xdata(np.array(self.Ibias[i])[mask])
            line.set_ydata(np.array(self.Idiff[i])[mask])

        self.fig.canvas.draw_idle()
    
    def plot_datas(self):
        # Destroy the previous Tkinter window
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        self.lines = [] 
        # Initial plot of X and Y axes
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)
        if self.line!=(0,0):
            # First segment: self.start to self.line
            x1=self.start[0]
            y1=self.start[1]
            x2=self.line[0]
            y2=self.line[1]
            x3=self.stop[0]
            y3=self.stop[1]
            print(f"First segment points: x1 = {x1}, x2 = {x2}, x3 = {x3}")  # Print x1 and x2 for first segment
            print(f" x2 = {x2}")
            slope1 = (y2 - y1) / (x2 - x1)
            intercept1 = y1 - slope1 * x1
            x_values1 = np.linspace(x1, x2, 500)
            y_values1 = slope1 * x_values1 + intercept1
            y_values1 = np.clip(y_values1, self.pick_up, self.Highest)
            a.plot(x_values1, y_values1, color='black')

            # Second segment: self.line to self.stop
            x3, y3 = self.stop
            slope2 = (y3 - y2) / (x3 - x2)
            intercept2 = y2 - slope2 * x2
            x_values2 = np.linspace(x2, x3+10, 1000)
            y_values2 = slope2 * x_values2 + intercept2
            y_values2 = np.clip(y_values2, self.pick_up, self.Highest)
            a.plot(x_values2, y_values2, color='black')
                        # Check if both 'Ibias' and 'Idiff' are defined as class attributes
            if hasattr(self, 'Ibias') and hasattr(self, 'Idiff') and len(self.Idiff)<= 3:
                    # 获取 self.Ibias 中元组的数量
                for i in range(3):
                                # Extracting the i-th element from each tuple in Ibias
                            # Check if the lengths match
                    if len(self.Ibias[i]) == len(self.Idiff[i]):
                        a.plot(self.Ibias[i], self.Idiff[i], label=f'Real Trip Curve {i+1}', linestyle='--')
                        a.legend()
                    else:
                        messagebox.WARNING(f"Error: Mismatch in data length for curve {i+1}")
                        print(f"Error: Mismatch in data length for curve {i+1}")
                    
            else:
                print("Error: self.Ibias or self.Idiff does not contain enough data.")
                messagebox.WARNING("Error: self.Ibias or self.Idiff does not contain enough data.")

                            # Collect x_values
                            #x_values = np.arange(0, float(max(Ibias_values)), 0.001)
        else:
            # Single segment: self.start to self.stop
            x1 = self.start[0]
            y1=self.start[1]
            x2=self.stop[0]
            y2=self.stop[1]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            x_values = np.linspace(x1, x2+10, 1000)
            y_values = slope * x_values + intercept
            y_values = np.clip(y_values, self.pick_up, self.Highest)
            a.plot(x_values, y_values, color='black')


            # Check if both 'Ibias' and 'Idiff' are defined as class attributes
            if hasattr(self, 'Ibias') and hasattr(self, 'Idiff') and len(self.Idiff)<= 3:
                    # 获取 self.Ibias 中元组的数量
                for i in range(3):
                                # Extracting the i-th element from each tuple in Ibias
                            # Check if the lengths match
                    if len(self.Ibias[i]) == len(self.Idiff[i]):
                        a.plot(self.Ibias[i], self.Idiff[i], label=f'Real Trip Curve {i+1}', linestyle='--')
                        a.legend()
                    else:
                        messagebox.WARNING(f"Error: Mismatch in data length for curve {i+1}")
                        print(f"Error: Mismatch in data length for curve {i+1}")
                    
            else:
                print("Error: self.Ibias or self.Idiff does not contain enough data.")
                messagebox.WARNING("Error: self.Ibias or self.Idiff does not contain enough data.")

                            # Collect x_values
                            #x_values = np.arange(0, float(max(Ibias_values)), 0.001)

            a.legend()
            a.set_xlabel('Ibias')
            a.set_ylabel('Idiff')

            # Embed the plot and toolbar in Tkinter window
            canvas = FigureCanvasTkAgg(f, master=self.plot_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

            toolbar = NavigationToolbar2Tk(canvas, self.plot_canvas)
            toolbar.update()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
            toolbar.pack(side='top', fill='both', expand=True)

    def plot_standardtrip(self):
        # Destroy the previous Tkinter window
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        
        print(f"self.start: {self.start}")  # Print the value of self.start
        print(f"self.stop: {self.stop}")    # Print the value of self.stop
        print(f"self.line: {self.line}") 
        # Plotting code
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)

        # Check for the existence of self.line and plot accordingly
        if self.line!=(0,0):
            # First segment: self.start to self.line
            x1=self.start[0]
            y1=self.start[1]
            x2=self.line[0]
            y2=self.line[1]
            x3=self.stop[0]
            y3=self.stop[1]
            print(f"First segment points: x1 = {x1}, x2= {x2}, x3 = {x3}")  # Print x1 and x2 for first segment
            slope1 = (y2 - y1) / (x2 - x1)
            intercept1 = y1 - slope1 * x1
            x_values1 = np.linspace(x1, x2, 500)
            y_values1 = slope1 * x_values1 + intercept1
            y_values1 = np.clip(y_values1, self.pick_up, self.Highest)
            a.plot(x_values1, y_values1, color='black')


            # Second segment: self.line to self.stop
            x3, y3 = self.stop
            slope2 = (y3 - y2) / (x3 - x2)
            intercept2 = y2 - slope2 * x2
            x_values2 = np.linspace(x2, x3+10, 1000)
            y_values2 = slope2 * x_values2 + intercept2
            y_values2 = np.clip(y_values2, self.pick_up, self.Highest)
            a.plot(x_values2, y_values2, color='black')
        else:
            # Single segment: self.start to self.stop
            x1 = self.start[0]
            y1=self.start[1]
            x2=self.stop[0]
            y2=self.stop[1]
            print(f"First segment points: x1 = {x1}, x2= {x2}")
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            x_values = np.linspace(x1, x2+10, 1000)
            y_values = slope * x_values + intercept
            y_values = np.clip(y_values, self.pick_up, self.Highest)
            a.plot(x_values, y_values, color='black')

        # Clear previous plot
        self.plot_canvas.delete("all")

        #a.legend()
        a.set_xlabel('Ibias')
        a.set_ylabel('Idiff')

        # Embed the plot and toolbar in Tkinter window
        canvas = FigureCanvasTkAgg(f, master=self.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.plot_canvas)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        toolbar.pack(side='top', fill='both', expand=True)

###load rio file
    def parse_rio_content(self, content):
        self.special_data = {}  # 确保每次都是新的字典
        data = {}
        current_section = data
        section_stack = [data]
        section_pattern = re.compile(r'^BEGIN\s+(\w+)|^END\s+(\w+)')
        special_parameters = ['IDIFF>>', 'IDIFF>', 'START', 'LINE', 'STOP','DEFBIAS','BIASDIVISOR']
        special_data = {}

        for line in content.splitlines():
            #print(f"Processing line: {line}")  # Debug print
            section_match = section_pattern.match(line)
            if section_match:
                section_start, section_end = section_match.groups()
                if section_start:
                    #print(f"Starting new section: {section_start}")  # Debug print
                    new_section = {}
                    current_section[section_start] = [new_section]
                    section_stack.append(new_section)
                    current_section = new_section
                elif section_end:
                    #print(f"Ending section: {section_end}")  # Debug print
                    section_stack.pop()
                    current_section = section_stack[-1]
            else:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    key, value = parts
                    #print(f"Adding key-value pair: {key}: {value}")  # Debug print
                    current_section[key] = value
                else:
                    # Handle lines without a tab character as standalone items
                    #print(f"Adding standalone line: {line}")  # Debug print
                    current_section.setdefault('TextLines', []).append(line)
                    parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    key, value = parts
                    if key in special_parameters:
                        special_data[key] = value
                        self.special_data[key] = value 
        print("Special Parameters Found:", special_data)
        messagebox.showinfo("Success", "All parameters are loaded.")
        self.extremes()
        return data
    def extremes(self):
        # 初始化所有值
        self.start = (0, 0)
        self.line = (0, 0)  # 显式地重置 self.line
        self.stop = (0, 0)

        try:
            if 'START' in self.special_data:
                self.start = self.parse_coordinates(self.special_data['START'])

            if 'LINE' in self.special_data:
                self.line = self.parse_coordinates(self.special_data['LINE'])

            if 'STOP' in self.special_data:
                self.stop = self.parse_coordinates(self.special_data['STOP'])

            self.Highest = float(self.special_data.get('IDIFF>>', 0))
            self.pick_up = float(self.special_data.get('IDIFF>', 0))
            self.parameters.K1 = float(self.special_data.get('BIASDIVISOR', 0))
            self.method = float(self.special_data.get('DEFBIAS', 0))

        except ValueError as e:
            print("Error in parsing data:", e)

    def parse_coordinates(self, data):
        if isinstance(data, str):
            # Process the string data (assuming it needs to be stripped and split)
            data = data.strip()
            x, y = data.split(',')  # or however the string is formatted
            return float(x), float(y)
        elif isinstance(data, (list, tuple)) and len(data) == 2:
            # If data is already a tuple, return it directly
            return data
        else:
            # Handle other cases or invalid data
            print("Invalid data format for coordinates")
            return None


    def populate_tree(self, tree, parent, data):
        for key, value in data.items():
            if isinstance(value, dict):
                node = tree.insert(parent, 'end', text=key, values=('--',))
                self.populate_tree(tree, node, value)
            elif isinstance(value, list):
                # 处理列表，可能包含嵌套字典或文本行
                for item in value:
                    if isinstance(item, dict):
                        self.populate_tree(tree, parent, item)
                    else:
                        # 处理文本行
                        tree.insert(parent, 'end', text=item, values=('--',))
            else:
                tree.insert(parent, 'end', text=key, values=(value,))

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("RIO files", "*.rio"), ("All files", "*.*")])#load RIO format
        if self.file_path:
            try:
                with open(self.file_path, 'r') as file:
                    content = file.read()
                    self.data = self.parse_rio_content(content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def show_data(self):
        if self.data:
            new_window = Toplevel(self.root)
            new_window.title("RIO File Content")
            tree = ttk.Treeview(new_window, columns=('Value',), show='tree headings')
            tree.heading('Value', text='Value')
            self.populate_tree(tree, '', self.data)
            tree.pack(expand=True, fill='both', padx=10, pady=10)
        else:
            messagebox.showinfo("Info", "Please load a RIO file first.")

###Comtrade related code，including： transfer，array modify，rename
    def on_close_window(self):
        # 清除或重置 Listbox 引用
        self.comtrade_listboxes = [None, None]
        self.loader_window.destroy()
        self.loader_window = None
    def create_loader_window(self):
         if not self.loader_window:
            self.loader_window = Toplevel()
            self.loader_window.title("COMTRADE Loader")
            self.loader_window.grid_rowconfigure(0, weight=1)
            self.loader_window.grid_columnconfigure([0, 1], weight=1)
            self.loader_window.protocol("WM_DELETE_WINDOW", self.on_close_window)

            self.comtrade_listboxes = []
            # Creating two sections
            for section in range(2):
                frame = tk.Frame(self.loader_window, borderwidth=2, relief="groove")
                frame.grid(row=0, column=section, padx=10, pady=10, sticky="nsew")
                frame.grid_rowconfigure(4, weight=1)
                frame.grid_columnconfigure(0, weight=1)

                section_label = tk.Label(frame, text=f"COMTRADE file {section + 1}")
                section_label.grid(row=0, column=0, padx=10, pady=10,sticky="ew")

                load_cfg_button = tk.Button(frame, text="Load .CFG/.COM File", command=lambda s=section: self.load_cfg(s))
                load_cfg_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

                load_dat_button = tk.Button(frame, text="Load .DAT File", command=lambda s=section: self.load_dat(s))
                load_dat_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

                listbox = Listbox(frame, height=20, width=40)
                listbox.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
                self.comtrade_listboxes.append(listbox)

    def load_cfg(self, section):
        file_path = filedialog.askopenfilename(filetypes=[("COMTRADE config files", "*.cfg *.com")])
        if file_path:
            self.cfg_file_paths[section] = file_path
            print("com load successfully")
            messagebox.showinfo("Info", f"Loaded CFG/COM file: {file_path}")
    def refresh_listbox(self, listbox, new_content):
        listbox.delete(0, 'end')
        for item in new_content:
            listbox.insert('end', item)

    def load_dat(self, section):
        dat_file_path = filedialog.askopenfilename(filetypes=[("COMTRADE data files", "*.dat")])
        if dat_file_path:
            self.dat_file_paths[section] = dat_file_path
            print("dat load successfully")
            messagebox.showinfo("Info", f"Loaded DAT file: {dat_file_path}")

            # Check if both .cfg and .dat files are loaded for the section
            if self.cfg_file_paths[section]:
                self.rec = comtrade.load(self.cfg_file_paths[section], dat_file_path)
                df = self.rec.to_dataframe()
                self.comtrade_dataframes[section] = df  # Store dataframe
                self.time = self.rec.time
                self.trigger_time=self.rec.trigger_time
                print(self.time)

                # 准备新内容用于刷新 Listbox
                new_content = [f"{column}: {df[column].head().tolist()}" for column in df.columns]

                # 获取当前 section 的 Listbox 并使用 refresh_listbox 函数刷新内容
                if self.comtrade_listboxes[section]:
                    self.refresh_listbox(self.comtrade_listboxes[section], new_content)

    def select_current(self):
        # Check if data is loaded in both sections
        if any(df is None for df in self.comtrade_dataframes):
            messagebox.showwarning("Warning", "Please load data in both sections first.")
            return

        def add_selected_columns():
            if len(listbox_1.curselection()) > self.max_selections or len(listbox_2.curselection()) > self.max_selections:
                messagebox.showwarning("Warning", "Maximum of 3 columns can be selected per section.")
                return
            
            self.data_array1 = [0] * self.max_selections
            self.data_array2 = [0] * self.max_selections

            # Assign selections from listbox 1 to data_array1
            for i, idx in enumerate(listbox_1.curselection()):
                if idx < len(self.rec.analog) and i < self.max_selections:
                    self.data_array1[i] = self.rec.analog[idx]

            # Assign selections from listbox 2 to data_array2
            for i, idx in enumerate(listbox_2.curselection()):
                if idx < len(self.rec.analog) and i < self.max_selections:
                    self.data_array2[i] = self.rec.analog[idx]

            # Perform calculations with the selected data
            self.calculate_Ibias()
            self.calculate_Idiff()
            update_output_text()

        def update_output_text():
            output_text.delete("1.0", END)
            output_text.insert(END, "Selected columns from Section 1 (Ip):\n")
            for idx in listbox_1.curselection():
                output_text.insert(END, f"{self.comtrade_dataframes[0].columns[idx]} (Index: {idx})\n")
            output_text.insert(END, "\nSelected columns from Section 2 (Is):\n")
            for idx in listbox_2.curselection():
                output_text.insert(END, f"{self.comtrade_dataframes[1].columns[idx]} (Index: {idx})\n")



        selection_window = Toplevel()
        selection_window.title("Select Columns")

        # Setup frames and listboxes for each section
        for section in range(2):
            frame = tk.Frame(selection_window, borderwidth=2, relief="groove")
            frame.grid(row=0, column=section, padx=10, pady=10, sticky="nsew")
            selection_window.grid_rowconfigure(0, weight=1)
            selection_window.grid_columnconfigure(section, weight=1)

            section_label = tk.Label(frame, text=f"Section {section + 1}")
            section_label.grid(row=0, column=0, padx=10, pady=10)

            listbox = Listbox(frame, height=20, width=40, selectmode='multiple', exportselection=False)
            listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            for column in self.comtrade_dataframes[section].columns:
                listbox.insert(tk.END, column)

            if section == 0:
                listbox_1 = listbox
            else:
                listbox_2 = listbox

        # Button to confirm selections
        select_button = tk.Button(selection_window, text="Confirm Selections", command=add_selected_columns)
        select_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Text area to display selected columns
        output_text = tk.Text(selection_window, height=15, width=80)
        output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def plot_real_trip(self):
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        # 绘制图表
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)

        if hasattr(self, 'Ibias') and hasattr(self, 'Idiff') and len(self.Idiff)<= 3:
            # 获取 self.Ibias 中元组的数量
      
            for i in range(3):
                        # Extracting the i-th element from each tuple in Ibias
                        
                        
                    # Check if the lengths match
                        if len(self.Ibias[i]) == len(self.Idiff[i]):
                            a.plot(self.Ibias[i], self.Idiff[i], label=f'Real Trip Curve {i+1}', linestyle='--')
                            a.legend()
                        else:
                            print(f"Error: Mismatch in data length for curve {i+1}")
        else:
            print("Error: self.Ibias or self.Idiff does not contain enough data.")

        # 将图表嵌入到 Tkinter 窗口中
        canvas = FigureCanvasTkAgg(f, master=self.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.plot_canvas)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        toolbar.pack(side='top', fill='both', expand=True)
###Closing App
def on_closing():
    print("Closing the application")
    sys.exit(0)
if __name__ == "__main__":
    root = tk.Tk()
    app = Difftest(root)
    root.geometry("900x600")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    
