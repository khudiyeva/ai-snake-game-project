#!/usr/bin/env python3
"""
Train the DQN RL agent for the Snake game.

Usage:
    python snake_ai_project/train_rl.py
    python snake_ai_project/train_rl.py --episodes 1000

The trained model is saved to snake_ai_project/models/rl_model.pth.
After training, run the agent with:
    python snake_ai_project/main.py --mode rl
"""
from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

import numpy as np

# Ensure snake_ai_project/ is on the path so sibling packages resolve correctly.
sys.path.insert(0, str(Path(__file__).parent))

import torch
import torch.nn as nn
import torch.optim as optim

from agents.rl_env import SnakeEnv
from agents.rl_model import QNetwork, ReplayBuffer

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "rl_model.pth"

# ── Hyperparameters ──────────────────────────────────────────────────────────
LR = 0.001
GAMMA = 0.9
BATCH_SIZE = 1000
MEMORY_SIZE = 100_000
EPSILON_START = 1.0
EPSILON_END = 0.01
TARGET_SYNC_STEPS = 100   # copy policy → target every N gradient steps
MIN_MEMORY = 1_000        # don't train until this many transitions are stored
# ─────────────────────────────────────────────────────────────────────────────


def train(episodes: int) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[RL] Training on {device} for {episodes} episodes")
    print(f"[RL] Model will be saved to {MODEL_PATH}\n")

    env = SnakeEnv()

    policy_net = QNetwork().to(device)
    target_net = QNetwork().to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    memory = ReplayBuffer(maxlen=MEMORY_SIZE)

    epsilon = EPSILON_START
    epsilon_decay = (EPSILON_START - EPSILON_END) / max(episodes - 1, 1)

    total_steps = 0
    recent_scores: deque[int] = deque(maxlen=100)
    best_mean = -float("inf")

    for episode in range(1, episodes + 1):
        obs = env.reset()
        done = False

        while not done:
            # ε-greedy action selection
            if np.random.rand() < epsilon:
                action = np.random.randint(0, 3)
            else:
                with torch.no_grad():
                    t = torch.from_numpy(obs).unsqueeze(0).to(device)
                    action = int(policy_net(t).argmax(dim=1).item())

            next_obs, reward, done = env.step(action)
            memory.push(obs, action, reward, next_obs, done)
            obs = next_obs

            # Train when enough experience has been collected
            if len(memory) >= MIN_MEMORY:
                states, actions, rewards, next_states, dones = memory.sample(BATCH_SIZE)

                s  = torch.from_numpy(states).to(device)
                a  = torch.from_numpy(actions).to(device)
                r  = torch.from_numpy(rewards).to(device)
                ns = torch.from_numpy(next_states).to(device)
                d  = torch.from_numpy(dones).to(device)

                current_q = policy_net(s).gather(1, a.unsqueeze(1)).squeeze(1)
                with torch.no_grad():
                    max_next_q = target_net(ns).max(1).values
                    target_q = r + GAMMA * max_next_q * (1.0 - d)

                loss = nn.functional.mse_loss(current_q, target_q)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_steps += 1
                if total_steps % TARGET_SYNC_STEPS == 0:
                    target_net.load_state_dict(policy_net.state_dict())

        epsilon = max(EPSILON_END, epsilon - epsilon_decay)
        recent_scores.append(env.score)
        mean_score = sum(recent_scores) / len(recent_scores)

        if episode % 100 == 0:
            print(
                f"  Episode {episode:5d}/{episodes} | "
                f"Score: {env.score:3d} | "
                f"Mean(last 100): {mean_score:5.1f} | "
                f"ε: {epsilon:.3f}"
            )

        # Save whenever the 100-episode mean improves (after warm-up)
        if len(recent_scores) == 100 and mean_score > best_mean:
            best_mean = mean_score
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            torch.save(policy_net.state_dict(), MODEL_PATH)

    # Always write the final weights so the file exists even during early runs
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(policy_net.state_dict(), MODEL_PATH)

    print(f"\n[RL] Training complete.")
    print(f"[RL] Best mean score (100-ep window): {best_mean:.1f}")
    print(f"[RL] Model saved to: {MODEL_PATH}")
    print(f"\nRun the agent:  python snake_ai_project/main.py --mode rl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the Snake DQN agent")
    parser.add_argument(
        "--episodes",
        type=int,
        default=500,
        help="Number of training episodes (default: 500)",
    )
    args = parser.parse_args()
    train(args.episodes)
