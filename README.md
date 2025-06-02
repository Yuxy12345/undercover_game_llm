# Undercover Game LLM

## 项目介绍
Undercover LLM 是一个基于语言模型的 "谁是卧底" 游戏模拟器。该项目通过整合多个本地和在线语言模型，模拟玩家在游戏中的行为和决策，旨在探索语言模型在心理博弈和策略游戏中的表现。

## 实现思路
1. **玩家配置**：
   - 在 `player_configs.py` 中定义了多个 AI 玩家，每个玩家使用不同的语言模型（本地 Ollama 模型或 OpenAI 模型）。

2. **游戏逻辑**：
   - 游戏核心逻辑在 `game.py` 中实现，包括词语分配、描述阶段、投票阶段、PK 阶段等。
   - 游戏规则基于 `prompts/rule_base.txt`，并通过提示词模板指导 AI 玩家生成描述和投票决策。

3. **语言模型交互**：
   - 在 `llm_client.py` 中定义了与 OpenAI 和 Ollama 模型交互的客户端。
   - AI 玩家通过 `player.py` 调用语言模型生成描述、投票和更新印象。

4. **多轮游戏运行**：
   - `multi_run_games.py` 支持运行多轮游戏并记录结果。
   - 游戏结果存储在 `results/` 文件夹中，并通过 `game_analysis.py` 进行统计和分析。

## 文件结构
- `game.py`：游戏核心逻辑。
- `player.py`：AI 玩家类及其行为实现。
- `llm_client.py`：语言模型客户端。
- `player_configs.py`：玩家配置。
- `prompts/`：提示词模板。
- `results/`：游戏结果存储。
- `game_analysis.py`：游戏结果分析工具。
- `multi_run_games.py`：支持多轮游戏运行。
- `requirements.txt`：项目依赖。

## 运行方法
1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行单局游戏**：
   ```bash
   python game.py
   ```

3. **运行多轮游戏**：
   ```bash
   python multi_run_games.py <num_runs>
   ```
   其中 `<num_runs>` 是运行的游戏轮数。

4. **分析游戏结果**：
   ```bash
   python game_analysis.py
   ```

## 示例
运行 10 局游戏并分析结果：
```bash
python multi_run_games.py 10
python game_analysis.py
```

## 贡献
欢迎对项目提出建议或贡献代码！
