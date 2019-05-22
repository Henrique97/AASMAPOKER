from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 500


class BluffPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=2,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        can_raise = len([item for item in valid_actions if item['action'] == 'raise']) > 0

        if win_rate >= 1.0 / 2:
            if win_rate > 0.6:
                if can_raise:
                    action = valid_actions[2]
                    amount = action['amount']['min']
                else:
                    action = valid_actions[1]
                    amount = action['amount']
            else:
                action = valid_actions[1]
                amount = action['amount']
        else:
            action = valid_actions[0]  # fetch FOLD action info
            amount = 0
        return action['action'], amount  # action returned here is sent to the poker engine

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
