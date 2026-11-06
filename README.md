# My harness for Harness VLA / RPent Flash

Experimental, frozen-policy harness code for the [paper](https://arxiv.org/abs/2607.08448). The evaluated behavior is in [`robots/libero/flash/replay.py`](robots/libero/flash/replay.py). Original authorship and source are credited in [NOTICE.md](NOTICE.md).

## Results

| Reference | Result |

| --- | --- |

| Paper / official release | Flash Mode (max): 581/800 (72.63%), retrospective best-card selection |

| Our run of the authors' harness | Historical raw sweep: 292/660 (44.24%) |

| **My harness** | **Historical raw sweep: 362/750 (48.27%)** |


Historical single-card LIBERO-PRO replay sweeps with unequal executed coverage; these rates are not a matched improvement comparison.


These are reduced or explicitly qualified experiments. They do not establish full-paper reproduction or a confirmed benchmark win. See [evaluation details](EVALUATION.md) and the provenance in [provenance/](provenance/).

## What my harness changes

1. Skip perception anchors that are not attached to any executed motion.

2. After a failed grasp, re-localize its approach anchor with the same SAM3 or Molmo locator.

3. Bound translations to 8 cm, preserve orientation and the original three-attempt limit, and add no recovery query after a successful first grasp.


Categories: `observation_grounding`, `execution_monitoring`, `uncertainty_compute`.

## Models and inputs

- RLinf Pi0.5 LIBERO-130 SFT, SAM3 and allenai/Molmo2-8B; all frozen.

- Released RLinf/RPent-memory at 47f301ef33bf8d0e8c770342f16b3c39c6a0e8c1, libero/GPT_5.5_xhigh. Replaying these files makes no new GPT call.


Policy weights remain frozen. Model checkpoints and benchmark assets must be obtained from their original releases under their own access terms. No paid LLM/VLM API is required by the published variant.

## Start here

1. Use a Linux GPU host for simulator/model evaluation. Read the [pinned upstream setup](https://github.com/RLinf/RPent) before installing its model stack.
2. Controller dependency: Use the RPent LIBERO extras documented in ADAPTIVE_FLASH.md.
3. Inspect `configs/method.json` and `provenance/upstream.json`.
4. Verify the source-only export and inspect the core API:

```sh
python3 tools/verify_export.py
pytest tests/unit_tests/robots/libero tests/unit_tests/rpent/planner/test_api_contracts.py -q
```


CPU checks validate code behavior or packaging only. They do not run the robot benchmark or demonstrate numerical parity on a new GPU/runtime.

## Integrate with the frozen policy

Read [the integration contract and arm definitions](docs/INTEGRATION.md).

Use the existing RPent CLI with --planner flash, the pinned memory and model services, plus an explicit --max-episode-steps for the chosen suite. See ADAPTIVE_FLASH.md for complete commands.


The core harness is reusable. Integration snapshots and historical experiment drivers are included for inspection; full fresh-machine simulator reproduction has not been revalidated during this publication. Prepare the pinned native environment and required assets before using those drivers. No benchmark is automatically launched by cloning, importing, or verifying this repository.

## Evaluation budget

Original sweeps inherited a 10,000-action guard. Strict reference caps are Spatial 220, Object 280, Goal 300 and Long 520; set them explicitly.


Use identical tasks, initial states, seeds, models and budgets for the authors' harness and my harness. Charge every executed recovery/intervention to the action limit. Separate development and final cases, freeze the design before evaluation, and report all completed matched cases.

## Repository map

- `robots/libero/flash/replay.py`: main harness behavior.
- `configs/`: method and evaluation metadata.
- `provenance/`: source/model pins and export hashes.
- `tools/verify_export.py`: offline source integrity check.
- `reference/`, `integration/`, or `experiments/`, when present: native-loop snapshots.

## Known limitations

- No aggregate benchmark improvement is established.

- Published max-card selection and our raw sweeps are different procedures.

- Missing state files/cards, seed differences, and unknown original SAM3 download revision remain documented gaps.

- The before/after video examples are outcome-selected illustrations, not an aggregate replication.


Shared-GPU wall-clock measurements are descriptive. New checkpoints, a new serving runtime, different seeds or changed horizon enforcement require a newly labeled comparison.

## Publication checks

Source syntax and recorded-core hashes checked. All exported Python parses, shell scripts pass `bash -n`, relative documentation links resolve, and source files pass a credential-pattern scan. See [validation](provenance/validation.json). A complete GPU benchmark was not rerun for this publication.
