import logging
import random

import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)  # Set logging level


# Function to control risk dynamically
def risk_reducer(virtual_balance, current_risk, increase_check, increase_risk, decrease_check, decrease_risk):
    if virtual_balance >= increase_check:
        return increase_risk
    elif virtual_balance <= decrease_check:
        return decrease_risk
    else:
        return current_risk


# Models simulations
def run_simulation():
    try:
        num_simulations = 10
        results = []
        worst_drawdown_all_sims = 0  # outside the loop to track it well

        for sim in range(num_simulations):
            logging.info(f"Starting simulation {sim + 1}")
            virtual_balance = initial_balance
            current_risk = risk_per_trade
            simulation_data = {"balances": [virtual_balance], "risks": [current_risk], "drawdowns": [0]}
            sim_max_drawdown = 0
            condition_met = False
            peak = initial_balance

            for trade in range(trades_to_pass):
                current_risk = risk_reducer(
                    virtual_balance, current_risk, increase_check, increase_risk, decrease_check, decrease_risk
                )
                risk_amount = current_risk * initial_balance

                # Simulate trade outcome
                if random.random() < win_rate:
                    virtual_balance += reward_to_risk * risk_amount
                else:
                    virtual_balance -= risk_amount

                # Track drawdowns
                if virtual_balance > peak:
                    peak = virtual_balance  # Update peak if a new high is reached
                current_drawdown = (peak - virtual_balance) / peak if peak > 0 else 0
                sim_max_drawdown = max(sim_max_drawdown, current_drawdown)

                # Check for violations
                if virtual_balance >= initial_balance * (1 + profit_target) and not condition_met:
                    logging.info(
                        f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}% [Target reached]"
                    )
                    condition_met = True
                if sim_max_drawdown >= max_overall_drawdown and not condition_met:
                    logging.info(
                        f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}% [Max DD reached]"
                    )
                    condition_met = True

                # Log the balance and drawdown for each trade
                logging.info(f"Trade {trade + 1} - Balance: {virtual_balance:.2f}, Drawdown: {current_drawdown * 100:.2f}%")

                # Store simulation data
                simulation_data["balances"].append(virtual_balance)
                simulation_data["risks"].append(current_risk)
                simulation_data["drawdowns"].append(current_drawdown)

            # logging.info(f"[Worst drawdown sim: {sim + 1}]: {sim_max_drawdown * 100:.2f}%")
            worst_drawdown_all_sims = max(worst_drawdown_all_sims, sim_max_drawdown)

            results.append(simulation_data)

        # Log the worst drawdown across all simulations
        logging.info(f"[All Sims] Worst drawdown: {worst_drawdown_all_sims * 100:.2f}%")

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


# Example usage
if __name__ == "__main__":
    # initial_balance = 50000
    # profit_target = 0.06
    # max_overall_drawdown = 0.06
    # risk_per_trade = 0.01
    # win_rate = 0.55
    # reward_to_risk = 2.0
    # trades_to_pass = 20
    # # the model risk controllers
    # increase_risk = 0.02
    # increase_check = initial_balance * 1.03
    # decrease_risk = 0.005
    # decrease_check = initial_balance * 0.99

    initial_balance = float(input("Enter initial balance: "))
    risk_per_trade = float(input("Enter risk per trade (as a decimal, e.g., 0.01 for 1%): "))
    win_rate = float(input("Enter win rate (as a decimal, e.g., 0.55 for 55%): "))
    reward_to_risk = float(input("Enter reward-to-risk ratio (e.g., 2.0): "))
    profit_target = float(input("Enter profit target (as a decimal, e.g., 0.06 for 6%): "))
    max_overall_drawdown = float(input("Enter max overall drawdown (as a decimal, e.g., 0.06 for 6%): "))
    trades_to_pass = int(input("Enter number of trades to simulate: "))
    increase_risk = float(input("Enter increased risk (as a decimal, e.g., 0.02 for 2%): "))
    increase_check = float(input("Enter increase check percentage (e.g., 0.03 for 3%): "))
    decrease_risk = float(input("Enter decreased risk (as a decimal, e.g., 0.005 for 0.5%): "))
    decrease_check = float(input("Enter decrease check percentage (e.g., 0.01 for 1%): "))

    results = run_simulation()
    if results:
        plotting(results)
    else:
        logging.error("No results to plot.")
