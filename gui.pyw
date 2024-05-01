import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from postprocess import process_raw_reads, combine_dataframes, plot_2D, plot_3D, plot_distributions
from ttkbootstrap import Style


class ProcessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Processor")
        style = Style(theme="darkly")  # You can change the theme to any available theme

        self.loaded_files = []
        self.processed_df = None
        self.processed_dfs = []

        self.loaded_file_label = ttk.Label(root, text="No files loaded", foreground="red")
        self.loaded_file_label.pack()

        # Parameters
        self.quantity_var = tk.StringVar(root, "top10")
        self.subtract_bg_var = tk.BooleanVar(root, True)
        self.smoothing_var = tk.IntVar(root, 3)
        self.window_size_var = tk.IntVar(root, 11)
        self.show_peaks_var = tk.BooleanVar(root, True)
        self.peak_prominence_var = tk.DoubleVar(root, 0.02)
        self.peak_abs_height_var = tk.DoubleVar(root, 0.02)
        self.peak_rel_height_var = tk.DoubleVar(root, 0.5)

        # Widgets
        self.quantity_label = ttk.Label(root, text="Quantity:")
        self.quantity_label.pack()
        self.quantity_menu = ttk.OptionMenu(root, self.quantity_var, "mean", "max", "top10", command=self.process_data)
        self.quantity_menu.pack()

        # Buttons
        self.file_label = ttk.Label(root, text="CSV Files:")
        self.file_label.pack()
        self.file_entry = ttk.Entry(root, state='readonly', textvariable=tk.StringVar(root, "None"))
        self.file_entry.pack()
        self.file_button = ttk.Button(root, text="Browse", command=self.load_and_process_data)
        self.file_button.pack()

        self.bg_label = ttk.Label(root, text="Background file path (optional):")
        self.bg_label.pack()
        self.bg_entry = ttk.Entry(root, state='readonly', textvariable=tk.StringVar(root, "None"))
        self.bg_entry.pack()
        self.bg_button = ttk.Button(root, text="Browse", command=self.browse_bg_file)
        self.bg_button.pack()

        self.subtract_bg_check = ttk.Checkbutton(root, text="Subtract Background", variable=self.subtract_bg_var)
        self.subtract_bg_check.pack()

        self.smoothing_label = ttk.Label(root, text="Smoothing Window Size:")
        self.smoothing_label.pack()
        self.smoothing_entry = ttk.Entry(root, textvariable=self.smoothing_var)
        self.smoothing_entry.pack()

        self.window_size_label = ttk.Label(root, text="Rolling Window Size:")
        self.window_size_label.pack()
        self.window_size_entry = ttk.Entry(root, textvariable=self.window_size_var)
        self.window_size_entry.pack()

        self.show_peaks_check = ttk.Checkbutton(root, text="Show Peaks", variable=self.show_peaks_var)
        self.show_peaks_check.pack()

        self.peak_prominence_label = ttk.Label(root, text="Peak Prominence:")
        self.peak_prominence_label.pack()
        self.peak_prominence_entry = ttk.Entry(root, textvariable=self.peak_prominence_var)
        self.peak_prominence_entry.pack()

        self.peak_abs_height_label = ttk.Label(root, text="Peak Absolute Height:")
        self.peak_abs_height_label.pack()
        self.peak_abs_height_entry = ttk.Entry(root, textvariable=self.peak_abs_height_var)
        self.peak_abs_height_entry.pack()

        self.peak_rel_height_label = ttk.Label(root, text="Peak Relative Height:")
        self.peak_rel_height_label.pack()
        self.peak_rel_height_entry = ttk.Entry(root, textvariable=self.peak_rel_height_var)
        self.peak_rel_height_entry.pack()

        self.save_button = ttk.Button(root, text="Save Processed Data", command=self.save_processed_data,
                                      state='disabled')
        self.save_button.pack()

        self.plot_2d_button = ttk.Button(root, text="Plot 2D", command=self.plot_2d, state='disabled')
        self.plot_2d_button.pack()

        self.plot_3d_button = ttk.Button(root, text="Plot 3D", command=self.plot_3d, state='disabled')
        self.plot_3d_button.pack()

        self.plot_hist_button = ttk.Button(root, text="Plot histograms", command=self.plot_histograms, state='disabled')
        self.plot_hist_button.pack()

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

    def browse_bg_file(self):
        bg_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if bg_path:
            self.bg_entry.config(state='normal')
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(0, bg_path)
            self.bg_entry.config(state='readonly')
        else:
            self.bg_entry.config(state='normal')
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(0, "None")
            self.bg_entry.config(state='readonly')

    def process_data(self, new_val=None):
        if self.loaded_files:
            dfs = []
            self.processed_dfs = []
            for file in self.loaded_files:
                df = process_raw_reads(file,
                                       quantity=self.quantity_var.get(),
                                       bg_path=None if self.bg_entry.get() == "None" else self.bg_entry.get(),
                                       subtract_bg=self.subtract_bg_var.get(),
                                       smoothing=self.smoothing_var.get(),
                                       window_size=self.window_size_var.get())
                dfs.append(df)
                self.processed_dfs.append(df)
            self.processed_df = combine_dataframes(dfs)
            self.save_button.config(state='normal')
            self.plot_2d_button.config(state='normal')
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

    def plot_3d(self):
        if self.processed_df is not None:
            plot_3D(self.processed_df)
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
