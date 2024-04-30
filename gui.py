import tkinter as tk
from tkinter import filedialog, messagebox
from postprocess import process_raw_reads, plot_smoothed_data, plot_3d

def load_and_process_data():
    filepath = filedialog.askopenfilename(title="Select CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    if filepath:
        try:
            df = process_raw_reads(filepath)
            messagebox.showinfo("Success", "Data processed successfully.")
            return df
        except Exception as e:
            messagebox.showerror("Error", f"Error processing data: {str(e)}")

def save_plot(df):
    filepath = filedialog.asksaveasfilename(title="Save Plot As", filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
    if filepath:
        try:
            plot_smoothed_data(df)
            plt.savefig(filepath)
            messagebox.showinfo("Success", "Plot saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving plot: {str(e)}")

def show_3d_plot(df):
    try:
        plot_3d(df)
    except Exception as e:
        messagebox.showerror("Error", f"Error showing 3D plot: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Data Processing GUI")

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    load_button = tk.Button(frame, text="Load & Process Data", command=load_and_process_data)
    load_button.grid(row=0, column=0, padx=10, pady=5)

    save_button = tk.Button(frame, text="Save Plot", command=save_plot)
    save_button.grid(row=0, column=1, padx=10, pady=5)

    show_3d_button = tk.Button(frame, text="Show 3D Plot", command=show_3d_plot)
    show_3d_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
