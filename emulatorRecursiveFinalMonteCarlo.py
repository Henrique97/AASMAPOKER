from pypokerengine.api.emulator import Emulator
from players.honest_player_og import HonestPlayer
from players.qlearner import RLPlayer
from players.random_player import RandomPlayer
from players.risky_player import RiskyPlayer
import pandas as pd

# 1. Set game settings on emulator
n_players = 4
j=0
emulator = Emulator()
#quuid = "uuid-q"
p_uuid=["high-iq","low-iq","low-iq2","low-iq3"]
#qlearner_player = RLPlayer(n_players, quuid)
monte_carlos_tries=[[10,10],[10,20],[10,30],[10,50],[10,100],[10,200],[10,400],[10,800],[10,1000],[10,1500]]
for tryM in monte_carlos_tries:
	df = pd.DataFrame(columns = ['uuid', 'stack', 'game'])
	for i in range(0,2):
		print("starting game " + str(i) + " from try " + str(j))
		df1 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
		df2 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
		df3 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
		df4 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
		emulator.register_player(uuid=p_uuid[0], player=RiskyPlayer(n_players,tryM[1],0.7))
		emulator.register_player(uuid=p_uuid[1], player=RiskyPlayer(n_players,tryM[0],0.7))
		emulator.register_player(uuid=p_uuid[2], player=RiskyPlayer(n_players,tryM[0],0.7))
		emulator.register_player(uuid=p_uuid[3], player=RiskyPlayer(n_players,tryM[0],0.7))
		emulator.set_game_rule(player_num=4, max_round=1000, small_blind_amount=20, ante_amount=0)
		# 2. Setup GameState object
		players_info = {
			p_uuid[0]: { "name": "player1", "stack": 10000 },
			p_uuid[1]: { "name": "player2", "stack": 10000 },
			p_uuid[2]: { "name": "player3", "stack": 10000 },
			p_uuid[3]: { "name": "player4", "stack": 10000 },
		}
		initial_state = emulator.generate_initial_game_state(players_info)
		game_state, events = emulator.start_new_round(initial_state)
		# 3. Run simulation and get updated GameState object
		game_finish_state, events = emulator.run_until_game_finish(game_state)
		#qlearner_player.clear_stack()
		for event in events:
			if(event['type']=="event_round_finish"):
				for player in event['round_state']['seats']:
					if(player['uuid']==p_uuid[0]):
						df1=df1.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
					elif(player['uuid']==p_uuid[1]):
						df2=df2.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
					elif(player['uuid']==p_uuid[2]):
						df3=df3.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
					elif(player['uuid']==p_uuid[3]):
						df4=df4.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
							
		for player in events[-1]['players']:
			df = df.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'game' : i} , ignore_index=True)
		df1.to_csv("recJob4/gameAllroundsP1_try_" + str(tryM[1]) + "_game_" + str(i) + ".csv")
		df2.to_csv("recJob4/gameAllroundsP2_try_"+ str(tryM[1]) + "_game_" + str(i) + ".csv")
		df3.to_csv("recJob4/gameAllroundsP3_try_"+ str(tryM[1]) + "_game_" + str(i) + ".csv")
		df4.to_csv("recJob4/gameAllroundsP4_try_"+ str(tryM[1]) + "_game_" + str(i) + ".csv")
	df.to_csv("recJob4/gameresults_try" + str(tryM[1]) + ".csv")
	j+=1
