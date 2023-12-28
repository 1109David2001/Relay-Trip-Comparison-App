import math
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import simpledialog, messagebox
import numpy as np
'''
1.增加读取CSV 数据，comtrade 和 可能增加csv 直接换算(finish)





2.增加磁饱和区域
3.电流全部是三相
4.CT 饱和/cta 分析
5.逆向工程，逆向做comtrade

'''

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
        self.x_max = None
        self.y_max = None
        self.df = None
        self.parameters = Parameters()  # Create an instance of the Parameters class
        self.data_arrays = {}
        # Other attributes
        self.create_widgets()

    def create_widgets(self):
        # Create canvas for plotting
        self.plot_canvas = tk.Canvas(self.root)
        self.plot_canvas.pack(side='left', fill='x', expand=True)

        # File input button for trip_action_curve CSV
        '''self.btn_load_csv = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.btn_load_csv.pack(side='right', expand=True, fill='y', pady=5)'''

        # Plot Standard trip and Real trip button
        self.btn_plot_curve = tk.Button(self.root, text="Plot Standard Trip and Real trip", command=self.plot_datas)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)

        # Plot Standard trip
        self.btn_plot_curve = tk.Button(self.root, text="Plot Standard Trip", command=self.plot_standardtrip)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)

        # New button to show and modify parameters
        self.btn_show_parameters = tk.Button(self.root, text="Show/Modify Parameters", command=self.show_modify_parameters)
        self.btn_show_parameters.pack(side='top', expand=True, fill='x', pady=5)

        # Dropdown menu for Ibias calculation method
        self.ibias_method_var = tk.StringVar()
        self.ibias_method_var.set("Method 1")  # Default method
        ibias_method_options = ["Method 1", "Method 2", "Method 3", "Method 4", "Method 5", "Method 6", "Method 7"]
        ibias_method_menu = tk.OptionMenu(self.root, self.ibias_method_var, *ibias_method_options)
        ibias_method_menu.pack(side='top', expand=True, fill='x', pady=5)
        # Load Comtrade file 
        self.btn_plot_curve = tk.Button(self.root, text="Load COMTRADE file(.dat)", command=self.choose_file)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
        #Show COMTRADE file 
        self.btn_plot_curve = tk.Button(self.root, text="Select/Rename COMTRADE data", command=self.show_arrays)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
        #Plot Real Trip curve
        self.btn_plot_curve = tk.Button(self.root, text="Plot real trip curve", command=self.plot_real_trip)
        self.btn_plot_curve.pack(side='top', expand=True, fill='x', pady=5)
    
    def calculate_Ibias(self, array1, array2):
        # Retrieve the data from the selected arrays
        Ip_values = [float(value) for value in self.data_arrays[array1]]
        Is_values = [float(value) for value in self.data_arrays[array2]]

        # Create an instance of the Ibiascal class
        ibias_calculator = Ibiascal()

        # Set Ip and Is values
        ibias_calculator.Ip = Ip_values
        ibias_calculator.Is = Is_values

        # Determine the selected Ibias calculation method
        selected_method = self.ibias_method_var.get()

        # Call the appropriate Ibias calculation method
        if selected_method == "Method 1":
            ibias_calculator.Ibias1()
        elif selected_method == "Method 2":
            ibias_calculator.Ibias2()
        elif selected_method == "Method 3":
            ibias_calculator.Ibias3()
        elif selected_method == "Method 4":
            ibias_calculator.Ibias4()
        elif selected_method == "Method 5":
            ibias_calculator.Ibias5()
        elif selected_method == "Method 6":
            ibias_calculator.Ibias6()
        elif selected_method == "Method 7":
            ibias_calculator.Ibias7()

        # Access the calculated Ibias values
        Ibias_values = ibias_calculator.Ibias

        # Create a new array containing the calculated Ibias values
        result_array = list(zip(Ibias_values))

        # Print or use the calculated Ibias_values as needed
        print("Ibias saved successfully.")
        self.Ibias = result_array
        messagebox.showinfo("Success", "Ibias saved successfully.")
        # Return the result_array
        return result_array


    def calculate_Idiff(self,array1,array2):
        # Assuming x_values represent Ibias
        # Calculate Idiff (Ip - Is) for each Ibias
        Idiff_values = [float(ip) - float(is_value) for ip, is_value in zip(self.data_arrays[array1], self.data_arrays[array2])]
        self.Idiff = Idiff_values
        messagebox.showinfo("Success", "Idiff saved successfully.")
        self.modify_arrays_window.destroy()
        return Idiff_values   

    def plot_datas(self):
        # Destroy the previous Tkinter window
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        # Initial plot of X and Y axes
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)
        slopes = self.slopes
        intercepts = self.bases
        min_value = self.pick_up
        max_value = self.Highest
        # Plot standard trip curve
        if self.x_max is None:
            messagebox.showerror("Error", "Invalid X-Max value")
        else:
            try:
                x_values = np.arange(0, float(self.x_max), 0.001)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid X-Max value: {e}")
                return

            y_values = np.maximum.reduce([slopes * x_values - intercepts for slopes, intercepts in zip(slopes, intercepts)])
            y_values = np.clip(y_values, min_value, max_value)

            a.plot(x_values, y_values, label='Standard Trip Curve')


            # Check if both 'Ibias' and 'Idiff' are defined as class attributes
            if hasattr(self, 'Ibias') and hasattr(self, 'Idiff'):
                Ibias_values = self.Ibias
                Idiff_values = self.Idiff

                a.plot(Ibias_values, Idiff_values, label='Real Trip Curve', linestyle='--')

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
        

        # Standard trip of X and Y axes
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)
        slopes = self.slopes
        intercepts = self.bases
        min_value = self.pick_up
        max_value = self.Highest
        if self.x_max is None:
            messagebox.showerror("Error", "Invalid X-Max value: ")
        else:
            try:
                x_values = np.arange(0, float(self.x_max), 0.001)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid X-Max value: {e}")
                return

            y_values = np.maximum.reduce([slopes * x_values - intercepts for slopes, intercepts in zip(slopes, intercepts)])
            y_values = np.clip(y_values, min_value, max_value)

            # Clear previous plot
            self.plot_canvas.delete("all")

            a.plot(x_values, y_values, color='black')#plot the standard trip curve
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
    
    def show_modify_parameters(self):
        # Create a new window to show and modify parameters
        self.parameters_window = tk.Toplevel(self.root)
        parameters_window=self.parameters_window
        parameters_window.title("Modify Parameters")

        # X-Y max parameters
        tk.Label(parameters_window, text="X-Max:").grid(row=0, column=0)
        tk.Label(parameters_window, text="Y-Max:").grid(row=1, column=0)
        entry_x_max = tk.Entry(parameters_window)
        entry_y_max = tk.Entry(parameters_window)
        entry_x_max.insert(0, str(self.x_max))
        entry_y_max.insert(0, str(self.y_max))
        entry_x_max.grid(row=0, column=1)
        entry_y_max.grid(row=1, column=1)
        # Input fields for K1 and K2
        tk.Label(parameters_window, text="K1:").grid(row=8, column=0)
        entry_k1 = tk.Entry(parameters_window)
        entry_k1.grid(row=8, column=1)

        tk.Label(parameters_window, text="K2:").grid(row=9, column=0)
        entry_k2 = tk.Entry(parameters_window)
        entry_k2.grid(row=9, column=1)
        entry_k1.insert(0, str(self.parameters.K1).strip("[]"))
        entry_k2.insert(0, str(self.parameters.K2).strip("[]"))

        # Input parameters
        tk.Label(parameters_window, text="Input Parameters:").grid(row=2, column=0)
        tk.Label(parameters_window, text="Slopes:").grid(row=3, column=0)
        tk.Label(parameters_window, text="Bases:").grid(row=4, column=0)
        tk.Label(parameters_window, text="Pick-up:").grid(row=5, column=0)
        tk.Label(parameters_window, text="Highest:").grid(row=6, column=0)
        #input parameters
        entry_slopes = tk.Entry(parameters_window)
        entry_bases = tk.Entry(parameters_window)
        entry_pick_up = tk.Entry(parameters_window)
        entry_highest = tk.Entry(parameters_window)
        # Display the parameters without square brackets
        entry_slopes.insert(0, ', '.join(map(str, self.slopes)))
        entry_bases.insert(0, ', '.join(map(str, self.bases)))
        entry_pick_up.insert(0, str(self.pick_up).strip("[]"))
        entry_highest.insert(0, str(self.Highest).strip("[]"))
        #entry location
        entry_slopes.grid(row=3, column=1)
        entry_bases.grid(row=4, column=1)
        entry_pick_up.grid(row=5, column=1)
        entry_highest.grid(row=6, column=1)

        # Save button
        save_button = tk.Button(parameters_window, text="Save", command=lambda: self.save_parameters(
            entry_x_max.get(), entry_y_max.get(), entry_slopes.get(), entry_bases.get(),
            entry_pick_up.get(), entry_highest.get(), entry_k1.get(), entry_k2.get()))
        save_button.grid(row=10, column=0, columnspan=2, pady=10)
  
    def save_parameters(self, x_max, y_max, slopes, bases, pick_up, highest, K1, K2):
        try:
            # Save the modified parameters
            self.x_max = float(x_max)
            self.y_max = float(y_max)

                # Replace double-byte commas with standard ASCII commas
            input_slopes = slopes.replace('，', ',')
            input_bases = bases.replace('，', ',')
            input_pick_up = pick_up.replace('，', ',')
            input_highest = highest.replace('，', ',')

            # Convert entries to arrays of floats
            self.slopes = np.array([float(x.strip()) for x in input_slopes.split(',')])
            self.bases = np.array([float(x.strip()) for x in input_bases.split(',')])
            self.pick_up = np.array([float(x.strip()) for x in input_pick_up.split(',')])
            self.Highest = np.array([float(x.strip()) for x in input_highest.split(',')])
            # Save the modified parameters
            self.x_max = float(x_max)
            self.y_max = float(y_max)
            
            # Set K1 and K2 in the Parameters class
            self.parameters.K1 = float(K1) if K1 else 1.0
            self.parameters.K2 = float(K2) if K2 else 1.0
            # Check if the conversion is successful
            print("Slopes:", self.slopes)
            print("Bases:", self.bases)
            print("Pick-up:", self.pick_up)
            print("Highest:", self.Highest)
            # Show a success message
            messagebox.showinfo("Success", "Parameters saved successfully.")
            self.parameters_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numerical values.Please input again")
