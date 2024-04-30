import tkinter as tk
from tkinter import filedialog,ttk, messagebox, Toplevel,Entry, StringVar
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import  messagebox
import numpy as np
import comtrade
from tkinter import filedialog, Toplevel, Listbox, END
import re
import sys
from matplotlib.widgets import Slider, SliderBase
from tkinter import font as tkFont  # 用于字体定义
from datetime import datetime
import os
import matplotlib
import math
from threading import Thread, Event
import time


class Difftest:
    def __init__(self, root):
    
        self.root = root
        self.root.title("Relay Trip Comparison App")
        self.slopes = []  # Initialize slopes as an empty list
        self.bases = []   # Initialize bases as an empty list
        self.pick_up = None
        self.Highest = None
        self.df = None
        self.done_event = Event()
        #self.parameters = Parameters()  # Create an instance of the Parameters class
        #data from 1st comtrade file

        #data from 2nd comtrade file

        self.rec=[None,None]
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
        self.K2=1
        self.K1=1
        self.A=0
        self.time1=[[],[]]
        self.trigger_time1 = [None, None]
        self.frequency=[None, None]
        self.time=None
        self.Ip1=None
        self.rotation_matrices = {
        0: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        30: [[1/math.sqrt(3), 0, -1/math.sqrt(3)], [-1/math.sqrt(3), 1/math.sqrt(3), 0], [0, -1/math.sqrt(3), 1/math.sqrt(3)]],
        60: [[0, 0, -1], [-1, 0, 0], [0, -1, 0]],
        90: [[0, 1/math.sqrt(3), -1/math.sqrt(3)], [-1/math.sqrt(3), 0, 1/math.sqrt(3)], [1/math.sqrt(3), -1/math.sqrt(3), 0]],
        120: [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
        150: [[-1/math.sqrt(3), 1/math.sqrt(3), 0], [0, -1/math.sqrt(3), 1/math.sqrt(3)], [1/math.sqrt(3), 0, -1/math.sqrt(3)]],
        180: [[-1, 0, 0], [0, -1, 0], [0, 0, -1]],
        -30: [[1/math.sqrt(3), -1/math.sqrt(3), 0], [0, 1/math.sqrt(3), -1/math.sqrt(3)], [-1/math.sqrt(3), 0, 1/math.sqrt(3)]],
        -60: [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
        -90: [[0, -1/math.sqrt(3), 1/math.sqrt(3)], [1/math.sqrt(3), 0, -1/math.sqrt(3)], [-1/math.sqrt(3), 1/math.sqrt(3), 0]],
        -120: [[0, -1, 0], [0, 0, -1], [-1, 0, 0]],
        -150: [[1/math.sqrt(3), -1/math.sqrt(3), 0], [0, 1/math.sqrt(3), -1/math.sqrt(3)], [-1/math.sqrt(3), 0, 1/math.sqrt(3)]],
    }

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14)  # 调整字体大小为14
        self.root.option_add("*Font", default_font)

        # 使用Frame增加一层布局，以便更灵活地控制边距和排列
        #self.main_frame = tk.Frame(self.root)
        #self.main_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        self.app_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Determine if running as a script or frozen executable
        if getattr(sys, 'frozen', False):
            # If the application is run as a frozen executable (e.g., packaged with PyInstaller)
            self.log_directory = os.path.dirname(sys.executable)
        else:
            # If the application is run as a script
            self.log_directory = os.path.dirname(__file__)
        
        # Define the log file name
        self.log_file_name = "debug_log.txt"
        
        # Construct the full path for the log file
        self.log_file_path = os.path.join(self.log_directory, self.log_file_name)
        
        # Other attributes
        #self.create_widgets()
        self.setup_gui()
    
    def setup_gui(self):
        # 设置侧边栏Frame用于放置按钮
        self.sidebar_frame = tk.Frame(self.root)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        

        # 创建用于绘图或其他显示的Canvas
        self.plot_canvas = tk.Canvas(self.root)
        self.plot_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 设置按钮宽度和高度
        button_width = 20
        button_height = 2

        # RIO File 按钮
        self.rio_menu_button = tk.Menubutton(self.sidebar_frame, text="RIO File", relief=tk.RAISED, bg='lightgray')
        self.rio_menu_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.rio_menu = tk.Menu(self.rio_menu_button, tearoff=0)
        self.rio_menu_button.config(menu=self.rio_menu)
        self.rio_menu.add_command(label="Load RIO file", command=self.load_file)
        self.rio_menu.add_command(label="Show RIO file", command=self.show_data)

        # Load COMTRADE file 按钮
        self.load_comtrade_button = tk.Button(self.sidebar_frame, text="Load COMTRADE file", command=self.create_loader_window, width=button_width, height=button_height)
        self.load_comtrade_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Select Current 按钮
        self.select_current_button = tk.Button(self.sidebar_frame, text="Select Current", command=self.select_current_New, width=button_width, height=button_height)
        self.select_current_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Plot Trip Characteristics 按钮
        self.plot_trip_char_button = tk.Button(self.sidebar_frame, text="Plot Trip Characteristics", command=self.plot_standardtrip, width=button_width, height=button_height)
        self.plot_trip_char_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        # Plot 类型下拉选择框
        self.plot_options_var = tk.StringVar()
        self.plot_options = ttk.Combobox(self.sidebar_frame, textvariable=self.plot_options_var, state="readonly",
                                         values=["RMS Current", "Sine Wave Current", "Differential Current"], width=button_width)
        self.plot_options.set("Select Plot Type") 
        self.plot_options.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.plot_options.set("Select Plot Type")

        # Plot 按钮
        self.plot_button = tk.Button(self.sidebar_frame, text="Plot", command=self.execute_plot, width=button_width, height=button_height)
        self.plot_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

    def execute_plot(self):
        # 根据下拉菜单的选择执行对应的绘图函数
        plot_type = self.plot_options_var.get()
        if plot_type == "RMS Current":
            self.plot_current_rms()
        elif plot_type == "Sine Wave Current":
            self.plot_current()
        elif plot_type == "Differential Current":
            self.plot_realtime_datas_New()
        else:
            messagebox.showwarning("Plot Selection", "Please select a plot type.")

##Ibias and Idiff Calculation
    #对齐数据
    def align_data(self):
        # Convert time series in self.time1 to numpy arrays for efficient operations
        self.time1 = [np.array(t) for t in self.time1]
        
        # Find index of closest match for each trigger time in its respective time series
        trigger_indexes = [np.abs(t - trigger).argmin() for t, trigger in zip(self.time1, self.trigger_time1)]
        
        # Calculate the difference between the trigger time indexes
        index_diff = trigger_indexes[1] - trigger_indexes[0]
        
        # Initialize start_index for adjusting Ip and Is arrays
        start_index = 0
        
        # If the index difference is 0, then no adjustment is needed
        if index_diff == 0:
            print("Trigger times are synchronized, no adjustment needed.")
            self.log_to_file("Trigger times are synchronized, no adjustment needed.")
            # Choose either time series as self.time, since they are synchronized
            self.time = self.time1[0]
            self.trigger_time=self.trigger_time1[0]   # or self.time1[1]
        else:
            # Adjust data alignment based on the index difference
            if index_diff > 0:
                # Second time series is delayed relative to the first one
                start_index = index_diff
                self.time = self.time1[1][start_index:]  # Select the delayed time series
                self.trigger_time=self.trigger_time1[1]            
            elif index_diff < 0:
                # First time series is delayed relative to the second one
                start_index = abs(index_diff)
                self.time = self.time1[0][start_index:]  # Select the delayed time series
                self.trigger_time=self.trigger_time1[0]  
        # Determine adjusted length for synchronization
        adjusted_length = len(self.time)
        
        # Adjust the Ip and Is arrays to synchronize with the selected self.time
        # Note: Assuming self.Ip* and self.Is* arrays are aligned with self.time1[0] initially
        self.Ip1 = self.Ip1[start_index:start_index + adjusted_length]/self.ratio1
        self.Ip2 = self.Ip2[start_index:start_index + adjusted_length]/self.ratio1
        self.Ip3 = self.Ip3[start_index:start_index + adjusted_length]/self.ratio1
        self.Is1 = self.Is1[start_index:start_index + adjusted_length]/self.ratio2
        self.Is2 = self.Is2[start_index:start_index + adjusted_length]/self.ratio2
        self.Is3 = self.Is3[start_index:start_index + adjusted_length]/self.ratio2

        # Print results for verification
        print(f"Adjusted start_index for alignment: {start_index}")
        self.log_to_file(f"Adjusted start_index for alignment: {start_index}")

    def Ibias1(self):
        """Calculate Ibias using Method 1 (Siemens relay, GEC/AREVA)"""
        self.Ibias_1 = (np.abs(self.Ip1) + np.abs(self.Is1)) / self.K1
        self.Ibias_2 = (np.abs(self.Ip2) + np.abs(self.Is2)) / self.K1
        self.Ibias_3 = (np.abs(self.Ip3) + np.abs(self.Is3)) / self.K1

    def Ibias2(self):
        """Calculate Ibias using Method 2 (ABB relay series, AEG relay series)"""
        self.Ibias_1 = (self.Ip1 - self.Is1) / self.K1
        self.Ibias_2 = (self.Ip2 - self.Is2) / self.K1
        self.Ibias_3 = (self.Ip3 - self.Is3) / self.K1

    def Ibias3(self):
        """Calculate Ibias using Method 3 (GE Multilin Series)"""
        self.Ibias_1 = (np.abs(self.Ip1) + np.abs(self.Is1) * self.K2) / self.K1
        self.Ibias_2 = (np.abs(self.Ip2) + np.abs(self.Is2) * self.K2) / self.K1
        self.Ibias_3 = (np.abs(self.Ip3) + np.abs(self.Is3) * self.K2) / self.K1

    def Ibias4(self):
        """Calculate Ibias using Method 4 (ABB relay series, Siemens relay series, GE relay, ELIN relay series)"""
        self.Ibias_1 = np.maximum(np.abs(self.Ip1), np.abs(self.Is1))
        self.Ibias_2 = np.maximum(np.abs(self.Ip2), np.abs(self.Is2))
        self.Ibias_3 = np.maximum(np.abs(self.Ip3), np.abs(self.Is3))

    def Ibias5(self):
        """Calculate Ibias using Method 5 (The smaller one value)"""
        self.Ibias_1 = np.minimum(np.abs(self.Ip1), np.abs(self.Is1))
        self.Ibias_2 = np.minimum(np.abs(self.Ip2), np.abs(self.Is2))
        self.Ibias_3 = np.minimum(np.abs(self.Ip3), np.abs(self.Is3))

    def Ibias6(self):
        """Calculate Ibias using Method 6 (ABB relay series RET316, NSE differential relay)"""
        self.Ibias_1 = np.sqrt(np.abs(self.Ip1 * self.Is1 * np.cos(self.A)))
        self.Ibias_2 = np.sqrt(np.abs(self.Ip2 * self.Is2 * np.cos(self.A)))
        self.Ibias_3 = np.sqrt(np.abs(self.Ip3 * self.Is3 * np.cos(self.A)))

    def Ibias7(self):
        """Calculate Ibias using Method 7 (ZIV transformer differential relays)"""
        self.Ibias_1 = (np.abs(self.Ip1) + np.abs(self.Is1) - np.abs(self.Idiff1)) / self.K1
        self.Ibias_2 = (np.abs(self.Ip2) + np.abs(self.Is2) - np.abs(self.Idiff2)) / self.K1
        self.Ibias_3 = (np.abs(self.Ip3) + np.abs(self.Is3) - np.abs(self.Idiff3)) / self.K1
    
    def Eliminate_function(self,I1,I2,I3):

        self.I7,self.I8,self.I9=I1,I2,I3
        matrix = np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]) / 3
        # Create an array from the inputs
        I = np.array([I1, I2, I3])
        # Perform the matrix multiplication
        result = np.dot(matrix, I)
        new_I1, new_I2, new_I3 = result
        self.I10=new_I1
        print("New I: ", result)
        return new_I1, new_I2, new_I3
    
    def apply_phase_rotation(self):

        
        # Calculate the angle of rotation
        angle_difference = (self.type2 - self.type1) * 30
        print(f"Phase shift: {angle_difference} degrees")
        
        # Adjust angles greater than 180 degrees
        if angle_difference > 180:
            angle_difference -= 360
        elif angle_difference < -180:
            angle_difference += 360
        
        # Select the corresponding rotation matrix
        rotation_matrix = self.rotation_matrices[angle_difference]
        I1=self.Ip1
        I2=self.Ip2
        I3=self.Ip3
        print("I1", I1)

        print("Transfomer Type1: ",self.connection)
        print("Transfomer Type2: ",self.connection2)

        if 'D' in self.connection:#Eliminate the zero squence
            I1,I2,I3=self.Eliminate_function(I1,I2,I3)
        if 'D' in self.connection2:
            I1,I2,I3=self.Eliminate_function(I1,I2,I3)
        
        # Apply the rotation matrix to the initial values
        self.Ip1 = (rotation_matrix[0][0] * I1 +
                    rotation_matrix[0][1] * I2 +
                    rotation_matrix[0][2] * I3)
        self.Ip2 = (rotation_matrix[1][0] * I1 +
                    rotation_matrix[1][1] * I2 +
                    rotation_matrix[1][2] * I3)
        self.Ip3 = (rotation_matrix[2][0] * I1 +
                    rotation_matrix[2][1] * I2 +
                    rotation_matrix[2][2] * I3)

    # The function apply_phase_rotation will now take the self.Is1, self.Is2, and self.Is3 values,
    # calculate the rotation needed based on self.type1 and self.type2,
    # and then set the new self.Ip1, self.Ip2, and self.Ip3 values after applying the rotation.
    # This function is to be a member of a class that contains the mentioned attributes.
    # The use of self implies that the variables are attributes of the instance of the class in which this function is defined.
    def show_progress(self):
        # 创建一个窗口
        progress_window = tk.Tk()
        progress_window.title("Progress")
        
        # 在窗口中添加一个标签
        label = tk.Label(progress_window, text="Calculating... Please wait.", font=("Arial", 12))
        label.pack(pady=20)
        
        # 这个函数用于检查事件，如果事件被设置，则关闭窗口
        def check_event():
            while not self.done_event.is_set():
                time.sleep(0.1)
            progress_window.destroy()
        
        # 在新线程中运行检查事件的函数
        Thread(target=check_event, daemon=True).start()
        
        # 显示窗口
        progress_window.mainloop()
    
    def calculate_Ibias_New(self):
        try:
            print("Starting calculate_Ibias...")
            self.log_to_file("Starting calculate_Ibias...")
    
            print(f"Selected Ibias calculation method: {self.method}")
            self.log_to_file(f"Selected Ibias calculation method: {self.method}")

            
            self.apply_phase_rotation()
        
            self.Is1=self.calculate_rms_values_optimized(self.Is1)
            self.Is2=self.calculate_rms_values_optimized(self.Is2)
            self.Is3=self.calculate_rms_values_optimized(self.Is3)
            self.Ip1=self.calculate_rms_values_optimized(self.Ip1)
            self.Ip2=self.calculate_rms_values_optimized(self.Ip2)
            self.Ip3=self.calculate_rms_values_optimized(self.Ip3)
            

            
            
            
            # Call the appropriate Ibias calculation method
            if self.method == 1:
                self.Ibias1()
            elif self.method == 2:
                self.Ibias2()
            elif self.method == 3:
                self.Ibias3()
            elif self.method == 4:
                self.Ibias4()
            elif self.method == 5:
                self.Ibias5()
            elif self.method == 6:
                self.Ibias6()
            elif self.method == 7:
                self.Ibias7()

        
            self.log_to_file(f"Calculated Ibias_1: {self.Ibias1}")
            self.log_to_file(f"Calculated Ibias_2: {self.Ibias2}")
            self.log_to_file(f"Calculated Ibias_3: {self.Ibias3}")
            #self.Ibias = result_array
            print("Ibias saved successfully.")
            self.log_to_file("Ibias saved successfully.")
            messagebox.showinfo("Success", "Ibias saved successfully.")
            #return result_array
    
        except ValueError as e:
            print(f"Error converting to float: {e}")
            self.log_to_file(f"Error converting to float: {e}")
    def calculate_Idiff_New(self):
        print("Starting calculate_Idiff...")
        self.log_to_file("Starting calculate_Idiff...")
        self.Idiff1=self.Ip1-self.Is1
        self.Idiff2=self.Ip2-self.Is2
        self.Idiff3=self.Ip3-self.Is3
        self.log_to_file(f"Calculated Idiff_1: {self.Idiff1}")
        self.log_to_file(f"Calculated Idiff_2: {self.Idiff2}")
        self.log_to_file(f"Calculated Idiff_3: {self.Idiff3}")
        print("Idiff saved successfully.")
        self.log_to_file("Idiff saved successfully.")
        messagebox.showinfo("Success", "Idiff saved successfully.")
    def plot_realtime_datas_New(self):
        # Clear the previous plot
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        self.check_data_selection()
        self.fig = Figure(figsize=(6, 4))
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        trigger_time_text = f"Trigger Time: {self.trigger_time}"

        self.plot_trip_characteristic()
    

        self.lines = []  # Store line objects for updating

        # Loop over the range and dynamically access Ibias and Idiff attributes

        curves = [
            ('Ibias_1', 'Idiff1', 'Phase a current'),
            ('Ibias_2', 'Idiff2', 'Phase b current'),
            ('Ibias_3', 'Idiff3', 'Phase c current'),
        ]

        for ibias_attr, idiff_attr, label in curves:
            x = getattr(self, ibias_attr, None)
            y = getattr(self, idiff_attr, None)
            # 检查x和y数据的存在性及长度匹配
            if x is not None and y is not None and len(x) == len(y):
                line, = self.ax.plot(x, y, label=f'{label},{trigger_time_text}')
                self.lines.append(line)
            else:
                messagebox.showwarning("Warning", f"Data for '{label}' is missing or lengths do not match. Skipping this curve.")
                print(f"Warning: Data for '{label}' is missing or lengths do not match. Skipping this curve.")
                self.log_to_file(f"Warning: Data for '{label}' is missing or lengths do not match. Skipping this curve.")
        # 设置图例和标签
        self.ax.legend()
        self.ax.set_xlabel('Ibias')
        self.ax.set_ylabel('Idiff')


        time_array = self.time

        # Slider setup
        axcolor = 'lightgoldenrodyellow'
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
        self.slider = Slider(ax_slider, 'Time', time_array.min(), time_array.max(), valinit=time_array.max())

        # Update plot based on slider
        self.slider.on_changed(self.update_plot_New)

        # Embedding figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.make_legend_pickable()

    def update_plot_New(self, selected_time_index):
        mask = self.time <= self.slider.val
        self.lines[0].set_xdata(self.Ibias_1[mask])
        self.lines[0].set_ydata(self.Idiff1[mask])

        # 更新第二条曲线的数据
        self.lines[1].set_xdata(self.Ibias_2[mask])
        self.lines[1].set_ydata(self.Idiff2[mask])

        # 更新第三条曲线的数据
        self.lines[2].set_xdata(self.Ibias_3[mask])
        self.lines[2].set_ydata(self.Idiff3[mask])

        self.fig.canvas.draw_idle()  # 重新绘制图表

    def plot_trip_characteristic(self):
        
        # 检查是否存在中间点（self.line），从而确定绘制一条还是两条线段
        if self.line != (0, 0):
            # 存在中间点，绘制两条线段

            # 第一段线
            x1, y1 = self.start
            x2, y2 = self.line
            # 计算第一段线的斜率和截距
            slope1 = (y2 - y1) / (x2 - x1)
            intercept1 = y1 - slope1 * x1
            # 生成x值，并计算对应的y值
            x_values1 = np.linspace(x1, x2, 500)
            y_values1 = slope1 * x_values1 + intercept1
            # 使用np.clip确保y值不超过预设的上下限
            y_values1 = np.clip(y_values1, self.pick_up, self.Highest)
            self.ax.plot(x_values1, y_values1, color='black', label='Trip Characteristic - 1st Segment')

            # 第二段线
            x3, y3 = self.stop
            # 计算第二段线的斜率和截距
            slope2 = (y3 - y2) / (x3 - x2)
            intercept2 = y2 - slope2 * x2
            # 生成x值，并计算对应的y值
            x_values2 = np.linspace(x2, x3, 500)
            y_values2 = slope2 * x_values2 + intercept2
            # 使用np.clip确保y值不超过预设的上下限
            y_values2 = np.clip(y_values2, self.pick_up, self.Highest)
            self.ax.plot(x_values2, y_values2, color='black', label='Trip Characteristic - 2nd Segment')

        else:
            # 没有中间点，绘制单条直线
            x1, y1 = self.start
            x2, y2 = self.stop
            # 计算直线的斜率和截距
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            # 生成x值，并计算对应的y值
            x_values = np.linspace(x1, x2, 500)
            y_values = slope * x_values + intercept
            # 使用np.clip确保y值不超过预设的上下限
            y_values = np.clip(y_values, self.pick_up, self.Highest)
            self.ax.plot(x_values, y_values, color='black', label='Trip Characteristic')

        # 在这里，self.ax 是一个matplotlib的Axes实例，用于绘图
        # self.start, self.line, self.stop 是定义曲线形状的关键点
    
    def plot_phase_1_current(self):
        
        # Clear the previous plot
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        
        self.check_data_selection()
        # 重新创建图表和轴
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        
        # 绘制断路特性曲线
        self.lines = []  # Store line objects for updating
        self.plot_trip_characteristic()
        x_1 = getattr(self, 'Ibias_1')
        y_1 = getattr(self, 'Idiff1')
        trigger_time_text = f"Trigger Time: {self.trigger_time}"
        line1, = self.ax.plot(x_1, y_1, label=f'Phase 1 current,{trigger_time_text}')
        self.lines.append(line1)
        # 绘制第一条曲线的代码
         # Setup the legend, labels
        self.ax.legend()
        self.ax.set_xlabel('Ibias')
        self.ax.set_ylabel('Idiff')

        time_array = self.time

        # Slider setup
        axcolor = 'lightgoldenrodyellow'
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
        self.slider = Slider(ax_slider, 'Time', time_array.min(), time_array.max(), valinit=time_array.max())

        # Update plot based on slider
        self.slider.on_changed(lambda val:self.update_plot_phase(self.Ibias_1,self.Idiff1))

        # Embedding figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_plot_phase(self,a,b):
        
        # 根据滑动条的当前值更新掩码
        mask = self.time <= self.slider.val

        # 只更新第一条曲线的数据
        self.lines[0].set_xdata(a[mask])
        self.lines[0].set_ydata(b[mask])

        # 重新绘制图表
        self.fig.canvas.draw_idle()

    def plot_phase_2_current(self):
        # 清除之前的图表组件
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        self.check_data_selection()
        # 重新创建图表和轴
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        
        # 绘制断路特性曲线
        self.plot_trip_characteristic()
        self.lines = []  # Store line objects for updating
        # 获取数据
        x_2 = getattr(self, 'Ibias_2')
        y_2 = getattr(self, 'Idiff2')
        trigger_time_text = f"Trigger Time: {self.trigger_time}"
   

        # 清除当前轴的内容并绘制新图表
        line2, = self.ax.plot(x_2, y_2, label=f'Phase 2 current, {trigger_time_text}')
        self.lines.append(line2)

        # 设置图例和标签
        self.ax.legend()
        self.ax.set_xlabel('Ibias')
        self.ax.set_ylabel('Idiff')

        # 配置时间滑动条
        time_array =self.time
        axcolor = 'lightgoldenrodyellow'
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
        self.slider = Slider(ax_slider, 'Time', time_array.min(), time_array.max(), valinit=time_array.max())

        # 根据滑动条更新图表
        
        self.slider.on_changed(lambda val:self.update_plot_phase(self.Ibias_2,self.Idiff2))

        # 将matplotlib图表嵌入到Tkinter界面
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def plot_phase_3_current(self):
        # Clear the previous plot
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()
        
        self.check_data_selection()
        # 重新创建图表和轴
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        
        # 绘制断路特性曲线
        self.plot_trip_characteristic()
        self.lines = []  # Store line objects for updating

        x_3 = getattr(self, 'Ibias_3')
        y_3 = getattr(self, 'Idiff3')
        trigger_time_text = f"Trigger Time: {self.trigger_time}"
        line3, = self.ax.plot(x_3, y_3, label=f'Phase 3 current,{trigger_time_text}')
        self.lines.append(line3)
        # 绘制第三条曲线的代码
         # Setup the legend, labels
        self.ax.legend()
        self.ax.set_xlabel('Ibias')
        self.ax.set_ylabel('Idiff')

        time_array =self.time

        # Slider setup
        axcolor = 'lightgoldenrodyellow'
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
        self.slider = Slider(ax_slider, 'Time', time_array.min(), time_array.max(), valinit=time_array.max())

        # Update plot based on slider
        self.slider.on_changed(lambda val:self.update_plot_phase(self.Ibias_3,self.Idiff3))

        # Embedding figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
   
    def plot_current_rms(self):
        # 清除之前的绘图
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        self.check_data_selection()
        # 重新创建图表和轴
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        trigger_time_text = f"Trigger Time: {self.trigger_time}"  # 使用有效的触发时间

        self.lines = []  # 用于存储线对象以便更新

        # 定义曲线数据和标签
        curves = [
            ('Ip1', 'Ip1'),
            ('Is1', 'Is1'),
            ('Ip2', 'Ip2'),
            ('Is2', 'Is2'),
            ('Ip3', 'Ip3'),
            ('Is3', 'Is3'),
            #('I1','I7'),
            #('I10','I10'),
        ]

        # 尝试获取时间数据
        x = getattr(self, 'time', None)
        if x is None:
            print("Error: 'time' data is missing.")
            self.log_to_file("Error: 'time' data is missing.")
            return  # 如果没有时间数据，直接返回，不进行绘图

        for attr, label in curves:
            y = getattr(self, attr, None)
            # 检查y数据的存在性，以及x和y长度是否匹配
            if y is not None and len(x) == len(y):
                line, = self.ax.plot(x, y, label=f'{label},{trigger_time_text}')
                self.lines.append(line)
            else:
                print(f"Warning: Data for '{label}' is missing or lengths do not match. Skipping this curve.")
                self.log_to_file(f"Warning: Data for '{label}' is missing or lengths do not match. Skipping this curve.")
        self.ax.legend()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('RMS current')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.make_legend_pickable()

    def plot_current(self):
    # 清除之前的绘图
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        self.check_data_selection()
        # 重新创建图表和轴
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)
        trigger_time_text = "Trigger Time: Placeholder"  # 使用有效的触发时间

        self.lines = []  # 用于存储线对象以便更新

        # 循环变量和相关标签
        variables = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6']#'I7','I8','I9','I10','I11','I12']
        labels = ['Ip1', 'Ip2', 'Ip3', 'Is1', 'Is2', 'Is3']#'I1p','I2p','I3p','new_I1p','new_I2p','new_I3p']

        # 尝试获取时间数据，此处我们需要两组时间数据
        x_primary = getattr(self.rec[0], 'time', None) if hasattr(self, 'rec') and len(self.rec) > 0 else None
        x_secondary = getattr(self.rec[1], 'time', None) if hasattr(self, 'rec') and len(self.rec) > 1 else None

        for var, label in zip(variables, labels):
            y = getattr(self, var, None)
            # 根据标签选择时间序列
            x = x_primary if 'p' in label else x_secondary
            
            # 检查y数据的存在性，以及x和y长度是否匹配
            if y is not None and x is not None and len(x) == len(y):
                line, = self.ax.plot(x, y, label=f'{label},{trigger_time_text}')
                self.lines.append(line)
            else:
                missing_data_msg = f"Warning: Data for '{label}' is missing or lengths do not match. Skipping this curve."
                print(missing_data_msg)
                self.log_to_file(missing_data_msg)
        self.ax.legend()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Sine Wave current')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.make_legend_pickable()

    def make_legend_pickable(self):
        # 将点击事件绑定到图例
        legend = self.ax.legend(loc='upper right', fancybox=True, shadow=True)
        lines = self.ax.get_lines()
        legline_map = {legline: origline for legline, origline in zip(legend.get_lines(), lines)}

        def on_pick(event):
            # 处理点击图例事件
            legline = event.artist
            origline = legline_map[legline]
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # 设置透明度以给出用户反馈
            legline.set_alpha(1.0 if vis else 0.2)
            self.canvas.draw()

        self.fig.canvas.mpl_connect('pick_event', on_pick)
        for legline in legend.get_lines():
            legline.set_picker(5)  # 5 pts容差


    ######## other function
   
    def check_data_selection(self):
        # Check if self.data is missing
        if not self.data:
            messagebox.showwarning("Data Missing", "Please upload a RIO file.")
            self.log_to_file("Data Missing: Please upload a RIO file.")
            return

        # Assuming self.rec, self.time, self.time1 could be NumPy arrays or None
        # We first check if they are not None and then if they have any content by using .any()
        t=np.array(self.trigger_time1)
        if not all(x is not None and x.any() for x in [t]):
            messagebox.showwarning("Data Missing", "Please upload a COMTRADE file.")
            self.log_to_file("Data Missing: Please upload a COMTRADE file.")
            return

        # Assuming self.Ibias1, self.Ibias2, self.Ibias3, self.Idiff1, self.Idiff2, self.Idiff3 could be arrays
        # Adjust the check similarly
        if not all(x is not None and x.any() for x in [self.Ip1]):
            messagebox.showwarning("Data Missing", "Please reselect 3-phase current data.")
            self.log_to_file("Data Missing: Please reselect 3-phase current data.")
            return

        # If all checks pass, proceed with the operation
        #messagebox.showinfo("Data Check", "All required data is selected.")
        self.log_to_file("Data Check: All required data is selected.")
    
    def log_to_file(self, message):
            # Format the current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Format the log message to include the app start time and current timestamp
            formatted_message = f"[App Start: {self.app_start_time}] [{current_time}] {message}"
            with open(self.log_file_path, 'a') as log_file:
                print(formatted_message, file=log_file)  # Write the formatted message to the log file

    def calculate_rms_values(self,data_list):
        def calculate_rms(values):
            squared_values = np.square(values)
            mean_of_squares = np.mean(squared_values)
            rms_value = np.sqrt(mean_of_squares)
            return rms_value

        return np.array([calculate_rms(data_list[:i+1]) for i in range(len(data_list))])
    
    def calculate_rms_values_optimized(self, data_list):
        squared_sum = 0
        rms_values = []
        for i, value in enumerate(data_list):
            squared_sum += value**2
            rms_value = np.sqrt(squared_sum / (i + 1))
            rms_values.append(rms_value)
        return np.array(rms_values)
    
    def find_peaks_manual(self, signal):
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i-1] < signal[i] > signal[i+1]:
                peaks.append(i)
        return np.array(peaks)

    def calculate_rms_based_on_time(self, signal, total_time, fre):
        """
        Calculate the RMS value of each period in a sine wave signal based on total time and period duration,
        then create an array of RMS values repeated over each period.

        Args:
        signal (np.ndarray): The signal array representing the combined sine waves.
        total_time (float): The total time duration of the signal in seconds.
        fre:frequency

        Returns:
        np.ndarray: An array containing the RMS values repeated for each sample in its period.
        """
        # Calculate the number of samples per period
        total_samples = len(signal)
        print("Number of samples: ", total_samples)
        samples_per_period = int(total_samples /(fre*total_time))
        print("Samples per period: ", samples_per_period)
        # Calculate number of complete periods in the signal
        num_periods = len(signal) // samples_per_period
        print("Number of periods: ", num_periods)
        
        # Prepare an array to store RMS values
        rms_values = np.zeros(len(signal))
        
        # Iterate over each period
        for i in range(num_periods):
            # Extract the period
            start_index = i * samples_per_period
            end_index = start_index + samples_per_period
            period = signal[start_index:end_index]
            print("Period", period)
            
            # Find peaks in the period using the manual method
            peak_indices = self.find_peaks_manual(period)
            print("Peak",peak_indices)
            if len(peak_indices) > 0:
                max_peak_value = period[peak_indices].max()
                # Calculate the RMS value, peak divided by sqrt(2)
                rms_value = max_peak_value / np.sqrt(2)
                # Repeat this RMS value for the entire period in the output array
                rms_values[start_index:end_index] = rms_value
        
        return rms_values

    # This function call is commented out to prevent execution here
    # Example usage:
    # total_time = 10  # seconds, total duration of the signal
    # period_duration = 0.5  # seconds, duration of one period
    # full_rms_values = calculate_rms_based_on_time(your_signal_array, total_time, period_duration)
    # print(full_rms_values)

    
    def plot_standardtrip(self):
        # Destroy the previous Tkinter window
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        
        print(f"self.start: {self.start}")  # Print the value of self.start
        print(f"self.stop: {self.stop}")    # Print the value of self.stop
        print(f"self.line: {self.line}") 
        self.log_to_file(f"self.start: {self.start}, self.stop: {self.stop}, self.line: {self.line}")
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
            self.log_to_file(f"First segment points: x1 = {x1}, x2= {x2}, x3 = {x3}, y1={y1}, y2={y2}, y3={y3}")
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
            self.log_to_file(f"First segment points: x1 = {x1}, x2= {x2}, y1={y1}, y2={y2}")
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
        """
        Parses the content of a RIO file. Each line is parsed to identify the name and corresponding parameters.
        """
        self.data=[]  # Reset data storage
        self.special_data = {}  # Reset special data storage
        name_count = {}  # Dictionary to keep track of the number of times each name has appeared

        # Define the list of special parameters you're interested in
        #special_parameters = ['IDIFF>>', 'IDIFF>', 'START3', 'LINE', 'STOP3', 'DEFBIAS', 'BIASDIVISOR']

        for line in content.splitlines():
            line = line.strip()
            # Attempt to split each line into a name and parameters part
            parts = re.split(r'\s+', line, maxsplit=1)
            original_name = parts[0]
            parameters = parts[1] if len(parts) > 1 else ""

            if original_name in name_count:
                name_count[original_name] += 1
                name = f"{original_name}{name_count[original_name]}"
            else:
                name_count[original_name] = 1
                name = original_name

            # Add the parsed line to the data storage
            self.data.append((name, parameters))

            # Check and store special parameters
          
            self.special_data[name] = parameters

        # Optionally, log or display the special parameters found
        print("Special Parameters Found:", self.special_data)
        self.log_to_file(f"Special Parameters Found: {self.special_data}")
        self.extremes()

    def extremes(self):
        # 初始化所有值
        self.start = (0, 0)
        self.line = (0, 0)  # 显式地重置 self.line
        self.stop = (0, 0)

        try:
            if 'START3' in self.special_data:
                # 假设START的格式是"数字,数字"，我们需要将其转换为元组(float, float)
                start_str = self.special_data['START3']
                self.start = tuple(map(float, start_str.split(',')))

            if 'LINE' in self.special_data:
                # 同上，处理LINE参数
                line_str = self.special_data['LINE']
                self.line = tuple(map(float, line_str.split(',')))

            if 'STOP3' in self.special_data:
                # 同上，处理STOP参数
                stop_str = self.special_data['STOP3']
                self.stop = tuple(map(float, stop_str.split(',')))

            # 其他参数不需要分割，直接转换类型
            self.Highest = float(self.special_data.get('IDIFF>>', 0))
            self.pick_up = float(self.special_data.get('IDIFF>', 0))
            self.K1 = float(self.special_data.get('BIASDIVISOR', 1))  # Assuming a default value of 1 if not present
            self.method = float(self.special_data.get('DEFBIAS', 0))
            self.ratio1 = float(self.special_data.get('NOM-PD-PH', 1)) / float(self.special_data.get('NOM-CT-PH', 1))*float(self.special_data.get('SN', 1)) /(math.sqrt(3)*float(self.special_data.get('VN', 1)))  # Assuming a default value of 1 if not present
            self.ratio2 = float(self.special_data.get('NOM-PD-PH2', 1)) / float(self.special_data.get('NOM-CT-PH2', 1))*float(self.special_data.get('SN2', 1)) /(math.sqrt(3)*float(self.special_data.get('VN2', 1)))  # Assuming a default value of 1 if not present
            self.type1=float(self.special_data.get('CONNECTIONNUMBER', 0))
            self.type2=float(self.special_data.get('CONNECTIONNUMBER2', 0))
            self.connection = self.special_data.get('CONNECTION', '')##delta or Y connection
            self.connection2 = self.special_data.get('CONNECTION2', '')
            #print("显示数据：", self.special_data['NOM-CT-PH'])
        except ValueError as e:
            print("Error in parsing data:", e)
            # 确保这个方法存在，或者根据实际情况进行调整
            self.log_to_file(f"Error in parsing data: {e}")
    def load_file(self):
        """
        Opens a dialog to select a RIO file, then parses and stores its content.
        """
        file_path = filedialog.askopenfilename(filetypes=[("RIO files", "*.rio"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                self.parse_rio_content(content)
                messagebox.showinfo("Success", "File successfully loaded and parsed.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def show_data(self):
        """
        Displays the parsed data in a new window using a Treeview widget for two-column display
        and allows direct editing of parameters, with the changes saved back into the original data.
        """
        if self.data:
            new_window = Toplevel(self.root)
            new_window.title("RIO File Content")

            tree = ttk.Treeview(new_window, columns=("Name", "Parameters"), show="headings")
            tree.heading("Name", text="Name")
            tree.heading("Parameters", text="Parameters")

            for idx, (name, parameters) in enumerate(self.data):
                tree.insert("", "end", iid=str(idx), values=(name, parameters))

            def on_double_click(event):
                for widget in new_window.winfo_children():
                    if isinstance(widget, Entry):
                        widget.destroy()

                item_id = tree.identify_row(event.y)
                column = tree.identify_column(event.x)

                if tree.heading(column, "text") == "Parameters":
                    x, y, width, height = tree.bbox(item_id, column)
                    value = tree.set(item_id, column)
                    entry_var = StringVar(new_window, value=value)

                    entry = Entry(new_window, textvariable=entry_var, bd=0)
                    entry.place(x=x, y=y, width=width, height=height)

                    def save_edit(event):
                        new_value = entry_var.get()
                        tree.set(item_id, column, new_value)

                        # Update self.data with the new value
                        idx = int(item_id)  # Convert the item_id back to an index
                        self.data[idx] = (self.data[idx][0], new_value)  # Update the tuple for the edited item

                        entry.destroy()

                    entry.bind("<Return>", save_edit)
                    entry.bind("<FocusOut>", save_edit)
                    entry.focus()

            tree.bind("<Double-1>", on_double_click)

            tree.pack(expand=True, fill='both', padx=10, pady=10)
        else:
            messagebox.showinfo("Info", "Please load a RIO file first.")
###Comtrade related code，including： transfer，array modify，rename
    def create_loader_window(self):
        self.comtrade_listboxes = [None, None]
        section_titles = ["Primary COMTRADE file", "Secondary COMTRADE file"]
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        # 创建两个部分用于加载COMTRADE文件
        for section in range(2):
            section_frame = tk.LabelFrame(self.plot_canvas, text=section_titles[section])
            section_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            load_cfg_button = tk.Button(section_frame, text="Load .CFG/.COM File", command=lambda s=section: self.load_cfg(s))
            load_cfg_button.pack(fill=tk.X, padx=5, pady=5)

            load_dat_button = tk.Button(section_frame, text="Load .DAT File", command=lambda s=section: self.load_dat(s))
            load_dat_button.pack(fill=tk.X, padx=5, pady=5)

            listbox = Listbox(section_frame, height=5)
            listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.comtrade_listboxes[section] = listbox



#####
    def load_cfg(self, section):
        file_path = filedialog.askopenfilename(filetypes=[("COMTRADE config files", "*.cfg *.com")])
        if file_path:
            self.cfg_file_paths[section] = file_path
            print("COM load successfully: ",section)
            self.log_to_file("COM load successfully")
            messagebox.showinfo("Info", f"Loaded CFG/COM file: Successfully")
    def refresh_listbox(self, listbox, new_content):
        listbox.delete(0, 'end')
        for item in new_content:
            listbox.insert('end', item)

    def load_dat(self, section):
        dat_file_path = filedialog.askopenfilename(filetypes=[("COMTRADE data files", "*.dat")])
        if dat_file_path:
            self.dat_file_paths[section] = dat_file_path
            print(".DAT load successfully")
            self.log_to_file(f".DAT load successfully: {section}")
            messagebox.showinfo("Info", f"Loaded DAT file: Successfully")

            # Check if both .cfg and .dat files are loaded for the section
            if self.cfg_file_paths[section]:
                self.rec[section] = comtrade.load(self.cfg_file_paths[section], dat_file_path)
                #self.time=np.array(self.rec.time)
                self.time1[section]=self.rec[section].time
                self.log_to_file(f"Time: {self.time}")
                self.trigger_time1[section]=self.rec[section].trigger_time
                print("Real Trigger Time:",self.trigger_time1[section],"Section: ",section)
                self.log_to_file(f"Real Trigger Time: {self.trigger_time1[section]},Section: {section}")
                df = self.rec[section].to_dataframe()
                self.frequency[section]=self.rec[section].frequency
                print("Frequency:",self.frequency[section],"Section: ",section)
                self.comtrade_dataframes[section] = df  # Store dataframe
                #print(self.time)

                # 准备新内容用于刷新 Listbox
                new_content = [f"{column}" for column in df.columns]

                # 获取当前 section 的 Listbox 并使用 refresh_listbox 函数刷新内容
                if self.comtrade_listboxes[section]:
                    self.refresh_listbox(self.comtrade_listboxes[section], new_content)


    def show_progress(event):
        # 创建一个窗口
        progress_window = tk.Tk()
        progress_window.title("Progress")
        
        # 在窗口中添加一个标签
        label = tk.Label(progress_window, text="Calculating... Please wait.", font=("Arial", 12))
        label.pack(pady=20)
        
        # 这个函数用于检查事件，如果事件被设置，则关闭窗口
        def check_event():
            while not event.is_set():
                time.sleep(0.1)
            progress_window.destroy()
        
        # 在新线程中运行检查事件的函数
        Thread(target=check_event, daemon=True).start()
        
        # 显示窗口
        progress_window.mainloop()

    def select_current_New(self):
        # Check if data is loaded in both sections
        if any(df is None for df in self.comtrade_dataframes):
            messagebox.showwarning("Warning", "Please load data in both sections first.")
            return
        


        def add_selected_columns():
            self.Ip1, self.Ip2, self.Ip3 = [], [], []
            self.Is1, self.Is2, self.Is3 = [], [], []
            self.I1, self.I2, self.I3 =[], [], []
            self.I4, self.I5, self.I6=[], [], []

            rec1=self.rec[0]
            rec2=self.rec[1]

            # 从 listbox_1 分配选择到 Ip1, Ip2, Ip3
            for i, idx in enumerate(listbox_1.curselection()):
                if idx < len(rec1.analog):
                
                    
                    if i == 0:
                        self.Ip1= np.array(rec1.analog[idx])
                        self.log_to_file(f"Calculated Ip1 at rec: {self.Ip1}")
                        self.I1=self.Ip1
                    elif i == 1:
                        self.Ip2=np.array(rec1.analog[idx])
                        self.log_to_file(f"Calculated Ip2 at rec: {self.Ip2}")
                        self.I2=self.Ip2
                    elif i == 2:
                        self.Ip3=np.array(rec1.analog[idx])
                        self.log_to_file(f"Calculated Ip3 at rec: {self.Ip3}")
                        self.I3=self.Ip3
                else:
                    print(f"Selection {idx} from listbox 1 is out of range.")
                    self.log_to_file(f"Selection {idx} from listbox 1 is out of range.")

            # 从 listbox_2 分配选择到 Is1, Is2, Is3
            for i, idx in enumerate(listbox_2.curselection()):
                if idx < len(rec2.analog):
                    
                    #self.trigger_time2=rec2.trigger_time
                    if i == 0:
                        self.Is1=np.array(rec2.analog[idx])
                        self.log_to_file(f"Is1: {self.Is1}")
                        self.I4=self.Is1
                    elif i == 1:
                        self.Is2=np.array(rec2.analog[idx])
                        self.log_to_file(f"Is2: {self.Is2}")
                        self.I5=self.Is2
                    elif i == 2:
                        self.Is3=np.array(rec2.analog[idx])
                        self.I6=self.Is3
                else:
                    print(f"Selection {idx} from listbox 2 is out of range.")
                    self.log_to_file(f"Selection {idx} from listbox 2 is out of range.")


            # 使用选中的数据执行计算
            self.align_data()
            self.calculate_Ibias_New()
            self.calculate_Idiff_New()
            update_output_text()
            self.root.focus()
            selection_window.destroy()

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
    