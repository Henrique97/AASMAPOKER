from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000


class RiskyPlayer(BasePokerPlayer):

	def __init__(self, n_players):
		self.nb_player = n_players
	
	def declare_action(self, valid_actions, hole_card, round_state):
		community_card = round_state['community_card']
		win_rate = estimate_hole_card_win_rate(
				nb_simulation=NB_SIMULATION,
				nb_player=self.nb_player,
				hole_card=gen_cards(hole_card),
				community_card=gen_cards(community_card)
				)
		if win_rate >= 1.0 / self.nb_player:
			action = valid_actions[1]  # fetch CALL action info
		elif win_rate >= 0.80 / self.nb_player and len(round_state['community_card'])==5:
			action = valid_actions[1]  # fetch CALL action info
		else:
			action = valid_actions[0]  # fetch FOLD action info
		return action['action'], action['amount']

	def receive_game_start_message(self, game_info):
		pass
	
	def receive_round_start_message(self, round_count, hole_card, seats):
		pass
	
	def receive_street_start_message(self, street, round_state):
		self.risk=(self.risk+1)%5
	
	def receive_game_update_message(self, action, round_state):
		pass
	
	def receive_round_result_message(self, winners, hand_info, round_state):
		self.risk=1
	
