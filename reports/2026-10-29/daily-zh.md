# arXiv 2026-10-29 中文总简报（部分完成，不可视为当日完整日报）

## 公告批次与严格覆盖声明

**北京时间报告日期：2026-10-29（周四）。** 本次 arXiv 官方列表标题显示 **“Wednesday, 28 October 2026”**，这是美国东部时区公告日期；该批北京时间 2026-10-29 08:00 左右公布，恰好是 **今天上午** 的目标批次。绝不能把网站的 10 月 28 日标签直接当作昨天北京时间的已处理批次。

| 官方类别 | new | cross | revisions | 原始合计 |
| --- | ---: | ---: | ---: | ---: |
| [gr-qc](https://arxiv.org/list/gr-qc/new) | 30 | 25 | 24 | 79 |
| [hep-th](https://arxiv.org/list/hep-th/new) | 37 | 28 | 41 | 106 |
| **两类原始合计** | **67** | **53** | **65** | **185** |

官方网页各栏目显示的数目与 2000 条/页上限核对过。新文与首次交叉共 **120 次原始收录**；手动按基础 arXiv ID 跨类去重得到 **100 篇不同论文、20 次跨类重复**（如 2610.37302 属 hep-th new / gr-qc cross）。尚未核实93篇待读条目的完整版本号。修订原始 65 条，单列不作为新论文。

**数据处理进度：100 个基础 ID 全部登记**。7 篇已读正文并有双语卡；**93 篇 pending（官方完整摘要/作者/版本未逐篇完成核验）**，仅摘要暂读 0，符合严格门槛的跳过 0。93 项并未经过有效预分类，故不可将其视为低相关或仅需摘要。**ID 去重已完成，但 97 篇完整摘要、版本、作者与有效 triage 尚未完成；正式正文需读数取决于后续严格预分类**，报告状态为 partial，不得声称筛完。

## 今日已核实的重要结果（作者结论）

1. **[引力中心荷的几何起源](papers/2610.37302v1.md)**：在协变相空间中，对零 flux 与 field-space exact flux 区分 Hamiltonian 荷，给出对应中心 cocycle。适合直接对照二维 dilaton 作用量的边界荷，不过实例是 AdS₃，不可直接搬用。
2. **[耦合 SYK 中婴儿宇宙](papers/2610.36032v1.md)**：内部重算符的关系型时间使 chord saddle 的“大小”按 $|\cos\mu t|$ 变化；不同于从外部边界 Hamiltonian 做时间演化。这涉及可观测时钟的定义，与当前研究方法上接近。
3. **[(A)dS₂ 上的 ’t Hooft 模型](papers/2610.37667v1.md)**：null-gauge 中 Casimir 将平直二维 QCD 的介子方程与几何 Legendre 算符相加；AdS₂ 的边界谱与 dS₂ 的共振须分别处理。注意其背景是刚性的，不等价于 JT 引力。

以上仅为正文已读的初步精选，**不是其余 117 条公告的低相关性判断**。每篇均有独立中文/英文概括与章节、方程定位，未开展独立数值复算。


## 新增四篇正文精选（独立正文阅读，未逐式复算）

- **[2610.36735v1：二维/四维共形反常 WZ 作用量](papers/2610.36735v1.md)** — I5/R5，§2.3 式 (30) 给出二维 Polyakov 非局域作用量的局域 scalar 表述；§2.5 的 WZ cocycle 与边界 Hermiticity 条件对于 2D dilaton 变分有直接借鉴价值。作者认为 conformalon 可视为 IR 集体自由度；此判断不自动意味着现有 dilaton 模型多一个物理 edge mode。
- **[2610.37493v1：量子 master constraints 恢复经典规范分布](papers/2610.37493v1.md)** — I5/R4，Theorem 3.1: \operatorname{Im} L=(T\Sigma)^\omega$，且 $L^2=0$ 等价 coisotropic， §3.3 的 double bracket 明确可观测量判据。适合巩固约束/辛约化工具，有限维正则前提不可忽略。
- **[2610.36128v1：5PM 散射 K3 Landau 奇点及记忆区](papers/2610.36128v1.md)** — I5/R4，§3 证明 $\gamma=3$ 是切割轮廓 pinch，§6 在指定 retarded routing 后得到 memory-region 积分常数，**并未计算完整5PM记忆可观测量**。
- **[2610.35969v1：虫洞单极子不可由源运动感应](papers/2610.35969v1.md)** — I4/R4，§II–IV 由电通量、Schwarzschild 真空扰动和 Bondi flux 区分“静态匹配解族”与真正时间演化，提示引力记忆计算须控制荷超选 sector 与边界时钟归一。

## 推荐阅读顺序及可执行步骤

先读中心荷 §2.2–2.3 并直接在现有 dilaton 模型中检验 $F_\xi$ 的可积性；其次读 SYK §4 的两种时间；最后读 AdS₂ QCD §3–5 Casimir 到 meson equation 的推导。已知完整卡片均链接于 [双语精选](selected-bilingual.md)。

## 数据风险与后续

两页均核实当日批次与数量，并记录[100 个不同基础 ID 的全量标题清单](../../data/2026-10-29/listing-id-index.json)。RSS 尚未独立核实日期；对于 93 篇待读，作者、完整摘要及版本仍待处理，尚不能正式 I/R 评分或合法跳过。[skipped.md](skipped.md) 的 0 只表示三篇已评估论文没有低相关跳过，另外 93 篇仍是 pending。本期状态存于 [status.json](status.json)，官方网页刊登日与北京时间报告日分别入库。

## 已捕获论文索引（非全量）

- [2610.36032v1: Cosmology of the Baby Universe in Coupled SYK](papers/2610.36032v1.md) · final I=5, R=4 · body_reviewed
- [2610.37302v1: On the geometric origin of central charges in gravity](papers/2610.37302v1.md) · final I=5, R=5 · body_reviewed
- [2610.37667v1: The 't Hooft model on (A)dS₂](papers/2610.37667v1.md) · final I=5, R=4 · body_reviewed
