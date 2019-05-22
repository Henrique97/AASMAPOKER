from pypokerengine.api.emulator import Emulator
from players.honest_player_og import HonestPlayer
from players.qlearner import RLPlayer
from players.random_player import RandomPlayer
from players.risky_player import RiskyPlayer
import pandas as pd

# 1. Set game settings on emulator
n_players = 2
emulator = Emulator()
#quuid = "uuid-q"
p_uuid=["low-iq","high-iq","low-iq2","uuid-4"]
#qlearner_player = RLPlayer(n_players, quuid)
df = pd.DataFrame(columns = ['uuid', 'stack', 'game'])
for i in range(0, 60):
	print("starting game " + str(i))
	df1 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
	df2 = pd.DataFrame(columns = ['uuid', 'stack', 'round'])
	emulator.register_player(uuid=p_uuid[0], player=HonestPlayer(n_players,10000))
	emulator.register_player(uuid=p_uuid[1], player=HonestPlayer(n_players,1000))
	emulator.set_game_rule(player_num=2, max_round=10000, small_blind_amount=20, ante_amount=0)
	# 2. Setup GameState object
	players_info = {
		p_uuid[0]: { "name": "player1", "stack": 100000 },
		p_uuid[1]: { "name": "player2", "stack": 100000 }
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
				#elif(player['uuid']==p_uuid[2]):
				#	df3=df3.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
				#elif(player['uuid']==p_uuid[3]):
				#	df4=df4.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'round' : event['round_state']['round_count']} , ignore_index=True)
						
	for player in events[-1]['players']:
		df = df.append({'uuid' : player['uuid'] , 'stack' : player['stack'], 'game' : i} , ignore_index=True)
	df1.to_csv("job2/2gameAllroundsP1" + str(i) + ".csv")
	df2.to_csv("job2/2gameAllroundsP2"+ str(i) + ".csv")

df.to_csv("job2/2gameresults.csv")

#df3.to_csv("gameAllroundsP3.csv")
#df4.to_csv("gameAllroundsP4.csv")

