#!/usr/bin/env bash
# 配置分层（改动系统状态）。仅在专用测试主机运行，勿在生产执行。
# 默认 DRY-RUN 只打印将执行的动作；设 MTP_CONFIRM=1 才真正执行。
# 用法: [MTP_CONFIRM=1] setup-tiers.sh <baseline|nvme-swap|cxl-numa> [device]
#   nvme-swap 的 <device> 会被 mkswap 格式化，务必是专用分区！
set -euo pipefail
mode="${1:?用法: setup-tiers.sh <baseline|nvme-swap|cxl-numa> [device]}"
dev="${2:-}"
run() { echo "+ $*"; if [ "${MTP_CONFIRM:-0}" = "1" ]; then eval "$*"; fi; }
[ "${MTP_CONFIRM:-0}" = "1" ] || echo "== DRY-RUN：仅打印，设 MTP_CONFIRM=1 才执行 =="

case "$mode" in
  baseline)
    run "echo false > /sys/kernel/mm/numa/demotion_enabled"
    run "echo 0 > /proc/sys/kernel/numa_balancing"
    ;;
  nvme-swap)
    # NVMe 作 swap 慢层（Linux 上 NVMe 分层的实际形态，见 benchmark-plan.md 机制澄清）
    : "${dev:?nvme-swap 需指定专用 swap 分区，如 /dev/nvme0n1p2（会被格式化）}"
    run "mkswap $dev"
    run "swapon $dev"
    run "sysctl -w vm.swappiness=60"
    run "modprobe zswap 2>/dev/null || true"
    run "echo 1 > /sys/module/zswap/parameters/enabled"   # 可选 zswap 前端
    ;;
  cxl-numa)
    # CXL 作内存 NUMA 节点 + 开启内核内存分层（命令据 report.md 参考 [5]）
    command -v daxctl >/dev/null 2>&1 || { echo "需要 daxctl"; exit 1; }
    run "daxctl reconfigure-device --mode=system-ram ${dev:-all}"
    run "echo true > /sys/kernel/mm/numa/demotion_enabled"
    run "echo 2 > /proc/sys/kernel/numa_balancing"
    ;;
  *) echo "未知 mode: $mode"; exit 2 ;;
esac
echo "done: $mode"
