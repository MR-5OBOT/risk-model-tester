import logging
import random

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)  # Set logging level

# User inputs
# max_overall_drawdown = float(input("Enter max overall drawdown (e.g., 0.10 for 10%): "))
# profit_target = float(input("Enter profit target (e.g., 0.10 for 10%): "))
# risk_per_trade = float(input("Enter risk per trade (e.g., 0.01 for 1%): "))
#
# win_rate = float(input("Enter win rate (e.g., 0.60 for 60%): "))
# reward_to_risk = float(input("Enter reward to risk ratio (e.g., 2.0 for 2:1): "))
# trades_to_pass = int(input("Enter number of trades needed to pass: "))

# increase_input = input("increase risk after x% :")
# increase_input = float(increase_input)
# increase_check = initial_balance * (increase_input / 100) + initial_balance
#
# derease_input = input("decrease risk after x% :")
# derease_input = float(derease_input)
# increase_check = initial_balance * (1 - derease_input / 100)
# decrease_check = initial_balance * 0.98

# Paramepers
initial_balance = 50000
profit_target = 0.06
max_overall_drawdown = 0.06
risk_per_trade = 0.01
win_rate = 0.2
reward_to_risk = 2.0
trades_to_pass = 20

# the model risk controllers
increase_risk = 0.02
increase_check = initial_balance * 1.03
decrease_risk = 0.005
decrease_check = initial_balance * 0.99


# function to control risk dynamiclly
def risk_reducer(virtual_balance, current_risk):
    if virtual_balance >= increase_check:
        return increase_risk
    elif virtual_balance <= decrease_check:
        return decrease_risk
    else:
        return current_risk


def calculate_drawdown(peak, balance):
    """Calculate the current drawdown based on the peak balance."""


# models simulations
def run_simulation():
    try:
        num_simulations = 10
        results = []
        for sim in range(num_simulations):
            logging.info(f"Starting simulation {sim + 1}")
            virtual_balance = initial_balance
            current_risk = risk_per_trade
            sim_max_drawdown = 0
            simulation_data = {
                "balances": [virtual_balance],
                "risks": [current_risk],
                "drawdowns": [0],
            }
            # Initialize a flag for target & max dd
            condition_met = False
            peak = initial_balance

            for trade in range(trades_to_pass):
                current_risk = risk_reducer(virtual_balance, current_risk)
                risk_amount = current_risk * initial_balance

                # Simulate trade outcome
                if random.random() < win_rate:
                    virtual_balance += reward_to_risk * risk_amount
                else:
                    virtual_balance -= risk_amount

                # Track drawdowns
                if virtual_balance > peak:
                    peak = virtual_balance  # Update peak if a new high is reached

                # Track drawdowns
                current_drawdown = (peak - virtual_balance) / peak if peak > 0 else 0
                sim_max_drawdown = max(sim_max_drawdown, current_drawdown)

                # Check for violations
                if virtual_balance >= initial_balance * (1 + profit_target) and not condition_met:
                    logging.info(f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}% [{profit_target *100:.0f}% Target reached]")
                    condition_met = True
                if sim_max_drawdown >= max_overall_drawdown * initial_balance and not condition_met:
                    logging.info(f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}% [{max_overall_drawdown *100:.0f}% Max DD reached]")
                    condition_met = True

                # Log the balance and drawdown for each trade
                logging.info(f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}%")

                # Store simulation data
                simulation_data["balances"].append(virtual_balance)
                simulation_data["risks"].append(current_risk)
                simulation_data["drawdowns"].append(sim_max_drawdown)

            results.append(simulation_data)
            logging.info(f"Ending simulation {sim + 1}")

            # worst dd value
            worst_dd_all_sims = max(simulation_data["drawdowns"])

            # loggings
            logging.info(f"[Sim {sim}] final balance: {virtual_balance}")
            logging.info(f"[Sim {sim}] current_risk: {current_risk * 100:.2f}%")
            logging.info(f"[Sim {sim}] max_drawdown: {sim_max_drawdown * 100:.2f}%")

            # logging.info(f"[sim {sim+1}] drawdowns: {simulation_data['drawdowns']}")
            logging.info(f"[all sims] worst drawdown: {worst_dd_all_sims * 100:.2f}%")

        return results

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def plotting(results):
    logging.info("Plotting the graph")
    plt.style.use("dark_background")
    plt.figure(figsize=(8, 6))
    ax = plt.gca()  # Get the current axis
    ax.set_title("Risk Model Performance", color="grey", fontsize=20, loc="center", pad=15)
    ax.set_xlabel("Trade Number", color="grey", fontsize=12)
    ax.set_ylabel("Balance", color="grey", fontsize=12)

    # plot balances
    for sim, data in enumerate(results):
        # ax.plot(data["balances"], label=f"Sim {sim + 1}")
        ax.plot(data["balances"])

    ax.axhline(
        initial_balance * (1 + profit_target),
        color="green",
        linestyle="--",
        label="Profit Target",
    )
    ax.axhline(
        initial_balance * (1 - max_overall_drawdown),
        color="red",
        linestyle="--",
        label="Max Drawdown",
    )
    # Customize spines and ticks
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(axis="x", direction="inout", length=6, width=2, colors="grey")
    ax.tick_params(axis="y", direction="inout", length=6, width=2, colors="grey")
    ax.spines["bottom"].set_linewidth(2)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_color("grey")
    ax.spines["left"].set_color("grey")
    # Add a watermark
    ax.text(
        0.5,
        0.5,  # X and Y position (relative, in axes coordinates)
        "@MR_5OBOT",  # Watermark text
        fontsize=30,  # Font size
        color="gray",  # Text color
        alpha=0.12,  # Transparency (0.0 to 1.0)
        ha="center",  # Horizontal alignment
        va="center",  # Vertical alignment
        rotation=10,  # Rotate text
        transform=ax.transAxes,  # Transform relative to the axes (0 to 1 range)
    )
    # Finalize plot
    ax.legend()
    plt.savefig("risk_model_performance.png")  # Save the figure
    plt.show()

 # run the programe
if __name__ == "__main__":
    run_simulation()
    results = run_simulation()
    plotting(results)
