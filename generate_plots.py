#!/usr/bin/env python3
"""
Generate EDA / analysis figures for the Snake AI project report.
Saves all figures to figures/ in the project root.

Usage:
    python generate_plots.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).parent / "snake_ai_project"))

OUT_DIR = Path(__file__).parent / "figures"
OUT_DIR.mkdir(exist_ok=True)

STYLE = {
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 150,
}
plt.rcParams.update(STYLE)

# ── Hardcoded checkpoint data from training_log.txt ──────────────────────────
EPS_500  = [100, 200, 300, 400, 500]
MEAN_500 = [0.5, 1.3, 2.1, 3.3, 9.4]
EPS_VALS_500 = [0.802, 0.603, 0.405, 0.206, 0.010]

EPS_1000  = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
MEAN_1000 = [0.3, 0.8, 1.4, 1.6, 2.0, 2.3, 2.3, 3.5, 6.0, 16.0]
EPS_VALS_1000 = [0.901, 0.802, 0.703, 0.604, 0.505, 0.405, 0.306, 0.207, 0.108, 0.010]

# ── In-game observed scores ───────────────────────────────────────────────────
OBSERVED_RL_500  = [374, 407]   # range across sessions
OBSERVED_RL_1000 = [289]
OBSERVED_ASTAR   = [884, 1302]

# ─────────────────────────────────────────────────────────────────────────────
# Figure 1 — Training learning curves (both runs)
# ─────────────────────────────────────────────────────────────────────────────
def fig_learning_curves() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)

    for ax, eps, means, label, color in [
        (axes[0], EPS_500,  MEAN_500,  "500 episodes", "#2196F3"),
        (axes[1], EPS_1000, MEAN_1000, "1000 episodes", "#E91E63"),
    ]:
        ax.plot(eps, means, marker="o", color=color, linewidth=2, markersize=6, label="100-ep mean score")
        ax.fill_between(eps, means, alpha=0.12, color=color)
        ax.set_title(f"DQN Training — {label}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Mean score (last 100 episodes)")
        ax.set_xlim(0, eps[-1] + eps[-1] * 0.05)
        ax.set_ylim(0)
        for x, y in zip(eps, means):
            ax.annotate(f"{y}", (x, y), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=8, color=color)

    axes[1].axvspan(700, 1000, alpha=0.07, color="#E91E63", label="Sharp improvement phase")
    axes[1].legend(fontsize=9)

    fig.suptitle("RL Agent Learning Curves", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    path = OUT_DIR / "fig1_learning_curves.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2 — Epsilon (exploration) decay
# ─────────────────────────────────────────────────────────────────────────────
def fig_epsilon_decay() -> None:
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(EPS_500, EPS_VALS_500, marker="s", color="#2196F3", linewidth=2,
            markersize=6, label="500-episode run", linestyle="--")
    ax.plot(EPS_1000, EPS_VALS_1000, marker="o", color="#E91E63", linewidth=2,
            markersize=6, label="1000-episode run")

    ax.axhline(0.01, color="gray", linewidth=1, linestyle=":", label="ε minimum (0.01)")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Exploration rate (ε)")
    ax.set_title("Epsilon-Greedy Exploration Decay", fontsize=13, fontweight="bold")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=10)

    # annotate exploitation zone
    ax.annotate("Exploitation\ndominates", xy=(900, 0.108), xytext=(650, 0.3),
                arrowprops=dict(arrowstyle="->", color="gray"),
                fontsize=9, color="gray", ha="center")

    fig.tight_layout()
    path = OUT_DIR / "fig2_epsilon_decay.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3 — Agent game score comparison
# ─────────────────────────────────────────────────────────────────────────────
def fig_score_comparison() -> None:
    fig, ax = plt.subplots(figsize=(8, 5))

    agents   = ["RL\n(500 ep)", "RL\n(1000 ep)", "A*"]
    midpoints = [np.mean(OBSERVED_RL_500), np.mean(OBSERVED_RL_1000), np.mean(OBSERVED_ASTAR)]
    lows      = [min(OBSERVED_RL_500), min(OBSERVED_RL_1000), min(OBSERVED_ASTAR)]
    highs     = [max(OBSERVED_RL_500), max(OBSERVED_RL_1000), max(OBSERVED_ASTAR)]
    colors    = ["#2196F3", "#E91E63", "#4CAF50"]

    bars = ax.bar(agents, midpoints, color=colors, alpha=0.8, width=0.5, zorder=3)

    # error bars showing observed range
    for i, (lo, hi, mid) in enumerate(zip(lows, highs, midpoints)):
        ax.errorbar(i, mid, yerr=[[mid - lo], [hi - mid]],
                    fmt="none", color="black", capsize=8, linewidth=2, zorder=4)

    for bar, val in zip(bars, midpoints):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{val:.0f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("In-game score", fontsize=11)
    ax.set_title("Agent Performance Comparison (In-Game Observed Scores)", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(highs) * 1.2)

    note = mpatches.Patch(color="none", label="Error bars = observed score range")
    ax.legend(handles=[note], fontsize=9)

    fig.tight_layout()
    path = OUT_DIR / "fig3_score_comparison.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 4 — Observation space schematic (what the RL agent sees)
# ─────────────────────────────────────────────────────────────────────────────
def fig_observation_space() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # ── Left: snake grid diagram ──────────────────────────────────────────────
    ax = axes[0]
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Agent's Local Observation", fontsize=12, fontweight="bold")

    # draw grid
    for x in range(6):
        ax.axvline(x, color="#ccc", linewidth=0.8)
    for y in range(6):
        ax.axhline(y, color="#ccc", linewidth=0.8)

    # snake body
    body = [(2, 2), (1, 2), (1, 3), (2, 3), (3, 3)]
    for bx, by in body[1:]:
        ax.add_patch(plt.Rectangle((bx, by), 1, 1, color="#90CAF9", zorder=2))
    # head
    hx, hy = body[0]
    ax.add_patch(plt.Rectangle((hx, hy), 1, 1, color="#1565C0", zorder=3))
    ax.text(hx + 0.5, hy + 0.5, "H", ha="center", va="center",
            color="white", fontweight="bold", fontsize=12, zorder=4)

    # food
    ax.add_patch(plt.Circle((3.5, 1.5), 0.35, color="#E53935", zorder=3))
    ax.text(3.5, 1.5, "F", ha="center", va="center",
            color="white", fontweight="bold", fontsize=10, zorder=4)

    # danger arrows (straight=right, right=down, left=up)
    danger_color = "#FF7043"
    ax.annotate("", xy=(4.1, 2.5), xytext=(3.0, 2.5),
                arrowprops=dict(arrowstyle="->", color=danger_color, lw=2))
    ax.text(4.15, 2.7, "danger\nstraight", fontsize=7, color=danger_color)

    ax.annotate("", xy=(2.5, 1.9), xytext=(2.5, 3.0),
                arrowprops=dict(arrowstyle="->", color="#FF9800", lw=2))
    ax.text(2.6, 1.75, "danger\nright", fontsize=7, color="#FF9800")

    ax.annotate("", xy=(2.5, 3.1), xytext=(2.5, 2.5),
                arrowprops=dict(arrowstyle="->", color="#9C27B0", lw=1.5))
    ax.text(2.6, 3.2, "danger\nleft", fontsize=7, color="#9C27B0")

    # food direction arrows
    ax.annotate("", xy=(3.2, 2.2), xytext=(3.0, 2.5),
                arrowprops=dict(arrowstyle="->", color="#4CAF50", lw=1.5, linestyle="dashed"))
    ax.text(3.35, 2.1, "food →\nfood ↓", fontsize=7, color="#4CAF50")

    # ── Right: feature vector bar chart ──────────────────────────────────────
    ax2 = axes[1]
    feature_names = [
        "danger straight", "danger right", "danger left",
        "heading left", "heading right", "heading up", "heading down",
        "food left", "food right", "food up", "food down",
    ]
    # example values for a snake heading right, food below-right, no immediate danger
    example_values = [0, 0, 0,  0, 1, 0, 0,  0, 1, 0, 1]
    colors_feat = (
        ["#FF7043"] * 3 +   # danger
        ["#1E88E5"] * 4 +   # heading
        ["#43A047"] * 4     # food
    )
    bars = ax2.barh(feature_names, example_values, color=colors_feat, alpha=0.85, height=0.6)
    ax2.set_xlim(0, 1.4)
    ax2.set_xlabel("Feature value (binary)")
    ax2.set_title("Example Observation Vector\n(heading right, food right & below)", fontsize=12, fontweight="bold")

    danger_p = mpatches.Patch(color="#FF7043", label="Danger bits (3)")
    heading_p = mpatches.Patch(color="#1E88E5", label="Heading bits (4)")
    food_p = mpatches.Patch(color="#43A047", label="Food direction bits (4)")
    ax2.legend(handles=[danger_p, heading_p, food_p], fontsize=9, loc="lower right")

    for bar, val in zip(bars, example_values):
        ax2.text(val + 0.02, bar.get_y() + bar.get_height() / 2,
                 str(val), va="center", fontsize=10, fontweight="bold")

    fig.suptitle("DQN Observation Space: 11 Binary Features", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = OUT_DIR / "fig4_observation_space.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 5 — RL score distribution from eval (100 greedy episodes, headless)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rl_score_distribution() -> None:
    try:
        import torch
        from agents.rl_env import SnakeEnv
        from agents.rl_model import QNetwork

        model_path = Path(__file__).parent / "snake_ai_project" / "models" / "rl_model.pth"
        model = QNetwork()
        model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
        model.eval()

        env = SnakeEnv()
        scores = []
        print("  Running 100 evaluation episodes for score distribution...")
        for _ in range(100):
            obs = env.reset()
            done = False
            while not done:
                with torch.no_grad():
                    t = torch.from_numpy(obs).unsqueeze(0)
                    action = int(model(t).argmax(dim=1).item())
                obs, _, done = env.step(action)
            scores.append(env.score)

        scores = np.array(scores)
        print(f"  RL eval: mean={scores.mean():.1f}, median={np.median(scores):.1f}, "
              f"max={scores.max()}, min={scores.min()}, std={scores.std():.1f}")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # histogram
        axes[0].hist(scores, bins=20, color="#E91E63", alpha=0.8, edgecolor="white", linewidth=0.5)
        axes[0].axvline(scores.mean(), color="#1a1a1a", linestyle="--", linewidth=2,
                        label=f"Mean = {scores.mean():.1f}")
        axes[0].axvline(np.median(scores), color="#555", linestyle=":", linewidth=2,
                        label=f"Median = {np.median(scores):.1f}")
        axes[0].set_xlabel("Score")
        axes[0].set_ylabel("Episode count")
        axes[0].set_title("RL Agent Score Distribution\n(100 greedy evaluation episodes)", fontweight="bold")
        axes[0].legend(fontsize=9)

        # sorted scores (performance profile)
        axes[1].plot(sorted(scores), color="#E91E63", linewidth=2)
        axes[1].fill_between(range(len(scores)), sorted(scores), alpha=0.15, color="#E91E63")
        axes[1].set_xlabel("Episode rank (sorted by score)")
        axes[1].set_ylabel("Score")
        axes[1].set_title("RL Agent Performance Profile\n(sorted scores)", fontweight="bold")

        stats_text = (f"n=100  mean={scores.mean():.1f}\n"
                      f"median={np.median(scores):.1f}  std={scores.std():.1f}\n"
                      f"min={scores.min()}  max={scores.max()}")
        axes[1].text(0.98, 0.05, stats_text, transform=axes[1].transAxes,
                     fontsize=9, ha="right", va="bottom",
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8))

        fig.tight_layout()
        path = OUT_DIR / "fig5_rl_score_distribution.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved {path}")

    except FileNotFoundError:
        print("  Skipping fig5: model file not found. Run train_rl.py first.")
    except ImportError as e:
        print(f"  Skipping fig5: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 6 — Reward structure
# ─────────────────────────────────────────────────────────────────────────────
def fig_reward_structure() -> None:
    fig, ax = plt.subplots(figsize=(8, 4))

    events = ["Eat apple", "Step toward food", "Step away from food", "Game over"]
    rewards = [10, 1, -1, -10]
    colors = ["#4CAF50", "#8BC34A", "#FF9800", "#F44336"]

    bars = ax.bar(events, rewards, color=colors, alpha=0.85, width=0.5)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_ylabel("Reward value")
    ax.set_title("DQN Reward Function", fontsize=13, fontweight="bold")

    for bar, val in zip(bars, rewards):
        offset = 0.3 if val >= 0 else -0.8
        ax.text(bar.get_x() + bar.get_width() / 2, val + offset,
                f"{val:+d}", ha="center", va="bottom" if val >= 0 else "top",
                fontsize=12, fontweight="bold")

    ax.set_ylim(-12, 12)
    fig.tight_layout()
    path = OUT_DIR / "fig6_reward_structure.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


if __name__ == "__main__":
    print("Generating figures...")
    fig_learning_curves()
    fig_epsilon_decay()
    fig_score_comparison()
    fig_observation_space()
    fig_rl_score_distribution()
    fig_reward_structure()
    print(f"\nAll figures saved to {OUT_DIR}/")
    print("Files:")
    for f in sorted(OUT_DIR.iterdir()):
        print(f"  {f.name}")
