# 对比测试执行方案 · Proxmox 内存分层

本方案把 [report.md](report.md) 第五节的"对比测试设计"细化为**可直接执行**的基准测试：具体负载、
参数矩阵、采集脚本与判定门，用于把报告里的**估算**在真实环境中验证为**实测**。脚本骨架在
[`scripts/`](scripts/)。

> 安全与合规：仅在**专用测试主机**运行，勿在生产环境执行；改动系统状态的脚本默认不执行，需显式
> 确认（见脚本内 `MTP_CONFIRM`）。所有命令随内核版本可能不同，以本机实际为准。

## 章节大纲

- 目的与验证对象
- 重要机制澄清（NVMe-swap 与 CXL-NUMA 不是一回事）
- 环境与前置
- 配置矩阵
- 负载
- 指标与采集
- 方法
- 预估与判定门
- 结果回填与价值兑现
- 参考

## 目的与验证对象

验证 report.md 的两条核心价值假设，并划出适用/不适用负载边界：

- **假设一**：慢层安全扩容不显著伤 SLO（关键负载 P99 增幅在可接受范围）。
- **假设二**：降低内存 TCO、提升单机密度（每 GB 成本下降、可用内存/VM 密度上升）。

## 重要机制澄清（NVMe-swap 与 CXL-NUMA 不是一回事）

这一点直接影响测试设计的正确性：

- **CXL/PMem 作慢层**：被内核视为**内存 NUMA 节点**，才是"真·内核内存分层"，由 TPP、DAMON、
  降级/提升、加权交织直接管理 [5][6][7]。
- **NVMe 作慢层**：NVMe 是**块设备**，在 Linux 上作慢层实为 **swap/zswap 承载**（可叠加 zram 前端），
  与内核内存分层是不同机制；这更接近 VMware 集成式 NVMe 分层要解决的问题，但实现路径不同 [1]。

因此矩阵里 NVMe 路径走 swap 栈、CXL 路径走 NUMA 分层栈，二者分别评估，不可混为一谈。

## 环境与前置

- 专用测试主机；记录 CPU、DRAM 容量/速率、NVMe 型号、（如有）CXL 设备与固件。
- 内核：较新的稳定内核（含 TPP/DAMON/加权交织；具体特性以本机 `/sys/kernel/mm/` 与 `/proc/vmstat`
  实际字段为准）。
- 工具：`numactl`、`numastat`、`daxctl`（CXL）、`fio`、`stress-ng`、以及负载工具（`redis` +
  `memtier_benchmark`、RocksDB `db_bench`、或 `YCSB`）。

## 配置矩阵

| 配置 | 慢层与机制 | 启用要点 |
|---|---|---|
| A 基线 | 纯 DRAM，无分层 | 关闭 demotion，`numa_balancing` 常规 |
| B NVMe-swap | NVMe 作 swap 慢层（可叠 zswap） | 建 swap on NVMe；调 `swappiness`；可选 zswap |
| C NVMe-swap 1:2 | 慢层容量加倍 | 同 B，改变 DRAM:慢层配比 |
| D CXL-NUMA（可选） | CXL 作内存 NUMA 节点 + 内核分层 | `daxctl --mode=system-ram`；`demotion_enabled=true`；`numa_balancing=2` [5] |
| 参照 VMware（可选） | 同硬件、同配比的 ESXi 分层 | 外部对照 [1] |

具体启用命令见 [`scripts/setup-tiers.sh`](scripts/setup-tiers.sh)。

## 负载

- **冷热分明（利于分层）**：RocksDB `db_bench`（大数据集 + 偏斜读），或 Redis + `memtier_benchmark`
  （大 keyspace + 长尾冷 key），或 `YCSB` Zipfian 分布。
- **均匀热/随机（反例边界）**：`stress-ng --vm` 随机访问，或指针追逐微基准，制造无冷热区分的压力。
- **超分场景**：并发起 N 台 VM，各带工作集，总量 > DRAM，观察整体密度与尾延迟。

## 指标与采集

| 指标 | 来源 |
|---|---|
| P99/P999 延迟、吞吐 | 负载工具自带输出 |
| 慢层访问占比、迁移量 | `/proc/vmstat` 的 `pgdemote_*`、`pgpromote_success`、`numa_pages_migrated`（字段以本机为准）|
| 内存压力 | `/proc/pressure/memory`（PSI）|
| 每节点内存分布 | `numastat`、`/sys/devices/system/node/node*/meminfo` |
| 迁移 CPU 开销 | 迁移相关内核线程 CPU 占用 |
| 每 GB 成本 | 由配置容量与市价推算（见 report.md [9][10]）|

采集见 [`scripts/collect-metrics.sh`](scripts/collect-metrics.sh)（只读快照，安全）。

## 方法

固定负载、变分层配置；每配置预热到稳态后采窗口数据，重复 ≥3 轮取中位；对照 A 基线**与**文献
基线（report.md 的估算）。测试主循环：

```mermaid
flowchart LR
    %% 基准测试主循环
    S1[1、选配置 A 至 D（Config）] --> S2[2、配置分层（setup-tiers）]
    S2 --> S3[3、预热（Warmup）]
    S3 --> S4[4、跑负载并采集（run-bench）]
    S4 --> S5[5、多轮取中位（Median）]
    S5 --> S6[6、对照基线与预估（Analyze）]
    S6 --> S7[7、价值回填报告（Backfill）]
```

## 预估与判定门

预估取自 report.md（据公开锚点，属预估非实测）；判定门是价值假设的通过标准：

| 对比 | 预估 | 判定门（通过标准）|
|---|---|---|
| B vs A（冷热分明）| 密度约 +80%〜+100% [1]；P99 增幅个位数〜低两位数 % [7]；内存成本约 −40%〜−45% [9][10] | P99 增幅 ≤ 约定 SLO 阈值，且成本下降 ≥ 20% |
| B vs A（均匀热/随机）| P99 显著上升（不适用边界）| 记录为不适用负载，不作达标要求 |
| D vs B（CXL）| 延迟更友好（CXL 约为 DRAM 2 倍 [11]）| CXL 路径 P99 优于 NVMe-swap |

## 结果回填与价值兑现

把实测中位值回填到 report.md 第七节"价值度量"表：将"估算"替换为"实测"，并对照判定门标注价值
是否兑现；未达标则回到价值假设或 MVP 方案修正（对应价值验证闭环）。这样完成"估算 → 实测"的最后
一公里。

## 参考

引用编号与 report.md 一致：VMware 机制 [1]；Linux 内核分层机制与开关 [5]；加权交织 [6]；DAMON 收益
[7]；成本数据 [9][10]；CXL 延迟 [11]；内核在研工作 [12]。完整链接见 [report.md](report.md) 参考资料。
