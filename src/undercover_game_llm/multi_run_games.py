from game import UndercoverGame
import sys

from game_analysis import print_game_winners_table, print_player_win_stats

def multi_run_games(num_runs):
    player_map = None
    game_results = []
    # 运行多次游戏
    for i in range(num_runs):
        print(f"-- 运行第 {i + 1} / {num_runs} 次游戏 --")
        game = UndercoverGame(player_map=player_map, game_id=i + 1)
        game.start_game()
        player_map = game.player_map
        game_results.append(game.game_result)
    return player_map, game_results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])
    else:
        num_runs = 1  # 默认运行1次
    final_player_map, final_game_results = multi_run_games(num_runs)
    print_game_winners_table(final_game_results)
    print_player_win_stats(final_player_map, final_game_results)
