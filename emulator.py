from pypokerengine.api.emulator import Emulator
from honest_player import HonestPlayer
from qlearner import RLPlayer

# 1. Set game settings on emulator
n_players = 4
emulator = Emulator()
quuid = "uuid-q"
qlearner_player = RLPlayer(n_players, quuid)
for i in range(0, 60):
    emulator.register_player(uuid="uuid-1", player=HonestPlayer(n_players))
    emulator.register_player(uuid="uuid-2", player=HonestPlayer(n_players))
    emulator.register_player(uuid="uuid-3", player=HonestPlayer(n_players))
    emulator.register_player(uuid=quuid, player=qlearner_player)
    emulator.set_game_rule(player_num=4, max_round=100, small_blind_amount=20, ante_amount=0)
    # 2. Setup GameState object
    players_info = {
        "uuid-1": { "name": "player1", "stack": 1000 },
        "uuid-2": { "name": "player2", "stack": 1000 },
        "uuid-3": { "name": "player3", "stack": 1000 },
        quuid: { "name": "q-learning", "stack": 1000 }
    }
    initial_state = emulator.generate_initial_game_state(players_info)
    game_state, events = emulator.start_new_round(initial_state)
    # 3. Run simulation and get updated GameState object
    game_finish_state, events = emulator.run_until_game_finish(game_state)
    qlearner_player.clear_stack()
    print(events[-1])