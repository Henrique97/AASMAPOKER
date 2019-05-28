from pypokerengine.api.emulator import Emulator
from honest_player_og import HonestPlayer
from random_player import RandomPlayer
from risky_player import RiskyPlayer
from qlearner import RLPlayer
import pandas as pd
import numpy as np

# 1. Set game settings on emulator
n_players = 2
emulator = Emulator()
quuid = "uuid-q"
qlearner_player = RLPlayer(n_players, quuid)
df1 = pd.DataFrame(columns = ['uuid', 'win_ratio', 'stack-diff'])
df2 = pd.DataFrame(columns = ['uuid', 'win_ratio', 'stack-diff'])
df3 = pd.DataFrame(columns = ['uuid', 'win_ratio', 'stack-diff'])
df4 = pd.DataFrame(columns = ['uuid', 'win_ratio', 'stack-diff'])
max_round = 50
learning_rates = np.arange(0.1, 1, 0.1)
#learning_rates = [0.3]
for j in learning_rates:
    qlearner_player = RLPlayer(n_players, quuid, j)
    for i in range(0, 150):
        emulator.register_player(uuid="uuid-1", player=HonestPlayer(n_players))
        #emulator.register_player(uuid="uuid-2", player=RiskyPlayer(n_players))
        emulator.register_player(uuid=quuid, player=qlearner_player)
        emulator.set_game_rule(player_num=n_players, max_round=max_round, small_blind_amount=20, ante_amount=0)
        players_info = {
            "uuid-1": { "name": "player1", "stack": 1000 },
            #"uuid-2": { "name": "player2", "stack": 1000 },
            quuid: { "name": "q-learning", "stack": 1000 }
        }
        initial_state = emulator.generate_initial_game_state(players_info)
        game_state, events = emulator.start_new_round(initial_state)

        game_finish_state, events = emulator.run_until_game_finish(game_state)
        qlearner_player.clear_stack()
        #[{'uuid': 'uuid-3', 'stack': 789}]
        win_ratio_dict = {"uuid-1" : 0, "uuid-2" : 0, "uuid-3" : 0, quuid : 0}
        final_stack_dict = {"uuid-1" : 0, "uuid-2" : 0, "uuid-3" : 0, quuid : 0}
        rounds_occ = 0
        for event in events:
            if (event['type'] == "event_round_finish"):
                rounds_occ += 1
                for winner in event['winners']:
                    win_ratio_dict[winner['uuid']] += 1
        for player in events[-1]['players']:
            final_stack_dict[player['uuid']] = player['stack']
        
        #df1=df1.append({'uuid' : "uuid-1" , 'win_ratio' : win_ratio_dict["uuid-1"]/(rounds_occ + 0.0), 'stack-diff' : j}, ignore_index=True)
        #df2=df2.append({'uuid' : "uuid-2" , 'win_ratio' : win_ratio_dict["uuid-2"]/(max_round + 0.0), 'stack_diff' : final_stack_dict['uuid-2']-1000}, ignore_index=True)
        #df4=df4.append({'uuid' : "uuid-q" , 'win_ratio' : win_ratio_dict["uuid-q"]/(rounds_occ + 0.0), 'stack-diff' : j}, ignore_index=True)
        #df1=df1.append({'uuid' : "uuid-1" , 'win_ratio' : win_ratio_dict["uuid-1"]/(max_round + 0.0), 'j' : j}, ignore_index=True)
        #df4=df4.append({'uuid' : "uuid-q" , 'win_ratio' : win_ratio_dict["uuid-q"]/(max_round + 0.0), 'j' : j}, ignore_index=True)
        print(events[-1])

#df1.to_csv("q-learnresults_1_honest_j.csv")
#df2.to_csv("q-learnresults_2_risky.csv")
#df4.to_csv("q-learnresults_4_honest_j.csv")
