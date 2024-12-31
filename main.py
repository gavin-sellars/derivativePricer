import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.stats import norm

class LabeledEntry(ttk.Frame):
    """
    A reusable labeled entry widget with an optional label text.
    """
    def __init__(self, parent, label_text, default_value="", *args, **kwargs):
        super().__init__(parent)
        ttk.Label(self, text=label_text).pack(side="left", padx=(0, 10))
        self.entry = ttk.Entry(self, width=20)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, default_value)  # Add default value
    
    def get(self):
        """
        Returns the value in the entry field.
        """
        return self.entry.get()

    def clear(self):
        """
        Clears the entry field.
        """
        self.entry.delete(0, tk.END)

class FinancialPricer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Financial Instrument Pricer")
        self.geometry("800x600")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill="both", padx=20)
        
        self.option_frame = self.create_tab("Options")
        self.future_frame = self.create_tab("Futures")
        self.swap_frame = self.create_tab("Swaps")
        
        self.setup_option_tab()
        self.setup_future_tab()
        self.setup_swap_tab()
    
    def create_tab(self, title):
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text=title)
        return frame

    def create_labeled_entry(self, parent, label_text, default_value=""):
        entry = LabeledEntry(parent, label_text, default_value=default_value)
        entry.pack(fill="x", pady=5)
        return entry

    def setup_option_tab(self):
        self.spot = self.create_labeled_entry(self.option_frame, "Spot Price ($):", "100")
        self.strike = self.create_labeled_entry(self.option_frame, "Strike Price ($):", "105")
        self.maturity = self.create_labeled_entry(self.option_frame, "Time to Maturity (years):", "1")
        self.rate = self.create_labeled_entry(self.option_frame, "Risk-free Rate (%):", "5")
        self.vol = self.create_labeled_entry(self.option_frame, "Volatility (%):", "20")
        
        type_frame = ttk.Frame(self.option_frame)
        type_frame.pack(fill="x", pady=10)
        self.option_type = tk.StringVar(value="call")
        ttk.Radiobutton(type_frame, text="Call", variable=self.option_type, value="call").pack(side="left", padx=10)
        ttk.Radiobutton(type_frame, text="Put", variable=self.option_type, value="put").pack(side="left", padx=10)
        
        ttk.Button(self.option_frame, text="Calculate Price", command=self.price_option).pack(pady=20)
        self.option_result = ttk.Label(self.option_frame, text="")
        self.option_result.pack(pady=10)
    
    def setup_future_tab(self):
        self.future_spot = self.create_labeled_entry(self.future_frame, "Spot Price ($):", "100")
        self.future_rate = self.create_labeled_entry(self.future_frame, "Risk-free Rate (%):", "5")
        self.future_maturity = self.create_labeled_entry(self.future_frame, "Time to Maturity (years):", "1")
        
        ttk.Button(self.future_frame, text="Calculate Future Price", command=self.price_future).pack(pady=20)
        self.future_result = ttk.Label(self.future_frame, text="")
        self.future_result.pack(pady=10)
    
    def setup_swap_tab(self):
        self.notional = self.create_labeled_entry(self.swap_frame, "Notional Amount ($):", "1000000")
        self.fixed_rate = self.create_labeled_entry(self.swap_frame, "Fixed Rate (%):", "3")
        self.floating_rate = self.create_labeled_entry(self.swap_frame, "Floating Rate (%):", "2.5")
        self.tenor = self.create_labeled_entry(self.swap_frame, "Tenor (years):", "5")
        
        ttk.Button(self.swap_frame, text="Calculate Swap Value", command=self.price_swap).pack(pady=20)
        self.swap_result = ttk.Label(self.swap_frame, text="")
        self.swap_result.pack(pady=10)
    
    def price_option(self):
        try:
            S = float(self.spot.get())
            K = float(self.strike.get())
            T = float(self.maturity.get())
            r = float(self.rate.get()) / 100
            sigma = float(self.vol.get()) / 100
            
            d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if self.option_type.get() == "call":
                price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            else:
                price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            
            self.option_result.configure(text=f"Option Price: ${price:.2f}")
        except ValueError:
            self.option_result.configure(text="Please enter valid numbers.")
    
    def price_future(self):
        try:
            S = float(self.future_spot.get())
            r = float(self.future_rate.get()) / 100
            T = float(self.future_maturity.get())
            
            future_price = S * np.exp(r * T)
            self.future_result.configure(text=f"Future Price: ${future_price:.2f}")
        except ValueError:
            self.future_result.configure(text="Please enter valid numbers.")
    
    def price_swap(self):
        try:
            notional = float(self.notional.get())
            fixed_rate = float(self.fixed_rate.get()) / 100
            floating_rate = float(self.floating_rate.get()) / 100
            tenor = float(self.tenor.get())
            
            annual_difference = notional * (floating_rate - fixed_rate)
            swap_value = annual_difference * tenor
            
            self.swap_result.configure(text=f"Swap Value: ${swap_value:.2f}")
        except ValueError:
            self.swap_result.configure(text="Please enter valid numbers.")

if __name__ == "__main__":
    app = FinancialPricer()
    app.mainloop()
