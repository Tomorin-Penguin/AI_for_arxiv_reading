# 阅读运行与恢复

## 本次已确认的故障

2026-10-29 的平台最近一次阅读运行 `f51b8b63-53f8-832a-8bb6-0c0cd8e8f26c`：计划 12:00:12，记录的最近开始 13:26:54.171，结束 13:51:57.261（北京时间），状态 **failed**。last_result/chat_ref 均为空，接口未提供错误原因或完整历史。因此不能断言是超时、额度、电脑离线或某次配置编辑引起；最近开始时间也不能代表最早阅读时间，仓库存在更早成果。来源是[任务管理接口诊断](https://chatgpt.com/c/6ae2f3e0-5ddc-83e8-8ea1-01a675be6cd7)中读取的 last_run 摘要。

13:47 的实际成果为 37/82 篇正文完成，13:49 修正简报后没有新增阅读提交。14:00、15:15 邮件任务仍用旧成果及 phase=reading 推断活跃，未检查平台 failed。原阅读日程只每日触发一次，提示词中的“继续读”没有变成失败后的调度；这是已确认的恢复与监测缺口。底层失败原因未知，不能用这个缺口代替底层错误归因。

## 同一任务按小时续跑

保留现有阅读 automation ID，11:00启动，12/13/14/15/16时只续做未完成队列。20分钟为主动保存退出预算，不是平台硬上限。逐篇或小批次提交，不能等整批82篇完成再保存；原论文阅读标准不降低。16:00轮先保证16:20有可发送快照。所有状态在GitHub，不能依赖本机进程或目录。

每次先以最新 main 和 expected_sha 原子领取 reading_worker 租约；回读确认 owner 后才能工作。其他有效租约存在则退出，过期才可接管；失去所有权的旧运行停止写入，不能覆盖新运行。每10分钟及每批记录真实 heartbeat_at，lease_expires_at 最多延至该心跳后30分钟。每次重读最新文件、合并事件再写，保留邮件任务的并发更新。

state/runs/YYYY-MM-DD.json 中 reading_worker 记录 owner（可用平台run id）、started_at、heartbeat_at、lease_expires_at、ended_at、end_reason。平台摘要另存 platform_last_run：run_id、status、started_at、finished_at、observed_at、evidence_url。二者不得混为同一个运行。新运行开始时间晚于旧失败结束时间才可能恢复；实际新心跳/提交需可核实。

预算到点保存 phase=awaiting_resume、ended_at、end_reason=checkpoint、next_resume_at；只在相应小时日程已回读验证时设置 resume_schedule_verified=true，释放租约。最后16:00轮不能虚构当日之后的续跑；尚有欠缺则明确部分完成/blocked及需要继续的队列。若不能继续等公告，写 waiting_source 和真实下一检查时点，不把来源失败写成无更新。无更新且无授权补读，后续小时轮次快速退出。

## 邮件必须检查运行是否真实活跃

优先读平台 last_run。failed/cancelled 且没有较新恢复运行，视作已失败；不能被旧的 reading 标记或 pending 队列覆盖。平台工具不可用时检查阅读心跳及正文提交：20分钟以上没有证据，不声称仍在阅读，记录 stale 并请求恢复。单个旧提交只能证明“曾经读过”；邮件检查/日志更新不是阅读进度。正常等待下一已保存的续跑时点可记 awaiting_resume，但超过计划10分钟仍未启动即视为停滞。

scripts/reading_health.py 返回活跃平台证据、活跃工作记录、待续跑、短期未验证进度、停滞或失败；scripts/delivery_policy.py 结合窗口处理。调用前必须刷新真实平台证据，不能凭缓存伪造观测时间。14:00已知失败应告知；14:00后才发现，窗口内及时告知并说明实际发现时间，可附已完成部分。同日仍最多一封主邮件。正在恢复且有新证据，则按完成窗口发送。邮件任务不承担论文正文阅读，也不更新阅读心跳。

修复验收不能只看日程或提示词已保存：必须观察新的运行、真实正文成果提交，以及之后小时触发是否能接管未完成队列。底层终止原因没有证据时保持未知。

## 仓库增量写入的完整性门禁

【仓库提交完整性，2026-10-29新增最高优先级】任何GitHub写入前先读最新main为H，再取H的commit.tree.sha为T。create_tree必须显式base_tree_sha=T，只传本批预定修改；禁止省略base_tree_sha。创建新提交前获取T和新tree的完整recursive树（truncated必须false），核对原有所有文件仍在、未修改文件mode/type/sha完全相同、新增/修改路径严格等于本批清单且blob与预定内容相符；可运行scripts/publication_guard.py或逐项等价校验，不能验证则停止发布并保留草稿。create_commit的parent_sha=H；update_ref必须expected_sha=H且force=false。并发冲突后重新读main并合并，禁止force更新、回退分支或自行回滚。写后读main和目标文件确认。仓库完整性事故已恢复；旧的临时停止指令只针对当时出错会话，不取消用户已明确授权的后续续读。正式阅读计数必须与阅读卡和ledger一致；发现孤立卡先核验补登记，不能重复读或虚报完成。

2026-10-29手动恢复时，执行器省略base_tree_sha，把只含状态文件的树提交到main，造成当前快照仅剩1个文件。此前127个文件的历史完整，已通过非强制提交255913060c668f6f6e75de7cab1cccaa19080e4f恢复，逐项验证0缺失。此事故与13:51的平台failed是两件事，不能据此推断早先运行的底层失败原因。
