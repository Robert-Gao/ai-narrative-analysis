# AI Narrative Analysis · AI 叙事研究

面向传播学研究的开放 Agent Skill：分析媒体、企业、政策与公众如何讲述 AI，并将语料分析衔接到受众效果研究。默认中文，可处理其他语言材料。

## 安装与使用

```bash
npx skills add RoberGao-hub/ai-narrative-analysis --skill ai-narrative-analysis -g -y
```

在支持 Skills 的助手中使用：

> 使用 $ai-narrative-analysis，分析这些新闻如何建构 AI 的角色。每项判断附原文与位置，保留不同说话者和反例。

> 使用 $ai-narrative-analysis，帮我把“AI 辅助者/替代者”候选维度转化为受众实验方案，区分叙事角色与正负情感操纵。

获取更新：`npx skills update ai-narrative-analysis -g`。更新后核对文件内容；如 CLI 更新未生效，可重新执行安装命令。一般使用者不需要启用下面的维护者同步程序。

## 内容

- [SKILL.md](SKILL.md)：范围、核心判断、工作分流与技能协作。
- [语料与编码](references/corpus-and-coding.md)：抽样边界、候选维度、方法一致性、人工复核。
- [受众效果](references/audience-effects.md)：操纵、刺激材料、预试、样本量与推断边界。
- [记录与示例](references/records-and-examples.md)：台账、编码字段、反讽与引述等边界情形。

本 Skill 是研究辅助工作流，不是经过验证的叙事量表，也不替代研究者的方法判断。候选类别不是研究发现；模型模拟不构成受试者数据；文本中的叙事不自动证明受众效果。现有版本经过结构检查，尚未开展独立研究效度评估。

可按任务配合 literature-review、qualitative-research-guide、experimental-design、statistical-power、statistical-analysis；这些技能需独立安装，不随本仓库自动下载。网络扩散问题再使用 networkx。

## 两台 Mac 双向同步（维护者专用）

这会将此仓库的 Skill 和说明文件改动自动公开到 GitHub。不要在发布文件中放原始访谈、受试者信息、密码或未公开研究材料。代码有文件白名单和有限凭据检查，但不能自动识别所有私人信息。

每台 Mac 各执行一次；需要 macOS、Python 3.9+、Git、GitHub CLI，以及 RoberGao-hub 的账户权限：

```bash
brew install gh
gh auth login --hostname github.com --git-protocol https --web
mkdir -p "$HOME/Documents/Codex"
git clone https://github.com/RoberGao-hub/ai-narrative-analysis.git "$HOME/Documents/Codex/ai-narrative-analysis"
cd "$HOME/Documents/Codex/ai-narrative-analysis"
python3 tools/install-macos.py
```

若同名目录已经存在，先查看其内容，不重复克隆或覆盖。若 Python 不可用，安装 Python 后再运行安装器。GitHub 的网页/插件登录与本机 CLI 登录相互独立。

安装器会备份现有全局 Skill，并将 `~/.codex/skills/ai-narrative-analysis` 链接到本地仓库。不会修改其他 Skills。维护者应通过 Git 工作副本更新，避免再用 Skills CLI 覆盖此链接。

后台每 30 秒运行一次。文件稳定至少 30 秒后自动提交，获取远端、尝试合并并推送；通常为约 30–60 秒加网络耗时，另一台再等待一次轮询，不承诺严格实时。仅登录会话中运行，睡眠或断网后恢复同步。

自动提交范围：SKILL.md、README.md、LICENSE、CITATION.cff、agents/openai.yaml、references 下的 Markdown。其他文件需要手动检查并提交。远端 tools/tests/工作流变动会暂停自动合并，需审阅并重新运行安装器；后台使用本机安装时复制的同步程序，不自动执行远端脚本。

## 状态、暂停与冲突处理

```bash
cat "$HOME/Library/Application Support/AI Narrative Sync/status.txt"
launchctl print "gui/$(id -u)/org.robergao.ai-narrative-sync"
```

冲突会保留双方提交、冲突标记和暂停状态，不自动选择某一方。提示记录在上述状态文件及同目录 sync.log 中；没有桌面弹窗。

解决时，在仓库中查看 `git status`，人工编辑冲突文件，执行 `git add <已解决文件>` 和 `git commit`。确认内容后恢复：

```bash
python3 "$HOME/Library/Application Support/AI Narrative Sync/sync.py" \
  --repo "$HOME/Documents/Codex/ai-narrative-analysis" \
  --state "$HOME/Library/Application Support/AI Narrative Sync" --resume
```

远端维护脚本更新导致暂停时：先停止后台，审阅远端差异，手动合并，重新运行安装器，再恢复。网络和认证失败自动重试；分支不为 main、有手工暂存内容或白名单外改动时等待处理。程序不强推、不 reset、不 stash，也不自动放弃冲突。

停止后台（保留所有文件与链接）：

```bash
launchctl bootout "gui/$(id -u)/org.robergao.ai-narrative-sync"
```

需要永久禁用时，停止后将 `~/Library/LaunchAgents/org.robergao.ai-narrative-sync.plist` 移到备份目录。重新安装可恢复。

## 可复现与贡献

论文或报告请记录所用 commit（`git rev-parse HEAD`）、模型版本、提示词、人工修改及材料范围。滚动更新的 main 不等同于固定研究版本。欢迎通过 Issues 报告方法边界，通过 Pull Requests 提议改进；提交前运行 `python3 -m unittest discover -s tests`。

初稿由 RoberGao-hub 与 AI 助手协作编写；方法参考在相应文件中列出。引用信息见 [CITATION.cff](CITATION.cff)。MIT 许可证适用于本仓库原创内容；链接的外部文献不属于本仓库许可范围。
