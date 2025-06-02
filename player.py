import json
import re
from typing import List, Dict, Tuple
from llm_client import LLMClient, OpenAIClient, OllamaClient  # 假设llm_client.py在同一目录

# 读取提示词模板
def load_prompt_template(file_name: str) -> str:
    """从文件加载提示词模板"""
    try:
        with open(f"prompts/{file_name}", "r", encoding="utf-8") as f:
            return f.read()
    except:
        print(f"警告: 无法加载提示词模板 {file_name}")
        return ""

# 加载所有提示词模板
RULES = load_prompt_template("rule_base.txt")
ANALYZE_TEMPLATE = load_prompt_template("analyze_game_rule.txt")
VOTE_TEMPLATE = load_prompt_template("vote_prompt_template.txt")
DESCRIPTION_TEMPLATE = load_prompt_template("description_prompt_template.txt")
REFLECT_TEMPLATE = load_prompt_template("reflect_prompt_template.txt")
CORRECT_JSON_TEMPLATE = load_prompt_template("correct_json_template.txt")


# 定义AI玩家类
class AIPlayer:
    def __init__(self, player_id: int, name: str, word: str, role: str, model: str, local: bool):
        self.player_id = player_id
        self.name = name  # 玩家名称
        self.word = word  # 分配到的词语
        self.role = role  # "平民" 或 "卧底"
        self.is_alive = True
        self.impressions: Dict[int, str] = {}  # {其他玩家ID: 印象描述}
        self.player_rules = ""  # 玩家对游戏规则的理解
        self.player_map = {}  # 玩家映射 {玩家ID: AIPlayer实例}

        # 根据配置选择LLM客户端
        if local:
            self.llm_client: LLMClient = OllamaClient()
        else:
            self.llm_client: LLMClient = OpenAIClient()
        self.model = model

    def _try_correct_json(self, error_json: str) -> str:
        """
        尝试修正错误的JSON字符串，使用CORRECT_JSON_TEMPLATE提示词调用codellama:13b模型。
        返回模型生成的字符串。
        """
        prompt = CORRECT_JSON_TEMPLATE.format(error_json=error_json)
        content, _ = self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="codellama:13b"
        )
        return content.strip()
    

    def _parse_json_content(self, content: str, times=0) -> Dict:
        if times > 3:
            raise ValueError("解析JSON失败次数过多，可能是输入内容格式不正确")
        json_match = re.search(r'({[\s\S]*})', content)
        if json_match:
            json_str = json_match.group(1)
            try:
                result = json.loads(json_str)
            except:
                # 尝试修正JSON
                corrected = self._try_correct_json(json_str)
                result = self._parse_json_content(corrected, times + 1)
        else:
            # 尝试修正JSON
            corrected = self._try_correct_json(content)
            result = self._parse_json_content(corrected, times + 1)
        return result
                
    def generate_description(self) -> str:
        """生成对自己词语的描述"""
        # 准备模板变量
        template_vars = {
            "rules": RULES,
            "self_name": self.name,
            "player_rules": self.player_rules,
            "player_impressions": self._format_impressions(),
            "current_word": self.word
        }

        # 填充模板
        prompt = DESCRIPTION_TEMPLATE.format(**template_vars)

        # 调用LLM
        content, _ = self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.model
        )

        # 解析JSON响应
        try:
            response = self._parse_json_content(content)
            behavior = response.get("behavior", "")
            reason = response.get("reason", "")
            return behavior, reason
        except Exception as e:
            print(f"{self.name}响应解析失败: {str(e)}")
            # 备用方案
            backup_desc = content.strip()
            return backup_desc, f"{self.name}响应解析失败，原样输出模型返回内容"

    def vote(self, candidates: List[int], current_descriptions: Dict[int, str]) -> Tuple[int, str]:
        """投票选出怀疑的卧底"""
        # 准备模板变量
        template_vars = {
            "rules": RULES,
            "self_name": self.name,
            "alive_players": ', '.join(self.player_map[pid].name for pid in candidates),
            "player_descriptions": self._format_descriptions(current_descriptions),
            "player_rules": self.player_rules,
            "player_impressions": self._format_impressions(),
            "current_word": self.word
        }

        # 填充模板
        prompt = VOTE_TEMPLATE.format(**template_vars)

        # 调用LLM
        content, _ = self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.model
        )

        # 解析JSON响应
        try:
            response = self._parse_json_content(content)
            undercover_name = response["undercover_name"]
            reason = response["reason"]

            # 通过名称查找玩家ID
            for player_id in candidates:
                if self.player_map[player_id].name == undercover_name:
                    return player_id, reason

            # 如果找不到匹配名称，返回一个默认值
            return self.player_id, f"{self.name}没有返回正确的玩家名称，作为惩罚，投票给 {self.name}"
        except Exception as e:
            print(f"{self.name}响应解析失败: {str(e)}")
            # 备用方案
            return self.player_id, f"{self.name}响应解析失败，作为惩罚，投票给 {self.name}"

    def update_impressions(self, game_history: str):
        """根据游戏历史更新对其他玩家的印象"""
        # 先更新对其他玩家的印象
        for player_id in list(self.impressions.keys()):
            if player_id == self.player_id:
                continue

            # 准备模板变量
            template_vars = {
                "rules": RULES,
                "self_name": self.name,
                "player": self.player_map[player_id].name,
                "round_base_info": game_history,
                "round_action_info": self._get_action_info(player_id),
                "previous_impression": self.impressions.get(player_id, "暂无印象")
            }

            # 填充模板
            prompt = REFLECT_TEMPLATE.format(**template_vars)

            # 调用LLM
            content, _ = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model=self.model
            )

            # 更新印象
            self.impressions[player_id] = content.strip()

        # 然后更新对游戏规则的理解
        self._update_game_rules(game_history)

    def _update_game_rules(self, game_history: str):
        """更新玩家对游戏规则的理解"""
        # 准备模板变量
        template_vars = {
            "rules": RULES,
            "self_name": self.name,
            "player_descriptions": game_history,
            "player_rules": self.player_rules,
            "player_impressions": self._format_impressions()
        }

        # 填充模板
        prompt = ANALYZE_TEMPLATE.format(**template_vars)

        # 调用LLM
        content, _ = self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.model
        )

        # 更新规则理解
        self.player_rules = content.strip()

    def _format_impressions(self) -> str:
        """格式化印象信息"""
        return '\n'.join(
            f"{self.player_map[pid].name}: {imp}"
            for pid, imp in self.impressions.items() if pid != self.player_id
        ) or "暂无印象"

    def _format_descriptions(self, descriptions: Dict[int, str]) -> str:
        """格式化描述信息"""
        return '\n'.join(
            f"{self.player_map[pid].name}: {desc}"
            for pid, desc in descriptions.items() if pid != self.player_id
        )

    def _get_action_info(self, target_player_id: int) -> str:
        """获取目标玩家的行动信息"""
        return f"你正在分析 {self.player_map[target_player_id].name} 的行为模式、发言策略和投票倾向。"
