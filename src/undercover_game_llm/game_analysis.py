import json
import os
from typing import Dict

from player import AIPlayer


def read_json_from_file(file_name):
    """从文件中读取内容"""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"警告: 文件 {file_name} 不存在")
        return None
    except Exception as e:
        print(f"警告: 无法读取文件 {file_name}，错误: {e}")
        return None
    
def batch_get_game_results():
    """批量获取游戏结果"""
    game_results = []
    # 游戏结果存在results/result_*.json文件中，读取所有符合条件的文件
    result_dir = "results"
    if not os.path.exists(result_dir):
        print(f"警告: 结果目录 {result_dir} 不存在")
        return game_results
    for file_name in os.listdir(result_dir):
        if file_name.startswith("result_") and file_name.endswith(".json"):
            file_path = os.path.join(result_dir, file_name)
            result = read_json_from_file(file_path)
            if result:
                game_results.append(result)
    return game_results

def print_game_winners_table(game_results):
    print("\n-- 游戏胜利者表 --")
    print("{:<6} {:<38} {:<4}".format("局数", "赢家", "角色"))
    for idx, result in enumerate(game_results, 1):
        winner = result.get("winners", "N/A")
        role = result.get("role", "N/A")
        if isinstance(winner, list):
            winner_str = ", ".join(str(w) for w in winner)
        else:
            winner_str = str(winner)
        print("{:<8} {:<40} {:<4}".format(idx, winner_str, role))


def print_player_win_stats(player_map, game_results):
    # 统计每个玩家作为每个角色的胜出次数
    stats = {}
    for player in player_map.values():
        stats[player.name] = {"卧底": 0, "平民": 0}  # 初始化每个玩家的统计信息
    for result in game_results:
        winner = result.get("winners")
        role = result.get("role")
        if winner is None or role is None:
            continue
        for w in winner:
            if w not in stats:
                stats[w] = {"卧底": 0, "平民": 0}  # 初始化玩家统计信息
            stats[w][role] = stats[w].get(role, 0) + 1
    # 统计每个玩家的总数
    for player, role_counts in stats.items():
        role_counts["总数"] = sum(role_counts.values())  # 计算总数
    # stats根据总数、卧底和平民的数量进行降序排序
    sorting_keys = [(player, role_counts["总数"], role_counts["卧底"], role_counts["平民"]) for player, role_counts in stats.items()]
    sorting_keys.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)
    stats = {item[0]: stats[item[0]] for item in sorting_keys}
    # 打印表格
    print("\n-- 玩家胜利统计 --")
    roles = sorted({key for player_roles in stats.values() for key in player_roles.keys()})
    header = "{:<13}{:<4}{:<4}{:<4}".format("玩家", "总数", "卧底", "平民")
    print(header)
    for player, role_counts in stats.items():
        row = "{:<15}".format(player)
        row += "{:<6}".format(role_counts.get("总数", 0))
        row += "{:<6}".format(role_counts.get("卧底", 0))
        row += "{:<6}".format(role_counts.get("平民", 0))
        print(row)

def get_player_map_from_results(game_results):
    """从游戏结果中提取玩家映射"""
    player_map: Dict[int, AIPlayer] = {}
    player_id = 0
    for result in game_results:
        for player in result.get("winners", []):
            if player_id is not None and player_id not in player_map:
                # 创建AIPlayer实例
                player_map[player_id] = AIPlayer(
                    player_id=player_id,
                    name=player,
                    word="",
                    role="平民",
                    model="default_model",
                    local=True
                )
                player_id += 1
    return player_map

if __name__ == "__main__":
    # 示例用法
    game_results = batch_get_game_results()
    player_map = get_player_map_from_results(game_results)
    
    if game_results and player_map:
        print_game_winners_table(game_results)
        print_player_win_stats(player_map, game_results)
    else:
        print("无法打印游戏结果或玩家统计信息，请检查文件是否存在或格式是否正确。")
