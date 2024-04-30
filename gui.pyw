import tkinter as tk
from tkinter import filedialog, messagebox
from postprocess import process_raw_reads, plot_2D, plot_3D

class ProcessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Processor")
        self.loaded_file_label = tk.Label(root, text="No file loaded", fg="red")
        self.loaded_file_label.pack()

        # Parameters
        self.fpath = None
        self.bg_path = None
        self.quantity_var = tk.StringVar(root, "top10")
        self.subtract_bg_var = tk.BooleanVar(root, True)
        self.smoothing_var = tk.IntVar(root, 3)
        self.window_size_var = tk.IntVar(root, 11)

        # Widgets
        self.quantity_label = tk.Label(root, text="Quantity:")
        self.quantity_label.pack()
        self.quantity_menu = tk.OptionMenu(root, self.quantity_var, "mean", "max", "top10")
        self.quantity_menu.pack()

        self.bg_label = tk.Label(root, text="Background File Path:")
        self.bg_label.pack()
        self.bg_entry = tk.Entry(root, state='readonly', textvariable=tk.StringVar(root, "None"))
        self.bg_entry.pack()
        self.bg_button = tk.Button(root, text="Browse", command=self.browse_bg_file)
        self.bg_button.pack()

        self.subtract_bg_check = tk.Checkbutton(root, text="Subtract Background", variable=self.subtract_bg_var)
        self.subtract_bg_check.pack()

        self.smoothing_label = tk.Label(root, text="Smoothing Window Size:")
        self.smoothing_label.pack()
        self.smoothing_entry = tk.Entry(root, textvariable=self.smoothing_var)
        self.smoothing_entry.pack()

        self.window_size_label = tk.Label(root, text="Rolling Window Size:")
        self.window_size_label.pack()
        self.window_size_entry = tk.Entry(root, textvariable=self.window_size_var)
        self.window_size_entry.pack()

        # Buttons
        self.load_button = tk.Button(root, text="Load Data", command=self.load_and_process_data)
        self.load_button.pack()

        self.save_button = tk.Button(root, text="Save Processed Data", command=self.save_processed_data, state='disabled')
        self.save_button.pack()

        self.plot_2d_button = tk.Button(root, text="Plot 2D", command=self.plot_2d, state='disabled')
        self.plot_2d_button.pack()

        self.plot_3d_button = tk.Button(root, text="Plot 3D", command=self.plot_3d, state='disabled')
        self.plot_3d_button.pack()

    def load_and_process_data(self):
        self.fpath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.fpath:
            self.loaded_file_label.config(text="File loaded: " + self.fpath, fg="green")
            try:
                self.process_data()
                self.save_button.config(state='normal')
                self.plot_2d_button.config(state='normal')
                self.plot_3d_button.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.loaded_file_label.config(text="No file loaded", fg="red")

    def browse_bg_file(self):
        self.bg_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.bg_path:
            self.bg_entry.config(state='normal')
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(0, self.bg_path)
            self.bg_entry.config(state='readonly')
        else:
            self.bg_entry.config(state='normal')
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(0, "None")
            self.bg_entry.config(state='readonly')

    def process_data(self):
        processed_df = process_raw_reads(self.fpath,
                                         quantity=self.quantity_var.get(),
                                         bg_path=None if self.bg_path == "None" else self.bg_path,
                                         subtract_bg=self.subtract_bg_var.get(),
                                         smoothing=self.smoothing_var.get(),
                                         window_size=self.window_size_var.get())
        self.processed_df = processed_df

    def save_processed_data(self):
        if hasattr(self, 'processed_df'):
            save_path = self.fpath.replace(".csv", "_processed.csv")
            self.processed_df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Processed data saved successfully.")
        else:
            messagebox.showerror("Error", "No processed data to save.")

    def plot_2d(self):
        if hasattr(self, 'processed_df'):
            plot_2D(self.processed_df)
        else:
            messagebox.showerror("Error", "Data not processed.")

    def plot_3d(self):
        if hasattr(self, 'processed_df'):
            plot_3D(self.processed_df)
        else:
            messagebox.showerror("Error", "Data not processed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessGUI(root)
    root.mainloop()