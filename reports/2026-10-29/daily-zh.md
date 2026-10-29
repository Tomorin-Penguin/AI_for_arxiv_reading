# arXiv 2026-10-29 中文总简报（部分完成，不可视为当日完整日报）

## 公告批次与严格覆盖声明

**北京时间报告日期：2026-10-29（周四）。** 本次 arXiv 官方列表标题显示 **“Wednesday, 28 October 2026”**，这是美国东部时区公告日期；该批北京时间 2026-10-29 08:00 左右公布，恰好是 **今天上午** 的目标批次。绝不能把网站的 10 月 28 日标签直接当作昨天北京时间的已处理批次。

| 官方类别 | new | cross | revisions | 原始合计 |
| --- | ---: | ---: | ---: | ---: |
| [gr-qc](https://arxiv.org/list/gr-qc/new) | 30 | 25 | 24 | 79 |
| [hep-th](https://arxiv.org/list/hep-th/new) | 37 | 28 | 41 | 106 |
| **两类原始合计** | **67** | **53** | **65** | **185** |

官方网页各栏目显示的数目与 2000 条/页上限核对过。新文与首次交叉的**原始收录条数 120，跨类去重后的确切论文数暂不能核实；“120 篇不同论文”这一表述不可使用**。仅核实到一例跨类重复：2610.37302v1 同时为 hep-th new / gr-qc cross。修订原始 65 条，单列不作为新论文。

**数据处理进度（准确范围）**：已结构化捕获并核实版本 **3 个不同新文 ID**；这 3 篇均满足 priority，**正文已读 3、仅摘要 0、待读 0、跳过 0**，但这几个数字只覆盖已经捕获的 **3 篇**。剩余的 **117 条原始 new/cross 出现** 中含可能的交叉重复，不能直接解释为 117 篇未读不同论文。**所有公告的唯一 ID、完整官方摘要、全量 triage、真实“正文需读总数”和全局 skipped 清单尚未完成**，报告状态为 partial，不得声称筛完。

## 今日已核实的重要结果（作者结论）

1. **[引力中心荷的几何起源](papers/2610.37302v1.md)**：在协变相空间中，对零 flux 与 field-space exact flux 区分 Hamiltonian 荷，给出对应中心 cocycle。适合直接对照二维 dilaton 作用量的边界荷，不过实例是 AdS₃，不可直接搬用。
2. **[耦合 SYK 中婴儿宇宙](papers/2610.36032v1.md)**：内部重算符的关系型时间使 chord saddle 的“大小”按 $|\cos\mu t|$ 变化；不同于从外部边界 Hamiltonian 做时间演化。这涉及可观测时钟的定义，与当前研究方法上接近。
3. **[(A)dS₂ 上的 ’t Hooft 模型](papers/2610.37667v1.md)**：null-gauge 中 Casimir 将平直二维 QCD 的介子方程与几何 Legendre 算符相加；AdS₂ 的边界谱与 dS₂ 的共振须分别处理。注意其背景是刚性的，不等价于 JT 引力。

以上仅为正文已读的初步精选，**不是其余 117 条公告的低相关性判断**。每篇均有独立中文/英文概括与章节、方程定位，未开展独立数值复算。

## 推荐阅读顺序及可执行步骤

先读中心荷 §2.2–2.3 并直接在现有 dilaton 模型中检验 $F_\xi$ 的可积性；其次读 SYK §4 的两种时间；最后读 AdS₂ QCD §3–5 Casimir 到 meson equation 的推导。已知完整卡片均链接于 [双语精选](selected-bilingual.md)。

## 数据风险与后续

公告页两个分类可读取且数量已核对，但 RSS 的 2026-10-29 日期尚未独立证实，云端临时 Python 环境无法直接对 arxiv.org 发起网络请求。由于无法可靠自动抽取所有条目的完整标题/官方摘要/版本，**全量分流是当前阻塞点**。跳过页 [skipped.md](skipped.md) 中“0”仅指已核对 3 篇，绝非其余论文被跳过。本期状态存于 [status.json](status.json)，官方网页刊登日与北京时间报告日分别入库。

## 已捕获论文索引（非全量）

- [2610.36032v1: Cosmology of the Baby Universe in Coupled SYK](papers/2610.36032v1.md) · final I=5, R=4 · body_reviewed
- [2610.37302v1: On the geometric origin of central charges in gravity](papers/2610.37302v1.md) · final I=5, R=5 · body_reviewed
- [2610.37667v1: The 't Hooft model on (A)dS₂](papers/2610.37667v1.md) · final I=5, R=4 · body_reviewed
