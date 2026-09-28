#!/usr/bin/env bash
# 编排：对每个配置×负载，配置分层 → 预热 → 跑负载并采集 → 打标。
# 模板：负载命令为占位，请按 benchmark-plan.md 替换为实际工具调用。仅在专用测试主机运行。
# 用法: [MTP_CONFIRM=1] [MTP_DEV=/dev/nvme0n1p2] [REPEATS=3] run-bench.sh [outdir]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
outdir="${1:-./results}"
REPEATS="${REPEATS:-3}"
CONFIGS=("baseline" "nvme-swap" "cxl-numa")        # 按本机硬件删减
WORKLOADS=("cold-heavy" "uniform-hot" "overcommit")

run_workload() {
  case "$1" in
    cold-heavy)  echo "  TODO: 偏斜读负载，如 memtier_benchmark 或 RocksDB db_bench（占位）" ;;
    uniform-hot) echo "  TODO: 随机访问压力，如 stress-ng --vm（反例边界，占位）" ;;
    overcommit)  echo "  TODO: 并发起 N 台 VM，总工作集 > DRAM（占位）" ;;
  esac
}

for cfg in "${CONFIGS[@]}"; do
  echo "== 配置: $cfg =="
  MTP_CONFIRM="${MTP_CONFIRM:-0}" "$here/setup-tiers.sh" "$cfg" "${MTP_DEV:-}" || { echo "跳过 $cfg"; continue; }
  for wl in "${WORKLOADS[@]}"; do
    for i in $(seq 1 "$REPEATS"); do
      label="$cfg-$wl-r$i"
      "$here/collect-metrics.sh" "$label-pre" "$outdir" >/dev/null
      echo ">>> $label 预热..."
      echo ">>> $label 运行:"; run_workload "$wl"
      "$here/collect-metrics.sh" "$label-post" "$outdir" >/dev/null
      echo "  记录 -> $outdir/$label-*"
    done
  done
done
echo "完成。结果在 $outdir；对照 benchmark-plan.md 的判定门做分析，并回填 report.md 价值度量表。"
