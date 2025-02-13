from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000


class HonestPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
                )

        if win_rate >= 1.0 / self.nb_player:
            if win_rate >= 0.95:  # if win rate > 0.95 ALL-IN
                action = valid_actions[2]
                amount = action['amount']['max']
            else:
                action = valid_actions[1]  # fetch CALL action info
                amount = action['amount']
        elif hole_card[0][1] == 'A' and hole_card[1][1] == 'A': #if cards are Ace pair -> ALL-IN
            action = valid_actions[2]
            amount = action['amount']['max']
        else:
            action = valid_actions[0]  # fetch FOLD action info
            amount = action['amount']
        return action['action'], amount

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

