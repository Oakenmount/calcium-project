import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from postprocess import process_raw_reads, combine_dataframes, plot_2D, plot_3D, plot_distributions, plot_image
from ttkbootstrap import Style


class ProcessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DWLab calcium analysis tool")
        style = Style(theme="litera")  # You can change the theme to any available theme

        self.loaded_files = []
        self.processed_df = None
        self.processed_dfs = []

        # Left Frame for buttons
        self.left_frame = ttk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Right Frame for processing and peak parameters
        self.right_frame = ttk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Label Frames
        self.processing_frame = ttk.LabelFrame(self.right_frame, text='Data processing')
        self.processing_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.peak_frame = ttk.LabelFrame(self.right_frame, text='Peak detection')
        self.peak_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Loaded Files Label
        self.loaded_file_label = ttk.Label(self.left_frame, text="No files loaded", foreground="red")
        self.loaded_file_label.pack()

        # Quantity Menu
        self.quantity_var = tk.StringVar(root, "top10")
        self.quantity_label = ttk.Label(self.processing_frame, text="Quantity:")
        self.quantity_label.pack(in_=self.processing_frame)
        self.quantity_menu = ttk.OptionMenu(self.processing_frame, self.quantity_var, "mean", "mean", "max", "top10",
                                            command=self.process_data)
        self.quantity_menu.pack(in_=self.processing_frame)

        # File Entry and Button
        self.file_label = ttk.Label(self.left_frame, text="CSV Files:")
        self.file_label.pack(in_=self.left_frame)
        self.file_entry = ttk.Entry(self.left_frame, state='readonly', textvariable=tk.StringVar(root, "None"))
        self.file_entry.pack(in_=self.left_frame)
        self.file_button = ttk.Button(self.left_frame, text="Browse", command=self.load_and_process_data)
        self.file_button.pack(in_=self.left_frame)

        # Subtract Background Checkbutton
        self.subtract_bg_var = tk.BooleanVar(root, True)
        self.subtract_bg_check = ttk.Checkbutton(self.processing_frame, text="Subtract Background",
                                                 variable=self.subtract_bg_var)
        self.subtract_bg_check.pack()

        # Smoothing Window Size Entry
        self.smoothing_var = tk.IntVar(root, 3)
        self.smoothing_label = ttk.Label(self.processing_frame, text="Smoothing Window Size:")
        self.smoothing_label.pack()
        self.smoothing_entry = ttk.Entry(self.processing_frame, textvariable=self.smoothing_var)
        self.smoothing_entry.pack()

        # Rolling Window Size Entry
        self.window_size_var = tk.IntVar(root, 11)
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
        self.peak_abs_height_var = tk.DoubleVar(root, 0.02)
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
        self.save_button = ttk.Button(self.left_frame, text="Save Processed Data", command=self.save_processed_data,
                                      state='disabled')
        self.save_button.pack(in_=self.left_frame)

        # Plot 2D Button
        self.plot_2d_button = ttk.Button(self.left_frame, text="Plot 2D", command=self.plot_2d, state='disabled')
        self.plot_2d_button.pack(in_=self.left_frame)

        # Plot matrix
        self.plot_mat_button = ttk.Button(self.left_frame, text="Plot Matrix", command=self.plot_mat, state='disabled')
        self.plot_mat_button.pack(in_=self.left_frame)

        # Plot 3D Button
        self.plot_3d_button = ttk.Button(self.left_frame, text="Plot 3D", command=self.plot_3d, state='disabled')
        self.plot_3d_button.pack(in_=self.left_frame)

        # Plot Histograms Button
        self.plot_hist_button = ttk.Button(self.left_frame, text="Plot histograms", command=self.plot_histograms,
                                           state='disabled')
        self.plot_hist_button.pack(in_=self.left_frame)

    def load_and_process_data(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if files:
            self.loaded_files = files
            self.loaded_file_label.config(text="Files loaded: " + ', '.join(files), foreground="green")
            try:
                self.process_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.loaded_file_label.config(text="No files loaded", foreground="red")

    def process_data(self, new_val=None):
        if self.loaded_files:
            dfs = []
            self.processed_dfs = []
            for file in self.loaded_files:
                df = process_raw_reads(file,
                                       quantity=self.quantity_var.get(),
                                       subtract_bg=self.subtract_bg_var.get(),
                                       smoothing=self.smoothing_var.get(),
                                       window_size=self.window_size_var.get())
                dfs.append(df)
                self.processed_dfs.append(df)
            self.processed_df = combine_dataframes(dfs)
            self.save_button.config(state='normal')
            self.plot_2d_button.config(state='normal')
            self.plot_mat_button.config(state='normal')
            self.plot_3d_button.config(state='normal')
            self.plot_hist_button.config(state='normal')

    def save_processed_data(self):
        if self.processed_df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                self.processed_df.to_csv(save_path, index=False)
                messagebox.showinfo("Success", "Processed data saved successfully.")
        else:
            messagebox.showerror("Error", "No processed data to save.")

    def plot_2d(self):
        if self.processed_df is not None:
            plot_2D(self.processed_df,
                    show_peaks=self.show_peaks_var.get(),
                    peak_prominence=self.peak_prominence_var.get(),
                    peak_abs_height=self.peak_abs_height_var.get(),
                    peak_rel_height=self.peak_rel_height_var.get())
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_mat(self):
        if self.processed_df is not None:
            plot_image(self.processed_df)
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_3d(self):
        if self.processed_df is not None:
            plot_3D(self.processed_df,
                    show_peaks=self.show_peaks_var.get(),
                    peak_prominence=self.peak_prominence_var.get(),
                    peak_abs_height=self.peak_abs_height_var.get(),
                    peak_rel_height=self.peak_rel_height_var.get())
        else:
            messagebox.showerror("Error", "No processed data.")

    def plot_histograms(self):
        if self.processed_df is not None:
            plot_distributions(self.processed_dfs, [os.path.basename(f)[:-4] for f in self.loaded_files],
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
