import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LabeledEntry(ttk.Frame):
    def __init__(self, parent, label_text, default_value="", *args, **kwargs):
        super().__init__(parent)
        ttk.Label(self, text=label_text).pack(side="left", padx=(0, 10))
        self.entry = ttk.Entry(self, width=20)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, default_value)
    
    def get(self):
        return self.entry.get()

class FinancialPricer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Financial Instrument Pricer")
        self.geometry("1200x800")
        
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

        # Graph Frame for Option Breakeven Graph
        self.option_graph_frame = ttk.Frame(self.option_frame)
        self.option_graph_frame.pack(fill="both", expand=True, pady=20)

    def setup_future_tab(self):
        self.future_spot = self.create_labeled_entry(self.future_frame, "Spot Price ($):", "100")
        self.future_rate = self.create_labeled_entry(self.future_frame, "Risk-free Rate (%):", "5")
        self.future_maturity = self.create_labeled_entry(self.future_frame, "Time to Maturity (years):", "1")
        self.carry_cost = self.create_labeled_entry(self.future_frame, "Cost of Carry (%):", "2")
        
        ttk.Button(self.future_frame, text="Calculate Future Price", command=self.price_future).pack(pady=20)
        self.future_result = ttk.Label(self.future_frame, text="")
        self.future_result.pack(pady=10)

        # Graph Frame for Term Structure
        self.future_graph_frame = ttk.Frame(self.future_frame)
        self.future_graph_frame.pack(fill="both", expand=True, pady=20)

    def setup_swap_tab(self):
        self.notional = self.create_labeled_entry(self.swap_frame, "Notional Amount ($):", "1000000")
        self.fixed_rate = self.create_labeled_entry(self.swap_frame, "Fixed Rate (%):", "3")
        self.floating_rate = self.create_labeled_entry(self.swap_frame, "Floating Rate (%):", "2.5")
        self.tenor = self.create_labeled_entry(self.swap_frame, "Tenor (years):", "5")
        
        ttk.Button(self.swap_frame, text="Calculate Swap Value", command=self.price_swap).pack(pady=20)
        self.swap_result = ttk.Label(self.swap_frame, text="")
        self.swap_result.pack(pady=10)

    def plot_graph(self, frame, x_data, y_data, title, xlabel, ylabel, show_grid=False, x_axis_at_zero=False):
        """
        Plot a graph in the given frame using Matplotlib with optional grid and x-axis alignment.
        """
        for widget in frame.winfo_children():
            widget.destroy()  # Clear previous graph

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(x_data, y_data, label="Breakeven/Price Movement", color="blue")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        
        # Add grid if specified
        if show_grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set x-axis at zero if specified
        if x_axis_at_zero:
            ax.axhline(0, color='black', linewidth=1, linestyle='--')

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()


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

            # Generate Breakeven Graph
            spot_prices = np.linspace(S * 0.5, S * 1.5, 100)
            payoffs = [(max(sp - K, 0) if self.option_type.get() == "call" else max(K - sp, 0)) - price for sp in spot_prices]
            
            # Add grid and a clear x-axis for the breakeven graph
            self.plot_graph(self.option_graph_frame, spot_prices, payoffs, "Option Breakeven Graph", "Spot Price ($)", "Payoff ($)", show_grid=True, x_axis_at_zero=True)
        except ValueError:
            self.option_result.configure(text="Please enter valid numbers.")


    def price_future(self):
        try:
            S = float(self.future_spot.get())
            r = float(self.future_rate.get()) / 100
            c = float(self.carry_cost.get()) / 100
            T = float(self.future_maturity.get())
            
            future_price = S * np.exp((r + c) * T)
            self.future_result.configure(text=f"Future Price: ${future_price:.2f}")

            # Generate Term Structure Graph
            times = np.linspace(0, T, 100)
            prices = S * np.exp((r + c) * times)
            self.plot_graph(self.future_graph_frame, times, prices, "Future Price Movement (Cost of Carry)", "Time to Maturity (years)", "Future Price ($)", show_grid=True)
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
