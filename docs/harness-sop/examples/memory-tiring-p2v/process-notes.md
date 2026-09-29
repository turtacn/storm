# 过程记录与复盘 · memory-tiring-p2v

本文件记录用 `competitive-analysis` SOP 跑 Proxmox 对标 VMware（内存分层方向）这一真实案例的
过程，重点是**暴露的摩擦点**，作为 SOP 证据驱动迭代的依据（对应 [report.md](report.md)）。

## 案例概况

- 输入：XXX=内存分层，YYY=Proxmox VE，ZZZ=VMware vSphere。
- 检索：全程无授权（WebSearch/WebFetch），取得 VMware 分层机制（1:1、4 TB、9.1 GA、默认关闭）
  与 Linux 内核分层机制（TPP/DAMON/加权交织/`daxctl`）等可核验事实。
- 产物：一份符合写作标准的报告，含架构图、部署图、路线图（均 Mermaid 合规）。

## SOP 发挥价值之处

- **价值主线奏效**：阶段零的价值假设卡逼出了明确的度量口径，差距分析每条都能回溯到它。
- **价值筛选给出非显然结论**：四维打分把 MVP 从"重造分层引擎"纠正为"产品化内核已有能力"——
  这是本案例最有价值的判断，且由方法而非直觉得出。
- **防幻觉真的拦住了东西**：控标案例→"无法确定"；价值目标值→"待基线后设定"；OSDI 材料→标注为
  用户提供、未独立核验。没有一处凑数。
- **无授权检索够用**：keyless 路径拿到了足以支撑判断的权威来源。

## 过程中的摩擦与不足（迭代依据）

1. **用户提供但未独立核验的材料**没有专门位置。OSDI 2026 五篇是用户给的，SOP 未规定如何与
   "独立核验来源"区分、如何标注，只能临时加脚注。
2. **"用 reverse-skill 逆向分析开源项目"在开源目标上不对位**。关键实现（内核 TPP/DAMON）是开源
   的，最有效的吸收是源码/机制研读，而非二进制逆向；SOP 的调研阶段没区分"开源吸收"与"闭源逆向"。
3. **grill-with-docs 作为实时访谈在单次自动跑动中不适用**。它是交互式访谈技能；本次是自动产出，
   只能把它的"纪律"落成报告里的"存疑与需确认"一节。SOP 未说明这两种用法的边界。
4. **价值目标值容易被拍脑袋**。度量表若不提示"先建基线再设目标"，很可能被填上无据数字；本次
   刻意留空并注明，但这依赖执行者自觉，应写进模板。

## 据此的迭代动作（已应用）

| 摩擦点 | 迭代动作 | 落点 |
|---|---|---|
| 1 用户材料无位置 | 调研阶段增加"来源分级与标注"要求：独立核验 / 用户提供未核验，分别标注 | SKILL 阶段二、report-outline 参考资料说明 |
| 2 逆向不对位 | 调研阶段明确"开源吸收 vs 闭源逆向"：开源走源码/机制研读，闭源才用 reverse-skill | SKILL 阶段二 |
| 3 grilling 用法边界 | 说明两种用法：用户在场→实时访谈；自动产出→落"存疑与需确认"一节，并将其设为报告标准章节 | SKILL、report-outline 新增"存疑与需确认" |
| 4 目标值拍脑袋 | 度量表加"先建基线再设目标值"提示 | report-outline 价值度量表 |

## 遗留

- 端到端**真实运行分层负载**（在 Proxmox 上实测 TPP/DAMON 收益）超出本环境能力，未做；报告的
  目标值因此留空待基线。这是最大的未闭合项，需真实环境验证。
- 本次未触发 reverse-skill 二进制工具链（目标全为开源），其在闭源固件/驱动场景的价值待后续案例
  检验。

## v3 · 多 reviewer 对拍与实质返工

