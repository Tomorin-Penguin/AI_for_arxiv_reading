# arXiv 每日阅读

**gr-qc · hep-th｜摘要翻译 · 双语阅读卡 · 中文日报 · 研究精选**

每天北京时间 **12:00** 在云端开始阅读，**14:00** 将简报发送至 **1468610627@qq.com**。首次正式运行：**2026-10-29**。电脑离线时仍由云端执行，成果按日期保存在本仓库。

## 从这里开始

| 想做什么 | 入口 |
| --- | --- |
| 阅读最新简报或查阅往期 | **[日报索引](reports/README.md)** |
| 查看或调整科研偏好 | [兴趣与科研关联](config/interests.md) |
| 查看时间、收件人和云端日程 | [运行配置](config/schedule.json) |
| 了解阅读、筛选和邮件规则 | [执行规程](docs/workflow.md) |
| 维护脚本与核对结果 | [维护说明](docs/maintenance.md) |

每期提供原文摘要及中文翻译、基于正文的独立中英概括、一份中文综合简报，以及“兴趣精选”“科研密切相关”两组双语推荐。全部新文与首次交叉收录均纳入，跨分类去重，修订稿单列。

**当天邮件对应当天上午新公布的批次。** 未读完时如实列出正文已读、仅摘要、待读数量；测试数据与历史补读不充当当日成果。

## 目录

| 目录 | 保存内容 |
| --- | --- |
| `reports/` | 按日期组织的简报、阅读卡和完成状态；日常阅读入口 |
| `data/` | 当日官方论文清单、摘要元数据和去重统计 |
| `config/` | 唯一运行配置、研究兴趣、两个云端任务的补充说明 |
| `docs/` | 执行规程与维护说明 |
| `templates/` | [逐篇阅读卡模板](templates/paper.md) |
| `state/` | 已读版本记录与邮件防重记录 |
| `scripts/`、`tests/` | 采集、校验工具及测试 |
| `archive/` | [初始化与迁移记录](archive/setup-2026-10-28/README.md)，不参与正式日报 |

## 云端任务

- [每日阅读 · 12:00](https://chatgpt.com/scheduled?automationId=6ae1d5d4b0d88190985f3671e1eb0542&automationSource=cloud)
- [日报邮件 · 14:00](https://chatgpt.com/scheduled?automationId=6ae1d66b2a208190bd6b98923557d565&automationSource=cloud)

时区为 `Asia/Shanghai`。原本地日程已暂停。实际启动和送达时间受云端服务、额度及 GitHub/Gmail 连接状态影响。

`CLOUD_WORKFLOW.md` 是现有定时任务的固定入口，转向统一执行规程；完整规则只维护一份。
