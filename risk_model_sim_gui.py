import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Logger for UI
class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, msg + "\n")
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")


def risk_reducer(
    balance, current_risk, increase_check, decrease_check, increase_risk, decrease_risk
):
    if balance >= increase_check:
        return increase_risk
    elif balance <= decrease_check:
        return decrease_risk
    return current_risk


def run_simulation_gui():
    # Clear existing logs
    log_output.configure(state="normal")
    log_output.delete(1.0, tk.END)
    log_output.configure(state="disabled")

    try:
        # Get inputs
        init_balance = float(inputs["Initial Balance"].get())
        profit_target = float(inputs["Profit Target (%)"].get()) / 100
        max_drawdown = float(inputs["Max Drawdown (%)"].get()) / 100
        risk_per_trade = float(inputs["Risk Per Trade (%)"].get()) / 100
        reward_to_risk = float(inputs["Reward-to-Risk"].get())
        win_rate = float(inputs["Win Rate (%)"].get()) / 100
        n_trades = int(inputs["Number of Trades"].get())

        increase_risk = risk_per_trade * 2
        increase_check = init_balance * 1.02
        decrease_risk = risk_per_trade / 2
        decrease_check = init_balance * 0.99

        logger.info("Running Simulations")
        logger.info(f"Initial Balance: ${init_balance}")
        logger.info(f"Profit Target: {profit_target * 100:.2f}%")
        logger.info(f"Max Drawdown: {max_drawdown * 100:.2f}%")
        logger.info(f"Initial Risk: {risk_per_trade * 100:.2f}%")
        logger.info("-" * 30)

        results = []
        worst_dd = 0

        for sim in range(10):
            logger.info(f"\nSimulation {sim + 1}")
            balance = init_balance
            peak = init_balance
            current_risk = risk_per_trade
            passed = False
            failed = False
            outcome = None
            max_sim_dd = 0
            data = {"balances": [balance]}

            for trade in range(n_trades):
                current_risk = risk_reducer(
                    balance,
                    current_risk,
                    increase_check,
                    decrease_check,
                    increase_risk,
                    decrease_risk,
                )
                risk_amount = current_risk * init_balance
                balance += (
                    reward_to_risk * risk_amount
                    if random.random() < win_rate
                    else -risk_amount
                )

                peak = max(peak, balance)
                drawdown = (peak - balance) / peak
                max_sim_dd = max(max_sim_dd, drawdown)

                if balance >= init_balance * (1 + profit_target):
                    logger.info(f"TP hit at trade {trade + 1} — ${balance:.2f}")
                    passed = True
                elif drawdown >= max_drawdown:
                    logger.info(
                        f"Max drawdown hit at trade {trade + 1} — {drawdown * 100:.2f}%"
                    )
                    failed = True

                data["balances"].append(balance)

                if passed:
                    outcome = "PASSED"
                elif failed:
                    outcome = "FAILED"
                else:
                    outcome = "UNDETERMINED!"

            logger.info(
                f"""Final Balance: ${balance:.2f}
Max DD: {max_sim_dd * 100:.2f}% | {outcome}"""
            )
            worst_dd = max(worst_dd, max_sim_dd)
            results.append(data)

        logger.info(f"\nWorst Drawdown Across All Sims: {worst_dd * 100:.2f}%")
        plot_results(results, init_balance, profit_target, max_drawdown)

    except Exception as e:
        logger.error(f"Error: {e}")


def plot_results(results, init_balance, profit_target, max_drawdown):
    for widget in plot_area.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 6), facecolor="black")
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title("Risk Model Performance", color="white")
    ax.set_xlabel("Trade", color="lightgrey")
    ax.set_ylabel("Balance", color="lightgrey")

    for data in results:
        ax.plot(data["balances"], alpha=0.8)

    ax.axhline(
        init_balance * (1 + profit_target),
        color="green",
        linestyle="--",
        label="Profit Target",
    )
    ax.axhline(
        init_balance * (1 - max_drawdown),
        color="red",
        linestyle="--",
        label="Max Drawdown",
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("grey")
    ax.spines["bottom"].set_color("grey")
    ax.tick_params(colors="lightgrey")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=plot_area)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# ==== UI Layout ====
root = tk.Tk()
root.title("Risk Simulator")
root.configure(bg="#111111")
root.geometry("1300x720")

# LEFT COLUMN (Inputs + Logs) - Reduced width
left_column = tk.Frame(root, width=250, bg="#111111")  # Reduced to 250
left_column.pack(side=tk.LEFT, fill=tk.Y, padx=5)

# Top: Inputs
input_section = tk.Frame(left_column, bg="#111111")
input_section.pack(fill=tk.BOTH, padx=5, pady=5)

inputs = {}
fields = [
    ("Initial Balance", 100000),
    ("Profit Target (%)", 6),
    ("Max Drawdown (%)", 3),
    ("Risk Per Trade (%)", 0.5),
    ("Reward-to-Risk", 1.5),
    ("Win Rate (%)", 60),
    ("Number of Trades", 10),
]

for label, default in fields:
    tk.Label(input_section, text=label, bg="#111111", fg="white").pack(
        anchor="w",
        pady=(2, 0),  # Reduced padding
    )
    entry = tk.Entry(input_section, bg="#111111", fg="white", width=15)  # Reduced width
    entry.insert(0, str(default))
    entry.pack(fill=tk.X, pady=(0, 2))  # Reduced padding
    inputs[label] = entry

ttk.Button(input_section, text="Run Simulation", command=run_simulation_gui).pack(
    pady=5  # Reduced padding
)

# Bottom: Logs
log_output = scrolledtext.ScrolledText(
    left_column,
    # height=20,
    bg="#111111",
    fg="lightgrey",
    font=("Consolas", 10),
    width=38,  # Reduced width
)
log_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

# RIGHT COLUMN (Plot)
plot_area = tk.Frame(root, bg="#1e1e1e")
plot_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
text_handler = TextHandler(log_output)
text_handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [text_handler]

root.mainloop()