###Comtrade related code，including： transfer，array modify，rename
    def transfer_comtrade_to_arrays(self, comtrade_file_path):
        try:
            # Read the Comtrade file
            with open(comtrade_file_path, 'r') as file:
                lines = file.readlines()

            # Extract column names from the header
            column_names = lines[0].strip().split(',')

            # Initialize arrays in the dictionary
            for column_name in column_names:
                self.data_arrays[column_name] = []

            # Fill arrays with data
            for line in lines[1:]:
                values = list(map(float, line.strip().split(',')))
                for i, value in enumerate(values):
                    self.data_arrays[column_names[i]].append(value)

            return "Data loaded successfully."
        except Exception as e:
            return f"Error reading Comtrade file: {e}"

    def choose_file(self):#Choose Comtrade File
        file_path = filedialog.askopenfilename(filetypes=[('Comtrade files', '*.dat')])
        if file_path:
            result = self.transfer_comtrade_to_arrays(file_path)
            print(result)
            self.show_arrays()

    def show_arrays(self):

        if not self.data_arrays:
            tk.messagebox.showinfo("Arrays Information", "No arrays available.")
            return

        # Create a Toplevel window for renaming and choosing arrays
        self.modify_arrays_window = tk.Toplevel(self.root)
        self.modify_arrays_window.title("COMTRADE Arrays")

        # Create a dictionary to store renamed arrays
        renamed_arrays = {}

        for idx, (name, data) in enumerate(self.data_arrays.items()):
            # Label and entry for each array
            count_label_text = f"{idx + 1}. Name '{name}' ({len(data)} values):"
            tk.Label(self.modify_arrays_window, text=count_label_text).grid(row=idx, column=0)
            entry_array_name = tk.Entry(self.modify_arrays_window)
            entry_array_name.insert(0, name)
            entry_array_name.grid(row=idx, column=1)

            renamed_arrays[name] = {"entry": entry_array_name, "data": data}

        # Listbox for selecting arrays
        array_listbox = tk.Listbox(self.modify_arrays_window, selectmode=tk.MULTIPLE)
        for name in self.data_arrays.keys():
            array_listbox.insert(tk.END, name)
            array_listbox.grid(row=len(self.data_arrays)+1, column=0, columnspan=2,pady=10)

        # Button to perform actions on selected arrays
        selected_button = tk.Button(self.modify_arrays_window, text="Selected", command=lambda: self.perform_selected_action(array_listbox))
        selected_button.grid(row=len(self.data_arrays) + 2, column=0,columnspan=2,pady=10)

        # Confirm button
        confirm_button = tk.Button(self.modify_arrays_window, text="Rename", command=lambda: self.confirm_modify(renamed_arrays))
        confirm_button.grid(row=len(self.data_arrays) , column=0, columnspan=2, pady=10)

    def perform_selected_action(self, array_listbox):
            # Get the selected array names
            selected_arrays = [array_listbox.get(idx) for idx in array_listbox.curselection()]

            # Check if two arrays are selected
            if len(selected_arrays) == 2:
                # Show the selected array names in the modify_arrays_window
                self.show_selected_arrays_names(selected_arrays, array_listbox)
                self.calculate_Ibias(selected_arrays[0],selected_arrays[1])
                self.calculate_Idiff(selected_arrays[0],selected_arrays[1])
            else:
                tk.messagebox.showerror("Error", "Please select exactly two arrays.")

    def show_selected_arrays_names(self, selected_arrays, array_listbox):
        # Labels to display the selected array names
        tk.Label(self.modify_arrays_window, text=f"Selected Ip: {selected_arrays[0]}").grid(row=len(self.data_arrays) + 3, column=0,columnspan=2, pady=5)
        tk.Label(self.modify_arrays_window, text=f"Selected Is: {selected_arrays[1]}").grid(row=len(self.data_arrays) + 4, column=0, columnspan=2,pady=5)

        # You can also add the selected array names to a Listbox in modify_arrays_window
        '''for selected_array in selected_arrays:
            array_listbox.insert(tk.END, f"Selected: {selected_array}")'''#这里可以加入另一个框展示被选中的东西
    def confirm_modify(self, renamed_arrays):

        # Update renamed arrays based on user input
        for name, info in renamed_arrays.items():
            new_name = info["entry"].get().strip()
            if new_name:
                self.data_arrays[new_name] = info["data"]
                if new_name != name:
                    del self.data_arrays[name]

        #self.modify_arrays_window.destroy()
    def plot_real_trip(self):
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        # Initial plot of X and Y axes
        f = plt.figure(figsize=(6, 4))
        a = f.add_subplot(111)

        if hasattr(self, 'Ibias') and hasattr(self, 'Idiff'):
            Ibias_values = self.Ibias
            Idiff_values = self.Idiff

            a.plot(Ibias_values, Idiff_values, label='Real Trip Curve', linestyle='--')

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
if __name__ == "__main__":
    root = tk.Tk()
    app = Difftest(root)
    root.geometry("900x600")
    root.mainloop()
