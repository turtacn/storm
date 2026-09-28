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
  # 默认仅打印命令，避免误跑；取消下方注释并按机型调参即为实测。
  # 前置：须先用 host mem= 或 cgroup memory.high 压低 DRAM，逼出 swap/降级（见 benchmark-plan.md）。
  case "$1" in
    cold-heavy)
      echo "  cmd: memtier_benchmark --key-maximum=50000000 --key-pattern=G:G --ratio=1:4 --data-size=1024 --test-time=300"
      # memtier_benchmark --key-maximum=50000000 --key-pattern=G:G --ratio=1:4 --data-size=1024 --test-time=300
      ;;
    uniform-hot)
      echo "  cmd: stress-ng --vm 4 --vm-bytes 90% --vm-method all --timeout 300s"
      # stress-ng --vm 4 --vm-bytes 90% --vm-method all --timeout 300s
      ;;
    overcommit)
      echo "  逐台加 VM，直到任一 VM 破 P99 门或 host PSI-some 超阈值；记录 VM 数为密度"
      ;;
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
