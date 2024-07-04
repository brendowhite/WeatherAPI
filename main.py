from gui import MainView
# from weatherFetch import *
import tkinter as tk

def main():
    # Opens GUI window
    root = tk.Tk()
    main_view = MainView(root)  # Create an instance of your MainView
    main_view.pack(side="top", fill="both", expand=True)
    root.geometry("700x450")
    root.title("Weather API Fetching Virtual BACnet Device")
    root.resizable(False, False)

    root.mainloop()

if __name__ == "__main__":
    main()
