# Comparing Packet Filtering Policies in a Controlled Linux Network

CPTS 555, Computer Networks and Security, Washington State University.

We compare `nftables` packet filtering policies in an isolated lab network. We send legitimate and suspicious traffic through a Linux firewall and measure:

- how much suspicious traffic is blocked
- how much legitimate traffic is blocked by mistake
- the impact on network performance

The lab runs as 4 Docker containers on 2 isolated networks, so it works the same on macOS and on Windows (WSL2).

## Lab network

| Node | Role | Client network `10.0.1.0/24` | Server network `10.0.2.0/24` |
|---|---|---|---|
| `legit` | Legitimate client | `10.0.1.10` | — |
| `susp` | Suspicious client | `10.0.1.20` | — |
| `fw` | Linux firewall (`nftables`) | `10.0.1.1` (eth1) | `10.0.2.1` (eth2) |
| `server` | HTTP/HTTPS, DNS, SSH | — | `10.0.2.10` |

All traffic between the clients and the server goes through `fw`. The lab networks have no internet access.

## Repository layout and owners

| Folder | Owner | Content |
|---|---|---|
| `infra/` | Role 1: Environment and automation | Docker testbed (compose file, images) |
| `automation/` | Role 1: Environment and automation | Experiment runner, policy loader, config |
| `traffic/` | Role 2: Traffic generation | `legitimate/`, `suspicious/`, `scenarios/` |
| `policies/` | Role 3: Filtering policies | One `.nft` file per policy |
| `analysis/` | Role 4: Measurement and analysis | Parsers, metrics, plots |
| `results/` | Role 4: Measurement and analysis | `raw/` is generated and git-ignored |

## What is implemented

| Part | Status |
|---|---|
| Repository skeleton | Done |
| Conventions and Git workflow | Not yet |
| Docker testbed | Not yet |
| Firewall and server setup | Not yet |
| Client tools | Not yet |
| Experiment runner | Not yet |
| Makefile and full setup guide | Not yet |

## How to run

Not available yet. The testbed is coming in the next steps. This section will explain how to start it on macOS and on Windows (WSL2).

## Working together without conflicts

1. **Work only in your own folder** (see the table above). If you need a change in someone else's folder, open an issue or ask the owner.
2. **Never push to `main`.** Create a branch named `role<N>/<short-topic>`, for example `role2/syn-scan`.
3. **Keep pull requests small**, one topic each. Update your branch from `main` before you open one.
4. **The owner of the folder reviews the pull request** (enforced by `.github/CODEOWNERS`).
5. **Never commit** packet captures (`*.pcap`), `results/raw/`, or secrets.

The detailed Git workflow will be in `CONTRIBUTING.md`, and the interface contracts between roles will be in `docs/conventions.md` (coming soon).
