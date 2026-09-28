#!/usr/bin/env bash
# 只读采集：为一次测试运行快照内存分层相关指标。安全，不改系统状态。
# 用法: collect-metrics.sh <label> [outdir]
# 说明: /proc/vmstat 等字段随内核版本不同，以本机实际为准。
set -euo pipefail
label="${1:-snapshot}"
outdir="${2:-./results}"
ts="$(date +%Y%m%d-%H%M%S)"
dst="$outdir/$label-$ts"
mkdir -p "$dst"

# 内核内存分层计数器（降级/提升/迁移；字段以本机为准）
# CXL 通路看 pgdemote/pgpromote/numa_pages_migrated；NVMe-swap 通路看 pswpin/pswpout/pgscan/pgsteal
grep -E 'pgdemote|pgpromote|numa_pages_migrated|numa_hint|pgmigrate|pswpin|pswpout|zswpin|zswpout|zswpwb|pgscan|pgsteal' /proc/vmstat \
  > "$dst/vmstat.txt" 2>/dev/null || echo "no tiering/swap counters in /proc/vmstat" > "$dst/vmstat.txt"
# 内存压力 PSI
cat /proc/pressure/memory > "$dst/psi-memory.txt" 2>/dev/null || echo "PSI not available" > "$dst/psi-memory.txt"
# NUMA 分布
if command -v numastat >/dev/null 2>&1; then numastat > "$dst/numastat.txt" 2>/dev/null || true
else echo "numastat missing" > "$dst/numastat.txt"; fi
# 每节点内存
for n in /sys/devices/system/node/node*/meminfo; do
  [ -r "$n" ] && { echo "== $n =="; cat "$n"; } >> "$dst/node-meminfo.txt" 2>/dev/null || true
done
# 按 VM 采集（cgroup v2 qemu.slice 作用域）——host 全局计数无法归因到单台 VM
for s in /sys/fs/cgroup/qemu.slice/*.scope/memory.stat; do
  [ -r "$s" ] && { echo "== $s =="; cat "$s"; } >> "$dst/per-vm-memory-stat.txt" 2>/dev/null || true
done
# 按 VM 内存压力（PSI）
for pr in /sys/fs/cgroup/qemu.slice/*.scope/memory.pressure; do
  [ -r "$pr" ] && { echo "== $pr =="; cat "$pr"; } >> "$dst/per-vm-memory-pressure.txt" 2>/dev/null || true
done
# DAMOS 方案统计（DAMON 迁移/pageout 的真实计量；若已配置 DAMON）
for st in /sys/kernel/mm/damon/admin/kdamonds/*/contexts/*/schemes/*/stats; do
  [ -d "$st" ] && { echo "== $st =="; grep -H . "$st"/* 2>/dev/null; } >> "$dst/damos-stats.txt" 2>/dev/null || true
done
# swap（NVMe-swap 路径关注）与总体内存
cat /proc/swaps > "$dst/swaps.txt" 2>/dev/null || true
free -m > "$dst/free.txt" 2>/dev/null || true
# 分层开关状态
{
  echo "demotion_enabled: $(cat /sys/kernel/mm/numa/demotion_enabled 2>/dev/null || echo n/a)"
  echo "numa_balancing:   $(cat /proc/sys/kernel/numa_balancing 2>/dev/null || echo n/a)"
  echo "swappiness:       $(cat /proc/sys/vm/swappiness 2>/dev/null || echo n/a)"
} > "$dst/knobs.txt"

echo "collected -> $dst"
