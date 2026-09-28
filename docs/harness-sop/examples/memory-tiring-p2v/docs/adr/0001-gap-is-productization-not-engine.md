# ADR-0001：差距定性为"产品化"而非"引擎"

- 状态：已接受（v4；纠正 v3）
- 日期：2026-09

## 背景

v3 曾断言"NVMe 上 Proxmox 与 VMware 是**机制差距**（缺主动分层引擎）"，并据此提出"换战场到 CXL"。
经 reverse-skill 对 v6.14 内核源码逐条核验：`DAMON_RECLAIM`(5.16)、`DAMOS pageout`（paddr，可按 memcg
过滤）、cgroup v2 `memory.reclaim` 已能**主动**把访问-冷页逐到 NVMe swap，与 VMware（recency+frequency、
4 KB、访问 page-in）同类；Meta TMO 更在机群规模验证了这条通路 [16][17]。

## 决策

把 Proxmox 与 VMware 的差距定性为 **产品化/集成差距**（默认配比与护栏、按 VM 策略面、DRS 式分层
感知放置、迁移/HA 协同、guest 透明、GUI），**不是分层引擎差距**。

## 备选

1. 维持 v3"机制差距"叙事——被内核源码证据证伪。
2. 认为完全无差距（纯包装）——过头：确有 promotion/大页/按 VM 治理等真实短板。

## 后果

- 超越路径从"造/换引擎"转为"**产品化内核已有机制**"，可靠贴内核快速补齐（见 ADR-0002）。
- MVP 从"swap 参数调优"升级为"按 VM DAMOS pageout 策略 + GUI + 护栏 + 迁移/HA 感知"（见 ADR-0003）。
- 难以逆转：叙事、控标条款、路线与客户话术都据此重写。
