import tkinter as tk
from gui.scraper_app import ScraperApp

def main():
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
