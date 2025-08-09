# Undercover Game LLM

## 项目介绍
Undercover Game LLM 是一个基于语言模型的 "谁是卧底" 游戏模拟器。该项目通过整合多个本地和在线语言模型，模拟玩家在游戏中的行为和决策，旨在探索语言模型在心理博弈和策略游戏中的表现。

创作灵感和部分实现参考了LYiHub的liars-bar-llm项目：
https://github.com/LYiHub/liars-bar-llm

## 实现思路
1. **玩家配置**：
   - 在 `conf/player_config.toml` 中配置 AI 玩家，每个玩家使用不同的语言模型（本地 Ollama 模型或 OpenAI 模型）。
   - 在 `conf/gamewords.json` 中管理游戏词语配置。

2. **游戏逻辑**：
   - 游戏核心逻辑在 `src/undercover_game_llm/game.py` 中实现，包括词语分配、描述阶段、投票阶段、PK 阶段等。
   - 游戏规则基于 `prompts/rule_base.txt`，并通过提示词模板指导 AI 玩家生成描述和投票决策。

3. **语言模型交互**：
   - 在 `src/undercover_game_llm/llm_client.py` 中定义了与 OpenAI 和 Ollama 模型交互的客户端。
   - AI 玩家通过 `src/undercover_game_llm/player.py` 调用语言模型生成描述、投票和更新印象。

4. **多轮游戏运行**：
   - `src/undercover_game_llm/multi_run_games.py` 支持运行多轮游戏并记录结果。
   - 游戏结果存储在 `results/` 文件夹中，并通过 `src/undercover_game_llm/game_analysis.py` 进行统计和分析。
   - 游戏运行日志保存在 `log/llm.log` 中。

## 文件结构
- `src/undercover_game_llm/`：主要源代码目录
  - `game.py`：游戏核心逻辑
  - `player.py`：AI 玩家类及其行为实现
  - `llm_client.py`：语言模型客户端
  - `player_configs.py`：玩家配置加载
  - `multi_run_games.py`：支持多轮游戏运行
  - `game_analysis.py`：游戏结果分析工具
- `conf/`：配置文件目录
  - `player_config.toml`：玩家配置
  - `gamewords.json`：游戏词语配置
- `prompts/`：提示词模板
- `results/`：游戏结果存储
- `log/`：日志文件目录
- `pyproject.toml`：项目依赖管理

## 运行方法
1. **前置要求**：
   - 在 `conf/player_config.toml` 中配置要使用的大模型；
   - 如果使用 OpenAI API 模型，需要在项目根目录创建一个 `.env` 文件，配置你的 URL 和 API Key；

```dotenv
API_BASE_URL='<你的API Base URL>'
API_KEY='<你的API Key>'
```
   - 如果使用本地 Ollama 模型，需要本地安装好 Ollama 和配置文件中指定的大模型。

2. **安装依赖**：
   ```bash
   # 使用 uv 安装依赖
   uv pip install .
   ```
   
   或者使用传统的 pip：
   ```bash
   pip install .
   ```

3. **运行单局游戏**：
   ```bash
   python -m undercover_game_llm.game
   ```

4. **运行多轮游戏**：
   ```bash
   python -m undercover_game_llm.multi_run_games <num_runs>
   ```
   其中 `<num_runs>` 是运行的游戏轮数。

5. **分析游戏结果**：
   ```bash
   python -m undercover_game_llm.game_analysis
   ```

## 示例
运行 10 局游戏并分析结果：
```bash
python -m undercover_game_llm.multi_run_games 10
python -m undercover_game_llm.game_analysis
```

## 贡献
欢迎对项目提出建议或贡献代码！