按用户要求，成文后用四路 reviewer（技术深度 / 产品价值 / 证据严谨 / 架构可行）并行对抗式评审。结论：
v1/v2 "兑现太一般"，且含**机制性事实错误**。对拍查出并已在 v3 修正：

- **机制错误**：NVMe 慢层 = swap/zswap（非 TPP/DAMON；`daxctl` 不适用于 NVMe）；"降级" = 迁到 NUMA
  内存层（非写 NVMe）。
- **代次错配**：应以 Proxmox VE 9.0（内核 6.14）对 vSphere 9.x，而非 PVE 8.x（加权交织 6.9、DAMON
  迁移 6.11 在 6.8 内核不具备）。
- **数值**：删除误用 [7] 的 "P99<10%"；密度 [1] 仅支持方向、非 +80–100% 定值；TCO 改称"介质采购单价
  降幅"并列明未含项与消费级价格局限；CXL 延迟改为 140–410 ns 区间 + 尾延迟。
- **论点**：NVMe 上是机制差距（非包装差距）；超越靠 CXL 原生 + 自主可控 + TCO + 时机，非追 NVMe。
- **补齐**：热迁移×分层、大页/THP、故障域/安全/vNUMA/KSM、why-now、具名买家段、控标条款语言、异议
  应答、可证伪假设 + kill-gate、投资建议、业务与技术双规划。

**对"目标值留空"的更正**：前文遗留写的"留空待基线"已过时——现做法是**用可核验公开材料给估算（标注
来源与推导），需本地验证的写成对比测试设计（意图 + 预估）**（基线不限自测）。

**据此固化进 SOP**：`value-realization-model.md` 增"多路评审加固的必过门"（具名买家 / 买家货币 /
可证伪 + kill-gate / 控标条款语言 / 机制·代次核对 / 超越答案 / 评分自洽）与多 reviewer 对拍建议；
`report-outline.md` 增"如何超越"章节、控标条款语言与异议应答、why-now/对手、机制·代次提示；`SKILL.md`
阶段七要求"如何超越 + 业务/技术规划 + 投资建议"，并加自检项、机制·代次核对与多 reviewer 对拍步骤。

## v4 · 第二轮对拍（全资产参与 + 配置一致）与方向性纠正

按用户"全资产参与 + 子代理用主 agent 配置（Fable 5）"的要求，第二轮把之前闲置的三块资产以其方法论
派进对拍（也复审 v3）：grilling+domain-modeling、reverse-skill（开源版：对 v6.14 内核源码逐条核验）、
storm-research（视角覆盖）。三路（全 Fable 5）强烈收敛，抓出 v3 的**方向性错误**：

- **v3 把 v2 "改错了"**：v3 断言"NVMe=机制差距（非包装）"，但内核源码证明 `DAMON_RECLAIM`/`DAMOS
  pageout`/`memory.reclaim` 已能主动逐冷到 NVMe swap（Meta TMO 生产验证）——差距其实在**产品化**，即
  v2 的判断。v4 已收回并重述超越论点（产品化 + 开源/TCO 护城河；CXL 作期权）。
- 另修一批已核验事实错误：`set_mempolicy2` 不存在、`daxctl` 不用于 NVMe、DAMON 迁移不计
  `pgpromote/pgdemote`、大页双方都牺牲、vMotion 惩罚对称、VMware GA=9.0、`[11]` 作者标错、代次应到
  PVE 9.2/内核 7.0。
- 产出 domain-modeling 资产：`CONTEXT.md` 术语表 + `docs/adr/0001-0003`。

**配置一致的价值实证**：第一轮（默认子代理配置）与第二轮（Fable 5）对比，Fable 5 那轮明显更深、直接
对内核源码取证并推翻了一条核心论点——印证"子代理用主 agent 配置"这条原则对质量的实质影响。

**元教训（已回灌 SOP）**：机制性主张必须对**一手源**（内核源码/官方文档）核验，不能只靠博客；且一次
"修正"本身可能引入新错误（v3 之于 v2），故高价值结论需**再核验**，并优先用与主 agent 一致的高配置
子代理做对拍。

