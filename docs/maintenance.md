# 维护说明

[返回首页](../README.md) · [执行规程](workflow.md)

## 每种信息只维护一处

| 信息 | 权威文件 |
| --- | --- |
| 时间、收件人、分类、云端任务 ID | [config/schedule.json](../config/schedule.json) |
| 研究兴趣与筛选标准 | [config/interests.md](../config/interests.md) |
| 预分类分流阈值 | [config/triage.json](../config/triage.json) |
| 完整执行规则 | [docs/workflow.md](workflow.md) |
| 日报导航 | [reports/README.md](../reports/README.md) |
| 每日工作日志与运行状态 | logs/YYYY-MM-DD.md / state/runs/YYYY-MM-DD.json |
| 某日覆盖与阅读进度 | `reports/YYYY-MM-DD/status.json` |
| 已完成的正文阅读版本 | [state/processed.json](../state/processed.json) |
| 某日实际发送结果 | `state/mail/YYYY-MM-DD.json` |

修改日程时间或任务说明时，要同步更新云端任务本身及 `config/schedule.json`；仅修改仓库文件不会重新安排触发时间。运行配置记录已设置的日程，实时启用状态仍应以云端任务页面为准。

## 稳定入口

现有云端任务读取 `CLOUD_WORKFLOW.md`、`docs/workflow.md`、`config/schedule.json`、`config/triage.json` 与 `config/interests.md`。任务说明副本保存在 `config/cloud-reading-prompt.txt` 与 `config/cloud-email-prompt.txt`，修改后也要同步云端任务。这些入口路径保持稳定。

正式成果继续使用如下约定；`YYYY-MM-DD` 为北京时间报告日期，不预建空日报：

```text
data/YYYY-MM-DD/manifest.json
reports/YYYY-MM-DD/
  daily-zh.md
  selected-bilingual.md
  triage.json
  skipped.md
  papers/<arxiv-id>vN.md
  status.json
  mail.html
logs/YYYY-MM-DD.md
state/runs/YYYY-MM-DD.json
state/source-checks/YYYY-MM-DD.json
state/processed.json
state/mail/YYYY-MM-DD.json
```

`data/` 保存来源元数据，`reports/` 保存原创阅读成果，`state/` 保存持续运行需要的记录。论文全文和下载缓存只放临时环境；`archive/` 不参与日常采集、已读去重或邮件防重。

## 运行检查

以下命令在仓库根目录运行，需要 Python 3.9+，仅使用标准库。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/collect.py --feed-dir work/feeds --date YYYY-MM-DD --output data/YYYY-MM-DD/manifest.json
python3 scripts/validate_report.py reports/YYYY-MM-DD/status.json
```

`collect.py` 校验 RSS 日期并去重；`collect_listing.py` 在 RSS 延迟时处理官方公告页。`triage.py` 校验 AI 基于摘要作出的语义分流，不执行关键词分类；缺摘要、不确定、核心方向或方法迁移都受保留保护。具体参数可用 `--help` 查看。邮件发送前使用 `validate_report.py` 的 `--for-mail` 选项，核对真实当前北京时间日期，并自动检查同目录 triage.json、兴趣配置哈希和跳过依据。新报告用 schema_version=2，历史三状态报告仍可验证。

校验失败要修复或如实报告，不能跳过后声称完成。云端没有代码执行能力时，按执行规程做等价的来源、覆盖、版本及发信防重检查。

邮件检查时点为 14:00、15:15、16:30；阅读启动为 11:00。scripts/delivery_policy.py 只负责窗口与状态判定。日志以真实事件追加，无更新日也必须建档；缺少新版运行记录时先核对真实报告进度再迁移。

## 2026-10-28 目录整理（历史）

- 两份相同的执行规程合并为 `docs/workflow.md`；根目录保留云端任务入口。
- 重复的 `config/cloud-schedule-plan.json` 移除，运行配置统一到 `config/schedule.json`。
- 初始化清单、连接测试文件及云端启用快照移入 [归档](../archive/setup-2026-10-28/README.md)，原内容保持不变。
- 正式日报路径、兴趣配置、日程时间、收件人以及采集与校验逻辑保持不变。

历史版本可通过 Git 提交记录追溯。归档中的启用快照只反映当时状态，不能当作当前配置读取。
