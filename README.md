# Updated HarnessVLA: Adaptive Flash for RPent

[简体中文](README.zh-CN.md) · [Implementation and reproduction guide](ADAPTIVE_FLASH.md)

This repository contains HitarthSS's experimental improvements to the LIBERO
Flash harness in [RLinf/RPent](https://github.com/RLinf/RPent), the framework
behind [Harness VLA](https://arxiv.org/abs/2607.08448). It keeps the robot policy
frozen and changes how released action plans use perception and recover from
failed grasps.

**Evaluation status:** the implementation has offline regression coverage.
Initial simulator runs used RPent's 10,000-action default, so they do not establish
an improvement under the benchmark's reference horizons. No benchmark-beating
success rate or measured end-to-end speedup is claimed.

## What changed

- **Skip unused anchors:** localize only visual anchors attached to valid motion
  commands. In the inspected released corpus, this removes 42 of 206 surveyed
  anchors across 27 of 78 plans. This is a reduction in localization work, not a
  measured runtime improvement.
- **Refresh failed grasp approaches:** after a failed pick, re-localize its
  approach anchor using the latest observation and the original SAM3 or Molmo
  locator. Translate the approach while preserving height and orientation.
  Reject invalid readings, shifts over 8 cm, and unreachable targets.
- **Keep the original retry budget:** at most three pick attempts, within the
  same episode. A successful first pick adds no recovery perception query.

The change uses released plans, RGB-D observations and calibration, robot state,
and grasp feedback. It requires no policy training or simulator object-pose truth.

## Models and inference

The experiment uses frozen **Pi0.5**, **SAM3**, and **Molmo2-8B**, together with
released `RLinf/RPent-memory` plans. The released plans were generated upstream
with GPT-5.5; replaying them with `--planner flash` makes no new GPT, Claude, or
Codex planner calls. Model revisions and the unrecorded SAM3 download revision
are documented in [the model manifest](ADAPTIVE_FLASH.md#models-and-memory).

## Set up and run

Use a Linux machine with NVIDIA GPUs, the LIBERO-PRO assets, and the model
checkpoints. Start with this checkout:

```bash
git clone https://github.com/HitarthSS/updatedharnessVLA.git
cd updatedharnessVLA
```

Follow the included [LIBERO installation guide](docs/source-en/rst_source/simulators/libero.rst)
for the simulator and Pi0.5/SAM3 environment. Then follow the
[Adaptive Flash run instructions](ADAPTIVE_FLASH.md#run) to install Molmo in its
separate environment, start its service, and execute an episode with
`--planner flash` and an explicit `--max-episode-steps`.

Use the suite's reference simulator-action budget:

| Suite family | Maximum actions |
| --- | ---: |
| Spatial | 220 |
| Object | 280 |
| Goal | 300 |
| Long | 520 |

These limits count native simulator actions, not wall-clock time. A 1.5× budget
is a separate experimental condition. Compare the original harness and this
variant using identical models, frozen plans, tasks, seeds, and action budgets.
Use upstream commit `945682a55c4e17d6bb686a80b162ff801e768157` for the original
Flash implementation.

Report success from the native environment signal, retain errors and unavailable
cases, and report actual coverage. Initial runs used seeds 0–9 rather than the
paper's 1–10; the installed assets also had three empty initial-state files and
two missing complete Flash plans. See the
[evaluation limitations](ADAPTIVE_FLASH.md#horizon-and-evaluation-limitations)
before comparing against published numbers. Shared GPU contention also limits
latency comparisons.

## Code and tests

| Path | Purpose |
| --- | --- |
| [robots/libero/flash/replay.py](robots/libero/flash/replay.py) | Adaptive replay implementation |
| [tests/unit_tests/robots/libero/test_adaptive_replay.py](tests/unit_tests/robots/libero/test_adaptive_replay.py) | Offline regression tests |
| [ADAPTIVE_FLASH.md](ADAPTIVE_FLASH.md) | Algorithm, pinned assets, service commands, and evaluation protocol |
| [docs/](docs/) | Retained upstream setup and framework documentation |

With the test dependencies installed, run:

```bash
python -m pytest tests/unit_tests/robots/libero \
  tests/unit_tests/rpent/planner/test_api_contracts.py -q
```

The focused development check passed 174 tests. Unit tests verify software
behavior; they do not establish benchmark performance.

## Scope and attribution

This is an RPent-based research fork, based on upstream commit
`945682a55c4e17d6bb686a80b162ff801e768157`. The original framework source,
documentation, license, and commit history are retained; upstream leaderboard
pages describe upstream results. The original project overview remains available
in the [upstream README at the base revision](https://github.com/RLinf/RPent/blob/945682a55c4e17d6bb686a80b162ff801e768157/README.md).
Changes made here are described above and in
[ADAPTIVE_FLASH.md](ADAPTIVE_FLASH.md).

The published source excludes experiment queues, credentials, model weights,
logs, videos, and generated coverage data. HexaShell and RoboHarness experiments
are separate projects. RPent's original authorship and [Apache-2.0 license](LICENSE)
are preserved.
