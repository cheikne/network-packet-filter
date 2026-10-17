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
| Rules between roles (below) | Done |
| Docker testbed (4 nodes, 2 isolated networks) | Done |
| Firewall routing, server services, connectivity test | Done |
| Client tools | Not yet |
| Experiment runner | Not yet |
| Makefile and full setup guide | Not yet |

## Rules between roles

Follow these so everyone's parts fit together. Inside your own folder, do what you want.

- **Network:** use the names and IPs from the table above. On `fw`, `eth1` is the client side and `eth2` is the server side. The repository is mounted at `/project` in every container.
- **Policies (Role 3):** one file per policy, `policies/<name>.nft`. It starts with `flush ruleset` and puts rate thresholds as variables at the top. It is loaded with `automation/apply_policy.sh <name>`. Do not hard-code the `legit` or `susp` addresses.
- **Traffic scripts (Role 2):** runnable from the command line with `--target`, `--duration`, and `--output <dir>` (plus `--rate` when relevant). Each script writes its log into the output folder.
- **Results (Role 1 → Role 4):** each run creates `results/raw/<run_id>/` with `metadata.json`, the captures from `fw` (`m1.pcap` client side, `m2.pcap` server side), firewall counters, client logs, and server logs. Run ID format: `<date>-<time>_<config>_<scenario>_r<NN>`.
- **Official measurements** are done on one machine only, so performance numbers can be compared.

## How to run

You need Docker Desktop (macOS, or Windows with a WSL2 Ubuntu terminal).

```sh
cd infra
cp .env.example .env          # once; edit it to choose clients and resources
docker compose up -d --build  # start the lab
docker exec -it fw bash       # open a shell on a node (fw, server, legit, susp)
docker compose down           # stop the lab
cd .. && ./infra/tests/connectivity.sh   # check the lab (all lines must say PASS)
```

`fw` starts with no rules (Baseline). Services on `server` (`10.0.2.10`):

| Service | How to reach it |
|---|---|
| HTTP / HTTPS | `http://10.0.2.10/`, `https://10.0.2.10/` (self-signed, use `curl -k`), large file `/large.bin` |
| DNS | `dig @10.0.2.10 server.lab` (also `www.lab`) |
| SSH | user and password from `LAB_SSH_USER` / `LAB_SSH_PASSWORD` in `infra/.env` (ask the team for the shared values) |

Server logs (nginx, dnsmasq, sshd) are in `/var/log/lab/` on `server`.

## Working together without conflicts

1. **Work only in your own folder** (see the table above). If you need a change in someone else's folder, open an issue or ask the owner.
2. **Never push to `main`.** Create a branch named `role<N>/<short-topic>`, for example `role2/syn-scan`.
3. **Keep pull requests small**, one topic each. Update your branch from `main` before you open one.
4. **The owner of the folder reviews the pull request** (enforced by `.github/CODEOWNERS`).
5. **Never commit** packet captures (`*.pcap`), `results/raw/`, or secrets.
