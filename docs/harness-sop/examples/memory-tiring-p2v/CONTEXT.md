# CONTEXT.md · 内存分层对标案例术语表（glossary）

本文件是本案例的领域术语表，由 `grilling → domain-modeling` 产出并按 v4（已核验）口径校准。它只放
**术语与定义**，不放实现细节或规格；决策见 [`docs/adr/`](docs/adr/)。

| 术语 | 定义（v4 校准）|
|---|---|
| 慢层通路（NVMe-swap / CXL-NUMA）| 组织本案例一切判断的轴：慢层要么是经 swap 访问的块设备（NVMe），要么是经页迁移访问的无 CPU 内存 NUMA 节点（CXL/PMem）。两条通路机制不同，须分别评估。|
| 主动 vs 被动分层 | **按可寻址性而非触发方式区分**（v4 纠正）：两条通路都有*主动*逐冷机制。NVMe：`DAMOS pageout`/`DAMON_RECLAIM`/`memory.reclaim` 主动逐冷，访问需主缺页换入。CXL：TPP/DAMON 迁移，页保持字节可寻址、访问不缺页。|
| DAMON / DAMOS | DAMON：内核访问监控（区域采样 `nr_accesses`）。DAMOS：对冷热区域施加动作的方案；动作含 `pageout`（到 swap）与 `migrate_hot/cold`（到 NUMA 层）。6.14：迁移动作仅 `paddr` 支持；`vaddr` 要 6.17。|
| DAMON_RECLAIM | 内核 5.16 起的主动、轻量回收模块：找访问-冷区域并在压力前逐出到 swap。是"NVMe 主动逐冷"的关键证据。|
| memcg 过滤 | DAMOS(paddr) 可按内存 cgroup 过滤，从而把策略**限定到单台 VM** 的 `qemu.slice/<vmid>.scope`。按 VM 分层今 6.14 即可落地的路径。|
| TPP | "透明页放置"：reclaim 时降级 + hint-fault 提升。**上游代码主要由 Intel 提交**（Dave Hansen 5.15 降级、Huang Ying 6.1 提升/显式层）；"TPP"是 Meta 论文命名。|
| 降级 / 提升（demotion/promotion）| 降级=回收路径把冷页迁到更低内存层（reclaim 触发）；提升=NUMA hint-fault 把热页迁回快层（6.1）。|
| 加权交织（MPOL_WEIGHTED_INTERLEAVE，6.9）| 按节点权重分摊分配以**聚合带宽**的 mempolicy，**不是冷页下沉机制**。勿用于容量型分层。|
| 产品化差距 | v4 定性的真正差距：不在分层"引擎"（两通路内核都有主动机制），而在集成默认、按 VM 策略面、DRS 式分层感知放置、迁移/HA 协同、guest 透明、GUI 与护栏。|
| 结构性护城河 | VMware 结构上难以复制的差异，本案例仅两条成立：**开源/AGPL**（可审计、可 fork、无锁定）与**无按核授权 TCO**。CXL、自调优 VMware 可跟随，不算结构性。|
| CXL 期权 | 把 CXL 原生分层当"随内核成熟推进的时机领先与期权"，而非近期主打或结构性超越；其成本论不成立（CXL $/GB ≥ DIMM，DRAM 涨价同抬）。|
| promotion-rate | MDK 口径的 SLO 代理指标；6.14 经 DAMOS `user_input` 目标反馈（`node_mem_*_bp` 要 6.16）。源自未核验的 [8]。|
| 密度 | 相对纯 DRAM，靠慢层超分多装的 VM 数（或每 VM 内存成本）；基线须含 PVE 既有的 balloon/KSM/free-page-reporting/virtio-mem，不可只对纯 DRAM。|
| 控标条款 | 招标建议评估语言（内核原生可审计 / 按 VM 策略 / CXL-ready / 不得按核订阅解锁 / 自主可控），只此架构满足；非事实断言、不构成幻觉。真实控标**案例**则"无法确定"。|
| kill-gate / 决策门 | 带数值阈值的门（启用 <30 分钟、config E 对 ESXi P99 差距 ≤ +15%、密度 ≥ +50%、迁移 ≤ 2× 基线）。**分通路分门**：M1 判 NVMe，CXL 门在 M3 单独判。|
| 信创（限定）| 需国产 CPU（鲲鹏/飞腾/龙芯/海光/兆芯）+ 国产 OS（麒麟/统信，内核 5.10/6.6）；"内核 6.14+ 分层"链条不转移，多无 CXL、CoCo 受限。现实可及仅 x86 信创、无 CXL、非 CoCo 子集。|
| CoCo（SEV-SNP/TDX）| 机密计算 VM，内存 host 不可读且钉住，**不能被 host swap 或迁移**——对分层是硬边界。|
| TMO | Meta《Transparent Memory Offloading》(ASPLOS'22)：机群规模用 PSI 主动把冷页 offload 到 swap，是 NVMe 主动分层的生产级证据。|