## v4.1 · 用户输入即线索（research 核验）

按用户原则"用户提供的都是 hints、须发挥能力去 research 核验/发散"，把之前偷懒标"未独立核验"的 OSDI
[8] 当线索独立检索：**OSDI '26 与 RamRyder / MAC / MDK 已独立核验**（RamRyder 的 +28.6%/+43.2% 与材料
吻合，MAC 题名在 OSDI '26 列表可查），**NEMO / OBASE 命名未能确认**（概念可溯 SoarAlto "Beyond Hotness"
OSDI'25、ObjecTier）；并挖到直接相关的已核验源 **Equilibria [20]**（CXL 多租户公平分层）与 **Memstrata /
Managing Memory Tiers with CXL in Virtualized Environments（OSDI'24）[21]**，后者部分回应了"KVM guest 上
分层无实测"之虑。原则已写进 SOP（价值模型/骨架/技能三处）：**用户材料是线索，须 research 核验/发散，
不得原样当"未核验材料"支撑结论**。

## v4.2 · 逆向学习（reverse 技能消化开源栈）

按用户给的课程（作为线索）执行 reverse 技能（开源形态），产出两份：SOP 层的可复用方法
[reverse-learning-map](../../reverse-learning-map.md)（按逆向学习价值排序、每仓库一问、观测/布局/
放置/回收四分法、名词贴回函数）；案例层的 [reverse-digest](reverse-digest.md)（P0–P3 逐仓库源码级
答案 + 论文增量表 + 对 v4 的反哺）。证据分级如实标注：内核 mm 主干为**源码核验**（沿用 Fable-5
reverse 轮对 v6.14 的核验），QEMU CXL 与 damo 为**本轮一手文档核验**（CFMW 经 ACPI CEDT、QEMU 不仿真
一致性协议；damo 的热判断在内核、`--damos_action pageout` 一键接观测到动作），其余为**阅读式**；
未运行部分并入 benchmark 执行前置。反哺：ADR-0001/0003 由概念级证据升为函数级；damo 分工可作 MVP
观测面参照；OBASE/MAC 维持远期评级的依据落实。

## v4.3–v4.4 · SOP 先行迭代 → 机制底座接线 → 对拍返修

按用户"先迭代 SOP，再用最新 SOP 迭代本案例"的次序执行，三步闭环：

1. **SOP 先行**：把"逆向学习"升为阶段二正式子步骤（SKILL 阶段二指引 + 资产映射行 + 自检项），
   价值模型新增"机制底座（逆向消化）"必过门（共享开源上游时须产出 reverse-digest、机制主张贴回
   函数并分级标注），报告骨架 §二 加机制底座提示。
2. **v4.3 接线**：按新必过门回灌报告——此前 report（v4）对 reverse-digest **零引用**，不合新门；
   把 §一/§二/§四/§六 的机制判断挂接到函数级底座，MVP 观测面补 damo 参照。
3. **v4.4 对拍返修**：一路 Fable-5 reviewer 对 report×digest 做一致性对拍，判 **FAIL（9 条必修）**。
   最有价值的三条：显式内存层作者归属错误（实为 IBM Aneesh Kumar K.V，`992bf775`）；"Red Hat 雇着
   维护者"无据断言；"计数器一律按 VM 采（已核验）"不成立（v6.14 `memory.stat` 无 `pswpin/pswpout`）。
   **对拍的一手核验我方全部亲手复核后才采纳**（GitHub API 查提交作者、双通道抓 v6.14/master
   `cgroup-v2.rst`），复核还多查明一处**利好**：v6.14 已有按 cgroup 的 `pgdemote_*`，按 VM 采降级
   即刻可行。9 条必修 + 8 条建议全部落地（含 digest 补大页/热迁移/`mpol_misplaced` 锚点与
   "收束三·计数器与按 VM 观测面"；benchmark-plan、采集脚本与案例讲解用的原生可编辑幻灯
   mt-v1.pptx 同步修正）。

