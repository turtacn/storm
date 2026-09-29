# 对标分析案例

本目录存放 `competitive-analysis` SOP 每次运行产出的**案例报告**。

- **命名建议**：`XXX-YYY-vs-ZZZ-YYYYMM.md`（方向-本方-对标-年月），例如
  `rag-检索增强-产品甲-vs-产品乙-202601.md`。
- **格式要求**：每份案例必须套用 [`../report-outline.md`](../report-outline.md) 的章节骨架，
  并整体符合 [`../../authoring/report-style-guide.md`](../../authoring/report-style-guide.md)
  与 Mermaid 附录（大纲先行、结论置后、表格对比、`[n]` 引注加参考资料、图表合规）。
- **硬约束**：调研全程无授权检索；所有事实与"控标经典案例"必须真实可核验，查不到写
  "无法确定"，严禁杜撰。

## 案例索引

- [memory-tiring-p2v](memory-tiring-p2v/report.md) — 内存分层方向 · Proxmox VE 对标 VMware
  vSphere 分析报告（附 [过程记录](memory-tiring-p2v/process-notes.md)、[可执行测试方案](memory-tiring-p2v/benchmark-plan.md) 与 [汇报幻灯 mt-v1.pptx](memory-tiring-p2v/mt-v1.pptx)）。这是 SOP 的首份
  真实案例，其过程复盘驱动了多轮 SOP 迭代（来源分级、开源吸收/闭源逆向、存疑与需确认、无实测估算
  与对比测试设计、上游视角、多 reviewer 对拍等）。幻灯由 python-pptx 生成为原生可编辑 PPTX，沿用
  fidelity-first 与防幻觉原则（表格/数字/引用为真实文本、估算显式标注）。另含
  [逆向消化摘要](memory-tiring-p2v/reverse-digest.md)——按
  [逆向学习地图](../reverse-learning-map.md) 对内存分层开源栈（linux/mm、QEMU CXL、ndctl、damo、
  numactl、pcm、分配器、模拟器）的源码级消化，含术语贴回函数与"论文增量"表。
