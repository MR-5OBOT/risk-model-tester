import logging
import random
import matplotlib.pyplot as plt

# Enable/Disable detailed trade logs
VERBOSE_LOGGING = False

logging.basicConfig(level=logging.INFO, format="%(message)s")

# Parameters
initial_balance = 100000
profit_target = 0.06
max_overall_drawdown = 0.03
risk_per_trade = 0.005
win_rate = 0.6
reward_to_risk = 1.5
n_trades = 10

# Dynamic risk
increase_risk = 0.01
increase_check = initial_balance * 1.02
decrease_risk = 0.005
decrease_check = initial_balance * 0.99


def risk_reducer(balance, current_risk):
    if balance >= increase_check:
        # logging.info(f"🔺 Risk increased to {increase_risk * 100:.2f}%")
        return increase_risk
    elif balance <= decrease_check:
        # logging.info(f"🔻 Risk reduced to {decrease_risk * 100:.2f}%")
        return decrease_risk
    return current_risk


def run_simulation():
    try:
        logging.info("🧪 Running Monte Carlo Simulations")
        logging.info("-" * 40)
        logging.info(f"   Initial Balance: ${initial_balance}")
        logging.info(f"   Profit Target: {profit_target * 100:.2f}%")
        logging.info(f"   Max Drawdown: {max_overall_drawdown * 100:.2f}%")
        logging.info(f"   Win Rate: {win_rate * 100:.2f}%")
        logging.info(f"   Reward/Risk: {reward_to_risk}")
        logging.info(f"   Number of Trades: {n_trades}")
        logging.info(f"   Risk per Trade: {risk_per_trade * 100:.2f}%")
        logging.info("-" * 40)

        num_simulations = 10
        results = []
        worst_drawdown_all_sims = 0

        for sim in range(num_simulations):
            logging.info(f"\n📊 Simulation {sim + 1}")
            virtual_balance = initial_balance
            current_risk = risk_per_trade
            peak = initial_balance
            max_dd = 0
            passed = False
            failed = False

            sim_data = {
                "balances": [virtual_balance],
                "risks": [current_risk],
                "drawdowns": [0],
            }

            for trade in range(n_trades):
                current_risk = risk_reducer(virtual_balance, current_risk)
                risk_amount = current_risk * initial_balance

                win = random.random() < win_rate
                if win:
                    profit = reward_to_risk * risk_amount
                    virtual_balance += profit
                else:
                    virtual_balance -= risk_amount

                if virtual_balance > peak:
                    peak = virtual_balance
                drawdown = (peak - virtual_balance) / peak if peak > 0 else 0
                max_dd = max(max_dd, drawdown)

                if VERBOSE_LOGGING:
                    logging.info(
                        f"Trade {trade + 1}: {'✅ Win' if win else '❌ Loss'} | Balance: ${virtual_balance:.2f} | DD: {drawdown * 100:.2f}%"
                    )

                if virtual_balance >= initial_balance * (1 + profit_target):
                    logging.info(
                        f"🎯 Profit target reached on trade {trade + 1} — ${virtual_balance:.2f}"
                    )
                    passed = True
                elif drawdown >= max_overall_drawdown:
                    logging.info(
                        f"⚠️ Drawdown limit reached on trade {trade + 1} — {drawdown * 100:.2f}%"
                    )
                    failed = True

                sim_data["balances"].append(virtual_balance)
                sim_data["risks"].append(current_risk)
                sim_data["drawdowns"].append(drawdown)

                if passed:
                    outcome = "✅ PASSED"
                elif failed:
                    outcome = "❌ FAILED"
                else:
                    outcome = "⏳ UNDETERMINED"

                logging.info(
                    f"🧾 Final Balance: ${virtual_balance:.2f} | Max DD: {max_dd * 100:.2f}% | {outcome}"
                )

            worst_drawdown_all_sims = max(worst_drawdown_all_sims, max_dd)
            results.append(sim_data)

        logging.info(
            f"\n📉 Worst Drawdown Across All Sims: {worst_drawdown_all_sims * 100:.2f}%"
        )

        return results

    except Exception as e:
        logging.error(f"🚨 Error occurred: {e}")


def plotting(results):
    logging.info("\n📈 Plotting Simulation Results")
    plt.style.use("dark_background")
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    ax.set_title("Risk Model Performance", color="grey", fontsize=20, pad=15)
    # ax.set_xlabel("Trade Number", color="grey", fontsize=12)
    # ax.set_ylabel("Balance", color="grey", fontsize=12)

    for data in results:
        ax.plot(data["balances"], alpha=0.8)

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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_linewidth(2)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_color("grey")
    ax.spines["left"].set_color("grey")
    ax.tick_params(axis="x", colors="grey", direction="inout", length=6, width=2)
    ax.tick_params(axis="y", colors="grey", direction="inout", length=6, width=2)

    ax.text(
        0.5,
        0.5,
        "@MR_5OBOT",
        fontsize=40,
        color="gray",
        alpha=0.12,
        ha="center",
        va="center",
        rotation=10,
        transform=ax.transAxes,
    )
    ax.legend()
    plt.savefig("risk_model_performance.png")
    plt.show()


if __name__ == "__main__":
    results = run_simulation()
    if results:
        plotting(results)
    else:
        logging.error("No results to plot.")
