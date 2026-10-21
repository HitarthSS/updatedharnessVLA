# Updated HarnessVLA：RPent 自适应 Flash

[English](README.md) · [完整算法与复现指南](ADAPTIVE_FLASH.md)

本仓库包含 HitarthSS 对 [RLinf/RPent](https://github.com/RLinf/RPent) 中
LIBERO Flash 的实验改进。RPent 是 [Harness VLA](https://arxiv.org/abs/2607.08448)
使用的框架。本分支冻结机器人策略，改进发布动作计划的视觉定位与抓取失败恢复。

**评测状态：**已有离线回归测试。初始仿真运行使用 RPent 默认的 10,000 个动作，
不能证明在基准参考时域内优于原方法，也不宣称已实现端到端加速。

## 改进内容

- 跳过未连接到有效运动指令的视觉锚点。在检查过的 78 个发布计划中，
  27 个计划包含未使用的锚点，共可减少 206 个锚点中的 42 个。
  这是定位工作量的减少，不是实际耗时测量。
- 抓取失败后，用最新观测与原有 SAM3 或 Molmo 定位器重新定位接近路径的锚点。
  只平移接近动作，保留高度与姿态；拒绝无效读数、超过 8 厘米的偏移和不可达目标。
- 保留每次任务最多三次抓取尝试，不重置环境。首次成功不增加恢复定位调用。

输入为发布计划、RGB-D 图像与标定、机器人状态和抓取反馈。
不训练新策略，也不使用仿真器物体真值位姿。

## 模型与运行

使用冻结的 Pi0.5、SAM3、Molmo2-8B 和公开的 `RLinf/RPent-memory` 计划。
计划由上游 GPT-5.5 生成；使用 `--planner flash` 重放不需要新的 GPT、Claude
或 Codex 规划调用。固定版本及未记录的 SAM3 下载版本见[模型清单](ADAPTIVE_FLASH.md#models-and-memory)。

需要 Linux、NVIDIA GPU、LIBERO-PRO 资源和模型权重：

```bash
git clone https://github.com/HitarthSS/updatedharnessVLA.git
cd updatedharnessVLA
```

先按 [LIBERO 安装指南](docs/source-zh/rst_source/simulators/libero.rst)准备仿真器与
Pi0.5/SAM3，再按[完整运行步骤](ADAPTIVE_FLASH.md#run)单独安装 Molmo、启动服务，
并用 `--planner flash` 和显式的 `--max-episode-steps` 运行。

| 套件类别 | 原生仿真动作上限 |
| --- | ---: |
| Spatial | 220 |
| Object | 280 |
| Goal | 300 |
| Long | 520 |

这些上限不是实际秒数。1.5 倍时域应单独报告。与原 Flash 比较时，保持模型、冻结计划、
任务、seed 和动作预算一致；原实现对应提交 `945682a55c4e17d6bb686a80b162ff801e768157`。

成功应根据原生环境信号判定，并保留错误与不可用案例。初始运行 seed 为 0–9，
论文为 1–10；已安装资源中有三个空初始状态文件，发布语料缺少两个完整 Flash 计划。
共享 GPU 也会影响耗时比较。参见[评测限制](ADAPTIVE_FLASH.zh-CN.md#评测要求)。

## 代码与验证

实现位于 [robots/libero/flash/replay.py](robots/libero/flash/replay.py)，
新增测试位于 [test_adaptive_replay.py](tests/unit_tests/robots/libero/test_adaptive_replay.py)。
安装测试依赖后执行：

```bash
python -m pytest tests/unit_tests/robots/libero \
  tests/unit_tests/rpent/planner/test_api_contracts.py -q
```

开发时的定向检查通过了 174 项测试。测试验证软件行为，不能替代基准结果。

## 范围与来源

基于 RPent 提交 `945682a55c4e17d6bb686a80b162ff801e768157`，保留上游源代码、文档、
历史、作者信息和 [Apache-2.0 许可证](LICENSE)。上游排行榜页面描述上游结果。
原项目概览见[基础版本的上游 README](https://github.com/RLinf/RPent/blob/945682a55c4e17d6bb686a80b162ff801e768157/README.zh-CN.md)。
发布内容不包含实验队列、密钥、模型权重、日志、视频或生成的覆盖率数据。
HexaShell 与 RoboHarness 实验属于其他项目。详见[中文算法说明](ADAPTIVE_FLASH.zh-CN.md)。
