import tkinter as tk
import matplotlib.pyplot as plt

from hwo_gtvt.hwo_tvt import Ephemeris
from hwo_gtvt.plotting import plot_visibility

def launch_gtvt_gui():
    root = tk.Tk()
    root.title("HWO GTVT")
    root.resizable(False, False)
 
    ra = tk.StringVar()
    dec = tk.StringVar()
    
    def generate_plot():
        eph = Ephemeris() # Could allow date specification here: e.g. Ephemeris(start_date=start, end_date=end)
        eph.get_fixed_target_positions(ra.get(), dec.get())
        plot_visibility(eph, instrument=None)

    def close_all():
        root.destroy()
        plt.close("all")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill="both", expand=True) 

    ra_label = tk.Label(frame, text="RA", font=("calibre", 10, "bold"), anchor="w")
    ra_entry = tk.Entry(frame, textvariable=ra, font=("calibre", 10,"normal"))

    dec_label = tk.Label(frame, text="Dec", font=("calibre", 10, "bold"), anchor="w")
    dec_entry = tk.Entry(frame, textvariable=dec, font=("calibre", 10, "normal"))
    
    plot_button = tk.Button(frame, text="Generate Plot", command=generate_plot)
    quit_button = tk.Button(frame, text="Quit", command=close_all)

    ra_label.grid(row=0, column=0, sticky="w")
    ra_entry.grid(row=1, column=0)
    dec_label.grid(row=2, column=0, sticky="w")
    dec_entry.grid(row=3, column=0)
    plot_button.grid(row=4,column=0)
    quit_button.grid(row=5,column=0)

    root.mainloop()
