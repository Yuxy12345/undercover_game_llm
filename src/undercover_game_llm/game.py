import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from player import AIPlayer


# 导入玩家配置
from player_configs import player_configs

class UndercoverGame:
    def __init__(self, player_map: Optional[Dict[int, AIPlayer]] = None, game_id: Optional[int] = 1):
        self.game_id = game_id
        self.civilian_word = ""
        self.undercover_word = ""
        self.game_history: List[Dict] = []
        self.current_descriptions: Dict[int, str] = {}
        self.current_round = 1
        self.find_undercover = False
        if player_map:
            self.player_map = player_map
            self._reassign_players()
        else:
            self.player_map: Dict[int, AIPlayer] = {}
            self._initialize_players()
            self._reassign_players()

    @property
    def undercover_names(self):
        """返回所有卧底玩家的名字"""
        return [player.name for player in self.player_map.values() if player.role == "卧底"]

    def _reassign_players(self):
        """重新分配玩家角色和词语"""
        # 从gamewords.json随机选择一组词语
        with open("conf/gamewords.json", "r", encoding="utf-8") as f:
            all_word_pairs = json.load(f)
        word_pair = random.choice(all_word_pairs)
        self.civilian_word = word_pair[0]
        self.undercover_word = word_pair[1]
        self.undercover_id = random.choice(list(self.player_map.keys()))
        for player in self.player_map.values():
            role = "卧底" if player.player_id == self.undercover_id else "平民"
            word = self.undercover_word if role == "卧底" else self.civilian_word
            player.role = role
            player.word = word
            player.is_alive = True  # 重置玩家状态

    def _initialize_players(self):
        """初始化玩家并分配角色"""
        for i, config in enumerate(player_configs):
            pid = i
            player = AIPlayer(
                player_id=pid,
                name=config["name"],
                word="",
                role="平民",  # 初始角色为平民，后续会重新分配
                model=config["model"],
                local=config["local"]
            )
            self.player_map[pid] = player
        
        # 初始化印象
        for player in self.player_map.values():
            player.player_map = self.player_map
            player.impressions = {
                other_pid: f"新玩家，尚无足够信息" 
                for other_pid in range(len(self.player_map))
                if other_pid != player.player_id
            }
        

    def _record_event(self, event: str, private: bool = False):
        """记录游戏事件"""
        self.game_history.append({"round": self.current_round, "event": event, "private": private})
        print(f"[第 {self.game_id} 局][回合 {self.current_round}] {event}")

    def _get_alive_players(self) -> List[AIPlayer]:
        """获取当前存活的玩家列表"""
        return [p for p in self.player_map.values() if p.is_alive]
    
    def _get_round_history_summary(self, ignore_private: bool) -> str:
        """获取当前回合历史记录的摘要"""
        return "\n".join(f"- {event['event']}" for event in self.game_history if event['round'] == self.current_round and (not ignore_private or not event['private']))

    def description_phase(self):
        """进行描述阶段，生成玩家描述"""
        self.current_descriptions = {}
        alive_players = self._get_alive_players()
        random.shuffle(alive_players)
        
        for player in alive_players:
            behavior, reason = player.generate_description()
            self.current_descriptions[player.player_id] = behavior
            self._record_event(f"{player.name} 描述: {behavior}")
            self._record_event(f"理由: {reason}", private=True)
    
    def voting_phase(self) -> Tuple[Optional[int], Optional[List[int]]]:
        """进行投票阶段，返回被淘汰的玩家ID, 以及可能平票的候选列表"""
        alive_players = self._get_alive_players()
        votes: Dict[int, int] = {}
        reasons: Dict[int, str] = {}
        
        for voter in alive_players:
            candidates = [p.player_id for p in alive_players if p != voter]
            vote_id, reason = voter.vote(candidates, self.current_descriptions)
            
            votes[vote_id] = votes.get(vote_id, 0) + 1
            reasons[voter.player_id] = f"{voter.name}投了{self.player_map[vote_id].name}， 理由: {reason}"
            self._record_event(reasons[voter.player_id])
        
        if not votes:
            return None, None
        
        max_votes = max(votes.values())
        max_candidates = [pid for pid, count in votes.items() if count == max_votes]
        
        if len(max_candidates) > 1:
            candidate_names = [self.player_map[pid].name for pid in max_candidates]
            self._record_event(f"平票！进入PK轮：{', '.join(candidate_names)}")
            return None, max_candidates
        
        eliminated = max_candidates[0]
        self._record_event(f"{self.player_map[eliminated].name} 被淘汰（{self.player_map[eliminated].role}）（得票: {max_votes}）")
        return eliminated, None
    
    def pk_voting_phase(self, candidates: List[int]) -> Optional[int]:
        """进行PK投票阶段，返回被淘汰的玩家ID"""
        candidate_names = [self.player_map[pid].name for pid in candidates]
        self._record_event(f"PK轮：请从 {', '.join(candidate_names)} 中选择")
        
        alive_players = self._get_alive_players()
        votes: Dict[int, int] = {pid: 0 for pid in candidates}
        
        for voter in alive_players:
            vote_id, reason = voter.vote(candidates, self.current_descriptions)
            if vote_id in candidates:
                votes[vote_id] += 1
                self._record_event(f"{voter.name}投了{self.player_map[vote_id].name}， 理由: {reason}")
        
        max_votes = max(votes.values())
        max_candidates = [pid for pid, count in votes.items() if count == max_votes]
        
        if len(max_candidates) > 1:
            eliminated = random.choice(max_candidates)
            self._record_event(f"再次平票！随机淘汰 {self.player_map[eliminated].name}")
            return eliminated
        
        eliminated = max_candidates[0]
        self._record_event(f"{self.player_map[eliminated].name} 被淘汰（{self.player_map[eliminated].role}）（得票: {max_votes}）")
        return eliminated

    def update_impressions(self):
        history_summary = self._get_round_history_summary(True)
        self._record_event("===== 更新印象阶段开始 =====")
        for player in self.player_map.values():
            player.update_impressions(history_summary)
            formatted_impressions = "\n".join(
                f"{self.player_map[key].name}: {msg}" for key, msg in player.impressions.items()
            )
            self._record_event(f"{player.name} 更新印象: \n{formatted_impressions}")
            self._record_event(f"{player.name} 更新规则理解: \n{player.player_rules}")
    
    def play_round(self):
        """进行一轮游戏"""
        self._record_event(f"===== 第 {self.current_round} 轮开始 =====")
        self._record_event(f"回合开始！平民词: {self.civilian_word}, 卧底词: {self.undercover_word}", private=True)
        self._record_event(f"当前存活玩家: {', '.join(player.name for player in self._get_alive_players())}")
        self._record_event(f"卧底玩家: {', '.join(self.undercover_names)}", private=True)
        self._record_event("===== 描述阶段开始 =====")
        self.description_phase()
        
        self._record_event("===== 投票阶段开始 =====")
        eliminated, max_candidates = self.voting_phase()
        
        if eliminated is None:
            eliminated = self.pk_voting_phase(max_candidates)
        
        self.player_map[eliminated].is_alive = False

        if self.player_map[eliminated].role == "卧底":
            self.find_undercover = True

        if self.check_game_end():
            winner = self._get_alive_players()
            if winner:
                role = "平民" if self.find_undercover else "卧底"
                winner_names = [p.name for p in winner if p.role == role]
                winners_info = ", ".join([f"{name}" for name in winner_names])
                winners_log = f"游戏结束！获胜者：{winners_info} （{role}）"
                self._record_event(winners_log)
                self.game_result = {
                    "winners": winner_names,
                    "role": role,
                    "game_history": self.game_history
                }
            else:
                winners_log = "游戏结束！无人获胜"
                self._record_event(winners_log)
                self.game_result = {    
                    "winners": [],
                    "role": "",
                    "game_history": self.game_history
                }

        self.update_impressions()
        self.current_round += 1
    
    def check_game_end(self) -> bool:
        """检查游戏是否结束"""
        # 游戏结束条件：存活玩家少于等于2人（少于2人代表卧底活到最后2人没找到，最后互相指正无意义），或者找到卧底
        return len(self._get_alive_players()) <= 2 or self.find_undercover
    
    def start_game(self):
        """开始游戏"""
        while not self.check_game_end():
            self.play_round()
        
        self.save_results()

    def save_results(self):
        """保存游戏结果到文件"""
        import os
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("../../results", exist_ok=True)
        filename = f"results/result_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.game_result, f, ensure_ascii=False, indent=4)
        print(f"结果已保存到 {filename}")
            
if __name__ == "__main__":
    game = UndercoverGame()
    game.start_game()
