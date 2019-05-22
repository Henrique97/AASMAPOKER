from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000


class RiskyPlayer(BasePokerPlayer):

	def __init__(self, n_players=4,sims=500,perc_risk=0.7):
		self.nb_player = n_players
		self.sims = sims
		self.risk = perc_risk
	
	def declare_action(self, valid_actions, hole_card, round_state):
		community_card = round_state['community_card']
		win_rate = estimate_hole_card_win_rate(
				nb_simulation=self.sims,
				nb_player=self.nb_player,
				hole_card=gen_cards(hole_card),
				community_card=gen_cards(community_card)
				)
				
		can_raise = len([item for item in valid_actions if item['action'] == 'raise']) > 0
		amount=0
		if win_rate >= 0.8:
			if can_raise:
				action = valid_actions[2]
				amount = (action['amount']['min'] + action['amount']['max']) /2.0
			else:
				action = valid_actions[1]
				amount = action['amount']
		elif win_rate >= self.risk / self.nb_player and len(round_state['community_card'])!=5:
			action = valid_actions[1]  # fetch CALL action info
			amount = action['amount']
		else:
			action = valid_actions[0]  # fetch FOLD action info
			amount = action['amount']
		return action['action'], amount

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
	
	def setup_ai():
		return FishPlayer()
