import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from postprocess import process_raw_reads, combine_dataframes, plot_2D, plot_3D, plot_distributions, plot_image
from ttkbootstrap import Style
from ttkbootstrap.constants import *


class ProcessGUI(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("DWLab calcium analysis tool")
        style = Style(theme="litera")  # You can change the theme to any available theme

        # list of loaded files
        self.loaded_files = []
        # dictionary mapping filename to dataframes
        self.processed_dfs = {}

        # We use the attributes below to check if something has changed to prevent unnecessary computation.
        # currently select files
        self.active_files = []
        # active df
        self.active_df = None
        # processing params changed
        self.params_changed = False

        self.pack(fill=BOTH, expand=YES)
        # Set up columns
        for i in range(3):
            self.columnconfigure(i, weight=1)

        col1 = ttk.Frame(self, padding=10)
        col1.grid(row=0, column=0, sticky=NSEW)

        self.col2 = ttk.Frame(self, padding=10)
        self.col2.grid(row=0, column=1, sticky=NSEW)

        col3 = ttk.Frame(self, padding=10)
        col3.grid(row=0, column=2, sticky=NSEW)

        # Label Frames
        self.processing_frame = ttk.LabelFrame(col3, text='Data processing')
        self.processing_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.peak_frame = ttk.LabelFrame(col3, text='Peak detection')
        self.peak_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # New Label for Loaded Data
        self.loaded_data_frame = ttk.LabelFrame(col1, text="Loaded Data:")
        self.loaded_data_frame.pack()

        self.file_button = ttk.Button(self.loaded_data_frame, text="Browse", command=self.load_and_process_data)
        self.file_button.pack(in_=self.loaded_data_frame)

        # Checkbox Variables
        self.checkbox_vars = []

        # Quantity Menu
        self.quantity_var = tk.StringVar(root, "top10")
        self.quantity_label = ttk.Label(self.processing_frame, text="Quantity:")
        self.quantity_label.pack(in_=self.processing_frame)
        self.quantity_menu = ttk.OptionMenu(self.processing_frame, self.quantity_var, "mean", "mean", "max", "top10",
                                            command=self.on_proc_changed)
        self.quantity_menu.pack(in_=self.processing_frame)

        # Subtract Background Checkbutton
        self.subtract_bg_var = tk.BooleanVar(root, True)
        self.subtract_bg_check = ttk.Checkbutton(self.processing_frame, text="Subtract Background",
                                                 variable=self.subtract_bg_var, command=self.on_proc_changed)
        self.subtract_bg_check.pack()

        # Smoothing Window Size Entry
        self.smoothing_var = tk.IntVar(root, 3)
        self.smoothing_var.trace("w", self.on_proc_changed)
        self.smoothing_label = ttk.Label(self.processing_frame, text="Smoothing Window Size:")
        self.smoothing_label.pack()
        self.smoothing_entry = ttk.Entry(self.processing_frame, textvariable=self.smoothing_var)
        self.smoothing_entry.pack()

        # Rolling Window Size Entry
        self.window_size_var = tk.IntVar(root, 11)
        self.window_size_var.trace("w", self.on_proc_changed)
        self.window_size_label = ttk.Label(self.processing_frame, text="Rolling Window Size:")
        self.window_size_label.pack()
        self.window_size_entry = ttk.Entry(self.processing_frame, textvariable=self.window_size_var)
        self.window_size_entry.pack()

        # Show Peaks Checkbutton
        self.show_peaks_var = tk.BooleanVar(root, True)
        self.show_peaks_check = ttk.Checkbutton(self.peak_frame, text="Show Peaks", variable=self.show_peaks_var)
        self.show_peaks_check.pack()

        # Peak Prominence Entry
        self.peak_prominence_var = tk.DoubleVar(root, 0.02)
        self.peak_prominence_label = ttk.Label(self.peak_frame, text="Peak Prominence:")
        self.peak_prominence_label.pack()
        self.peak_prominence_entry = ttk.Entry(self.peak_frame, textvariable=self.peak_prominence_var)
        self.peak_prominence_entry.pack()

        # Peak Absolute Height Entry
        self.peak_abs_height_var = tk.DoubleVar(root, 0.1)
        self.peak_abs_height_label = ttk.Label(self.peak_frame, text="Peak Absolute Height:")
        self.peak_abs_height_label.pack()
        self.peak_abs_height_entry = ttk.Entry(self.peak_frame, textvariable=self.peak_abs_height_var)
        self.peak_abs_height_entry.pack()

        # Peak Relative Height Entry
        self.peak_rel_height_var = tk.DoubleVar(root, 0.5)
        self.peak_rel_height_label = ttk.Label(self.peak_frame, text="Peak Relative Height:")
        self.peak_rel_height_label.pack()
        self.peak_rel_height_entry = ttk.Entry(self.peak_frame, textvariable=self.peak_rel_height_var)
        self.peak_rel_height_entry.pack()

        # Save Button
        self.save_button = ttk.Button(self.col2, text="Save Processed Data", command=self.save_processed_data,
                                      state='disabled')
        self.save_button.pack(in_=self.col2, fill=X)

        # Plot 2D Button
        self.plot_2d_button = ttk.Button(self.col2, text="Plot 2D", command=self.plot_2d, state='disabled')
        self.plot_2d_button.pack(in_=self.col2, fill=X)

        # Plot matrix
        self.plot_mat_button = ttk.Button(self.col2, text="Plot Matrix", command=self.plot_mat, state='disabled')
        self.plot_mat_button.pack(in_=self.col2, fill=X)

        # Plot 3D Button
        self.plot_3d_button = ttk.Button(self.col2, text="Plot 3D", command=self.plot_3d, state='disabled')
        self.plot_3d_button.pack(in_=self.col2, fill=X)

        # Plot Histograms Button
        self.plot_hist_button = ttk.Button(self.col2, text="Plot histograms", command=self.plot_histograms,
                                           state='disabled')
        self.plot_hist_button.pack(in_=self.col2, fill=X)

    def load_and_process_data(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        try:
            if files:
                # Create Checkboxes for Loaded Files
                for file in files:
                    if not file in self.loaded_files:
                        var = tk.BooleanVar(self.loaded_data_frame, value=True)
                        checkbox = ttk.Checkbutton(self.loaded_data_frame, text=os.path.basename(file), variable=var,
                                                   command=self.on_actives_changed)
                        checkbox.pack(expand=True)
                        self.checkbox_vars.append((file, var))

                        df = process_raw_reads(file,
                                               quantity=self.quantity_var.get(),
                                               subtract_bg=self.subtract_bg_var.get(),
                                               smoothing=self.smoothing_var.get(),
                                               window_size=self.window_size_var.get())
                        self.loaded_files.append(file)
                        self.active_files.append(file)
                        self.processed_dfs[file] = df
                self.on_actives_changed()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_proc_changed(self):
        self.params_changed = True

    def on_actives_changed(self):
        # TODO: change state based on number of active files
        self.active_df = None
        self.active_files = [file for file, var in self.checkbox_vars if var.get()]
        if len(self.active_files) > 0:
            self.save_button.config(state='normal')
            self.plot_2d_button.config(state='normal')
            self.plot_mat_button.config(state='normal')
            self.plot_3d_button.config(state='normal')
            self.plot_hist_button.config(state='normal')
        else:
            self.save_button.config(state='disabled')
            self.plot_2d_button.config(state='disabled')
            self.plot_mat_button.config(state='disabled')
            self.plot_3d_button.config(state='disabled')
            self.plot_hist_button.config(state='disabled')

    def get_active_data(self, combined: bool = True):
        # If params have changed, update data
        if self.params_changed:
            self.process_data()
            self.params_changed = False

        # If no active files, return None
        if len(self.active_files) == 0:
            return None

        # Otherwise return as list or as combined
        dfs = [self.processed_dfs[file] for file in self.active_files]
        if combined:
            # If we haven't changed anything, no need to combine again.
            if self.active_df:
                return self.active_df

            df = combine_dataframes(dfs)
            self.active_df = df
            return df
        else:
            return dfs

    def process_data(self, new_val=None):
        for file, var in self.checkbox_vars:
            if var.get():
                df = process_raw_reads(file,
                                       quantity=self.quantity_var.get(),
                                       subtract_bg=self.subtract_bg_var.get(),
                                       smoothing=self.smoothing_var.get(),
                                       window_size=self.window_size_var.get())
                self.processed_dfs[file] = df

    def save_processed_data(self):
        active_df = self.get_active_data()
        if active_df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                self.active_df.to_csv(save_path, index=False)
                messagebox.showinfo("Success", "Processed data saved successfully.")
        else:
            messagebox.showerror("Error", "No processed data to save.")

    def plot_2d(self):
        active_df = self.get_active_data()
        if active_df is not None:
            plot_2D(active_df,
                    show_peaks=self.show_peaks_var.get(),
                    peak_prominence=self.peak_prominence_var.get(),
                    peak_abs_height=self.peak_abs_height_var.get(),
                    peak_rel_height=self.peak_rel_height_var.get())
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_mat(self):
        active_df = self.get_active_data()
        if active_df is not None:
            plot_image(active_df)
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_3d(self):
        active_df = self.get_active_data()
        if active_df is not None:
            plot_3D(active_df,
                    show_peaks=self.show_peaks_var.get(),
                    peak_prominence=self.peak_prominence_var.get(),
                    peak_abs_height=self.peak_abs_height_var.get(),
                    peak_rel_height=self.peak_rel_height_var.get())
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_histograms(self):
        active_dfs = self.get_active_data(combined=False)
        if active_dfs is not None:
            plot_distributions(active_dfs, [os.path.basename(f)[:-4] for f in self.active_files],
                               peak_prominence=self.peak_prominence_var.get(),
                               peak_abs_height=self.peak_abs_height_var.get(),
                               peak_rel_height=self.peak_rel_height_var.get()
                               )
        else:
            messagebox.showerror("Error", "No processed data.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessGUI(root)
    root.mainloop()