**元教训（回灌依据）**：① "接线"本身要对拍——v4.3 只做挂接、未重审底座，对拍立刻抓出双向悬空
引用与分级标签被扩张（"内核源码核验"罩住了 Proxmox 用户态主张）；② reviewer 的一手核验结论同样
要**再核验**后才可采纳（本轮采纳前全部复核，且复核出 reviewer 漏掉的 `pgdemote_*` 利好）；③ "已
核验"三个字必须能指认核验对象与版本，否则就是新的幻觉入口。

**同轮落地的新写作规则（用户提出）**：**引用自闭环**——`[n]` 引注与跨文档链接只承担核验/溯源，
当前句段须就地写出关键事实/数字/结论，读者不跳转即可完整理解；不为篇幅牺牲自闭环。已植入
report-style-guide（新节 + 自检项）、CLAUDE.md、report-authoring/competitive-analysis 两技能与
report-outline 模板，并顺手修正 extensions/README 一处纯跳转引用（修正过程中还拦下一次自造
"方案二"的幻觉）。本案例 v4.3/v4.4 的全部新增引用均按此规则书写。

## v4.5 · 结论闭环（消灭悬留存疑）+ 五路对拍

按用户"存疑不允许存在、必要时启动多个独立资深 reviewer 对拍出可闭环结论"指令执行。先把规则固化进
SOP（report-style-guide 新增"结论闭环"节、value-model 必过门、report-outline 把"存疑"章改写为"结论
校准与验证闭环"、SKILL 自检项、CLAUDE.md），再落到本案例：把原 5 条存疑逐条推进到三种闭环形态
（事实 / 预测+可证伪门 / 确定的不可得判定+处理）。

**五路 reviewer（Opus，配置同主 agent）对拍 + 主 agent 再核验**：
- 文献路：**NEMO/OBASE 竟是真实 OSDI '26 论文**（此前判"命名存疑"被推翻）——主 agent 抓 USENIX 议程
  三重复核（含中性无提示复抓排除提示污染）坐实五篇题名/作者；vMotion 1.5–2× 换挂 Broadcom 一手；
  [9][10] 降为方向性 + TrendForce 合约价锚。
- 内核/产品化路：reviewer 自带两路子对拍，**自查出自己初稿的循环论证**（头对头 ±15% 从门倒抄），
  删除并改为悬崖结构 + p<约1%/k 门；产品化拆 M1a/M1b；补五卡点（memcg 过滤器 VM 重启静默失效等）。
- CXL 路：改"trade press 候选"为一手负证（VMware 9.0/9.1 文档 0 CXL、Peaberry 前瞻带免责），加强
  "CXL 作期权"。
- CoCo 子路（一手 ABI + 内核源码）：**纠正报告的因果错误**——CoCo 私有内存不能 host 分层系**实现
  缺口非加密架构禁止**（LWN guest_memfd 一手），共享页可分层、静态放置可用。
- 市场/信创路：结果未直接可用（agent 卡死被 stop），相关结论由主 agent 据 YYY 双形态输入 + 可核结构
  性事实自行闭环（形态 A/B、价格结构性不对称、非介质 TCO 方向）。

**踩到的真实工程问题（已在与用户对话中如实报告）**：① **子代理过度繁殖**——4 路 reviewer 均为
general-purpose，各自又 spawn 了嵌套对拍子代理（峰值 21 个），**耗尽本会话 WebSearch 预算（200/200）**；
② 因预算耗尽 + 嵌套阻塞，两路 reviewer 卡死 26 分钟，主 agent `TaskStop` 止损（stop 时 CXL 路/CoCo 子路
反而 flush 出可用结论）；③ 会话恢复时误对一个已完成的 reviewer 发 resume 致其重跑。教训：**对拍子代理
应限制为不可再 spawn、并预告检索预算**（已在恢复消息中补"勿再 spawn/勿再检索"）。

