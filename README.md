# Code Golf Task Runner

基于 Codex SDK 的自动化 Code Golf 框架。给定一个工作 baseline，自动调用 Codex 生成更短的正确代码，记录所有收发、思维链、token 用量。

## 快速开始

```powershell
# 单任务
python runner.py all_tasks/task004

# 批量（带 cooldown 防 API 限速）
python batch_runner.py all_tasks --ids "001,002,003" --delay 120

# 全部 400 任务
python batch_runner.py all_tasks --delay 120
```

## 任务结构

```
all_tasks/
├── task001/
│   ├── baseline.py         # 可工作的参考方案（越长越好）
│   ├── task001.json        # 训练+测试数据
│   ├── verify.py           # import p() 验证脚本
│   ├── task.md             # golf 指令
│   └── task_config.yaml    # budget 配置
├── ...
└── task400/
```

## task_config.yaml

```yaml
task_id: "task004"

budget:
  max_turns: 10              # 最大对话轮数
  max_tokens: 300000         # 累计 token 上限
  timeout_seconds: 1200      # 任务总时间上限
  turn_timeout_seconds: 600  # 单轮超时
  max_retries: 2             # 间歇错误重试次数

sandbox_mode: "danger-full-access"

verify:
  command: "python verify.py"
  early_stop: true
```

## 工作流程

1. 自动检测 `baseline.py` → 进入 **golf 模式**
2. 模型读取 baseline，理解 `p(grid)` 逻辑
3. 生成 `solveNNN.py`（更短的版本）
4. 运行 `python verify.py solveNNN.py`
5. 通过 + 更短 → 成功；失败 → 反馈重试

## 日志

每个任务输出到 `.codex-logs/`：

```
.codex-logs/
├── turn_001.json    # prompt、思维链、命令、验证结果、token 用量
└── summary.json     # 总 turns / tokens / 耗时 / 成功
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `runner.py` | 单任务运行器，自动检测 golf/探索模式 |
| `batch_runner.py` | 批量运行器，支持 `--delay` `--ids` |
| `setup_golf_tasks.py` | 从 wanderer-cc_golf 数据集批量生成任务 |
| `template/` | 通用模板（task.md, verify.py, task_config.yaml） |

## 生成 400 任务

```powershell
python setup_golf_tasks.py \
  --source "<wanderer_path>" \
  --target all_tasks \
  --all \
  --max-test 5
```

## 环境

- Python 3.12+ (`codex-sdk-python`, `pyyaml`)
- Codex CLI (npm)
- 模型：DeepSeek V4-Pro via OpenRouter
