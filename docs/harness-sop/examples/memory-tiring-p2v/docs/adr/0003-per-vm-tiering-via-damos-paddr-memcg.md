# ADR-0003：按 VM 分层用 DAMOS paddr + memcg 过滤，今 6.14 即可落地

- 状态：已接受（v4）
- 日期：2026-09

## 背景

MVP 需按 VM 施加分层策略。v3 的方案含 `set_mempolicy2`（经核验**不存在**于 6.14）、把 TPP/DAMON 画在
NVMe 上（错）、并优先建于"分层感知内存 cgroup"（尚未合入、两套竞争补丁）。

## 决策

按 VM 分层采用 **DAMOS(paddr) + memcg 过滤到 `qemu.slice/<vmid>.scope`**：NVMe 通路用 `pageout` 动作，
CXL 通路用 `migrate_hot/cold`（paddr）。这在**当前 6.14 即可落地**。控制面走 `PVE::API2::Qemu`
（qemu-server）+ GUI，按 VM 键写入 `/etc/pve/qemu-server/<vmid>.conf`。

## 备选

1. `set_mempolicy2`——不存在；加权交织实际经 `mbind`/`set_mempolicy` + sysfs 权重。
2. 依赖未合入的"分层感知内存 cgroup"——作演进方向，不作 MVP 前提。
3. host-global 分层无按 VM——达不到 CSP 的多租户/按 VM 诉求。

## 后果

- 避免把 guest RAM `policy=bind` 到慢层节点（会使其永不"misplaced"、提升永不触发）。
- 观测按 VM：DAMOS `stats` + `qemu.slice/<vmid>.scope/memory.{stat,pressure}`；NVMe 看 `pswpin/out`
  （及 zswap 时 `zswp*`），DAMON 迁移看 `pgmigrate_*`（不进 `pgpromote/pgdemote`）。
- `memtier:` 成为 `qemu-server` 永久兼容面（schema/备份/迁移），须走 Proxmox 上游评审（见报告"存疑"）。
- vaddr 上的 DAMON 迁移要 6.17（PVE 9.1+）；6.14 用 paddr。