**再核验否决**：主 agent 对 reviewer 的一手结论逐条复抓，**否决两条 reviewer 误报**——PVE 代次表
（9.2=7.0 默认，报告原本正确）、引注 [1] 归属（父页 verbatim 含 4TB/默认关/维护模式，报告原本正确）。
印证元教训④"reviewer 的一手结论采纳前须亲手复核"，连"reviewer 说报告有错"也要复核。

**控标真实案例（form ③→① 升级，闭环纪律的实证）**：初判受阻于 WebSearch 预算耗尽、拟以 form ③（条款
语言）闭环；但没有停在"不可得"——先试 keyless `html.duckduckgo.com`（WebFetch 报 socket closed 不可用），
再试**中国政府采购网 ccgp.gov.cn 搜索端点**（`search.ccgp.gov.cn/bxsearch`，keyless、符合无授权策略）
**成功**，取到真实中标公告并逐条 WebFetch 详情页核验：宁波二院"VMware 迁建改造+超融合"¥314.96 万
（2026-09-28 [37]）、瑞安人民医院"国产化超融合集群"¥97.5 万（2026-09-24 [38]）。诚实边界：中标品牌在
附件未公开，故只录可核字段、不臆断品牌、不宣称与 Proxmox 相关。**教训**：form ③ 是"确无路径"时的兜底，
不是偷懒出口——换一条 keyless 路径往往能升到 form ①。真机实测（config E 头对头）经用户确认无环境，仍以
form ②（预测 + 门）闭环。

**用户外部输入的采纳**：用户提供两条——"无实测主机"（据此把头对头等实测项定为 form ② 预测+门）、"YYY
泛化到国产 KVM HCI（Sangfor/SmartX）"（据此把信创改双形态，并按 hint 原则核验：二者与 PVE 同承 Linux/
KVM，具体入围条目主 agent 未独立核验、如实标注）。

**全仓自闭环清扫（规则落地后的整体迭代）**：派三路 Fable-5 只读审计员并行扫 23 份文档（案例组 8、
SOP 核心组 5、扩展与技能组 12——vendored 内容除外），逐处核查 `[n]` 引注与跨文档链接。结果：
**重违规 0、轻 11**，其中 10 处已修——补脚本一句话描述（DRY-RUN 语义经亲手核实脚本后才写入）、
在 reverse-digest 引用处就地概括方法要点、纠正 benchmark-plan 两处跨文档章节号错标（§十→§九、
§七→§八）、SKILL 就地列出记分卡七维（用价值模型真实维度，弃用审计员自拟模板）、SOP 各 README
的骨架/映射指针补就地概括；1 处表格单元格压缩按规则的紧凑豁免保留。多份文档（CONTEXT、三份
ADR、authoring/extensions 全部）被判整体合规，report-outline §四与价值模型必过门的写法被审计员
引为样板。

**第二轮·闭合全部剩余范围**：核过全仓 27 份"己方新增"文档（用 `git log --diff-filter=A` 逐一区分
上游 STORM 2024 原生文件——README/CONTRIBUTING/各 example README 均属之、按零改动原则不动——与本分支
新增文件），补齐前三路审计未覆盖的 3 份 vendored 树内"己方注记"：`.claude/skills/VENDOR-NOTICE.md`
（纯溯源+许可，已自闭环）、`vendor/reverse-skill/VENDORED-INTO-STORM.md`（把 LOCAL-OVERRIDES 的裸
指针改为就地列出三条 override）、`LOCAL-OVERRIDES.md`（Override 3 补入"引用自闭环"要点，使经 vendored
`docs-generator` 产出的逆向/渗透报告也继承该规则）。另全仓 grep "见/详见/方法见 X" 全部命中逐条复核：
除同文档前向指针、citation-plumbing（每个 `[n]` 已就地点明主题、仅 URL 后置）外无裸跳转；顺带把
benchmark-plan 的 setup-tiers 脚本指针补上 DRY-RUN 安全模型（改系统状态前须知，与 report 一致）。
