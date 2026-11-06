# Integration and arm definitions

The existing RPent tree and implementation are preserved. The selected behavior is in `robots/libero/flash/replay.py` and documented in [ADAPTIVE_FLASH.md](../ADAPTIVE_FLASH.md). Its focused tests remain in `tests/unit_tests/robots/libero/test_adaptive_replay.py`.

Use the original RPent setup and frozen local policy/perception servers. Existing memory replay is different from generating new memory using a paid planner. Do not enable a GPT planner or memory-generation workflow without separate authorization. Pin the memory release and set the strict per-suite physical limit explicitly. Source integrity checks in this publication validate the added export files; they do not hash the complete upstream RPent tree.
