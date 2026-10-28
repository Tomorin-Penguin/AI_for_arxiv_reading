# AI_for_arxiv_reading

这个库用于存放每日 gr-qc 和 hep-th 预印本的双语阅读卡、中文总简报及面向个人研究兴趣的双语精选。

## 每日安排

北京时间 **12:00 开始阅读，14:00 发送包含简报的邮件**，收件人为 **1468610627@qq.com**，通过已连接 Gmail 发送。首次正式执行为 **2026-10-29**，当天邮件只报道当天上午新公布的论文，不用前一天的文章替代。

由当前 Codex 桌面任务的定时日程执行，GitHub 用于保存材料；并非 GitHub Actions 云端运行。当前方案不需要另配模型 API key。运行时需保持电脑与应用可用、GitHub/Gmail 连接有效；到点启动和邮件送达仍受调度与网络影响。

14:00 邮件包含中文总简报、双语精选要点和完整报告链接。未读完时标明覆盖与待读数量，后续继续补齐仓库；不会把摘要初筛说成全文已读。

## 阅读内容

1. 官方英文摘要和中文翻译，保留出处。
2. 独立阅读概括，中英双语，说明方法、关键结果与适用条件。
3. 当日中文综合简报及完整论文索引。
4. “兴趣精选”和“科研密切相关”两组双语简报，解释具体联系与可开展的计算。

基础范围为两个分类的全部新文与首次交叉收录，跨分类去重；修订稿单列，重点追踪高相关/已精选文章。当前关注二维 dilaton 引力、AdS₂/JT、记忆与时钟可观测量、全局因果结构、SYK 与全息；可直接调整 [兴趣配置](config/interests.md)。

## 导航

- [每日执行规程](WORKFLOW.md)
- [时间和邮件配置](config/schedule.json)
- [逐篇阅读卡模板](templates/paper.md)
- [报告索引](reports/README.md)
- [2026-10-28 官方清单](data/2026-10-28/manifest.json)

初始化已验证两份 RSS 共 185 条公告，合并为 153 个版本，其中 100 篇新文/交叉收录、53 篇修订。此统计只表示清单获取成功，不表示已完成当天阅读。按用户要求，这批数据仅用于测试，不会放进次日的日报邮件。正式日报从 2026-10-29 当天的新批次开始。

## 维护与检查

脚本只需 Python 3.9+ 标准库。`collect.py` 校验 RSS 日期和类型并跨分类去重；`collect_listing.py` 在 RSS 延迟时校验公告页并构建临时清单；阅读与撰写由定时唤醒的 Codex 完成。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/collect.py --feed-dir work/feeds --date YYYY-MM-DD --output data/YYYY-MM-DD/manifest.json
python3 scripts/validate_report.py reports/YYYY-MM-DD/status.json
```

断点、正文读取状态与发信记录分别保存在 `reports/` 和 `state/`。重跑不重复发送相同日期日报；抓取失败不会记作“无新论文”。
