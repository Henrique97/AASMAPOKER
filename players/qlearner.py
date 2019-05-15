from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.utils.game_state_utils import restore_game_state

import numpy as np
from random_player import RandomPlayer
import itertools

NB_SIMULATION = 100
QVALUE_MATRIX = np.random.randint(40, size = (8960, 3) )
PLAYER_NUM = 0


class RLPlayer(BasePokerPlayer):

    def __init__(self):
        self._probability_cutoff = [0.2, 0.5, 0.75, 0.92]
        self._stack_cutoff = [5, 10, 15, 20, 25, 32.5, 40]
        self._raise_cutoff = [1, 2, 4, 5, 10, 15, 20, 25]
        self._stages = [0, 1, 2, 3]
        self._pot_cutoff = [1, 2, 4, 5, 10, 15, 20, 25, 32.5, 40]
        self.STATES = list(itertools.product(self._raise_cutoff, self._stages, self._probability_cutoff, self._pot_cutoff, self._stack_cutoff))
        self.ACTIONS = ['FOLD','BIGBLIND','RAISE','SMALLBLIND','CALL']
        self._pot = []
        self._previous_state = []
        self._stack = []
        self._uuid = ""
        self._probabilities = []
        self._state = []
        self._raise = []


    def qmatrix (self, valid_actions, hole_card, state):
        n_players = 2
        initial_player_stack = n_players * 1000
        
        my_uuid = state['seats'][ state['next_player'] ]['uuid']
        
        bb_amount = state['small_blind_amount'] * 2

        #feature_arrays = [hole_values, hole_suits, river_values, 
        # river_suits, total_pot_as_bb, own_stack_size, other_players_stack_sizes,
        #  player_folds, money_since_our_last_move, amt_to_call, min_raise, max_raise]

        probability = [0.2, 0.5, 0.75, 0.92]

        #pot size
        total_main_amount = state['pot']['main']['amount'] / bb_amount
        my_pot_size = 0
        pot_cutoff = [1, 2, 4, 5, 10, 15, 20, 25, 32.5, 40]
        for i in range(0, len(pot_cutoff)):
            if ( i == len(pot_cutoff) - 1):
                my_pot_size = i
            elif ( my_pot_size >= pot_cutoff[i] ):
                continue
            else:
                my_pot_size = i
                break

        #total_side_pot = sum([a['amount'] for a in state['pot']['side']])
        #total_pot_as_bb = [(total_main_amount + total_side_pot) / bb_amount]

        #my stack size
        my_stack_size = state['seats'][ state['next_player'] ]['stack'] / bb_amount
        stack_cutoff = [5, 10, 15, 20, 25, 32.5, 40]
        for i in range(0, len(stack_cutoff)):
            if ( i == len(stack_cutoff) - 1):
                my_stack_size = i
            elif ( my_stack_size >= stack_cutoff[i] ):
                continue
            else:
                my_stack_size = i
                break

        #others stack size
        #other_stack = p['stack'] / bb_amount for p in game_state['seats'][player_idx + 1:]
        stack_list = []
        for player_info in state['seats']:
            if (player_info['uuid'] == my_uuid):
                continue
            stack_list.append(player_info['stack'])

        #get stage "preflop", "flop", "turn", "river"
        stages = ["preflop", "flop", "turn", "river"]
        present_stage = stages.index( state['street'] )

        #get max raise
        raise_max = valid_actions[2]['amount']['max'] / bb_amount
        raise_cutoff = [1, 2, 4, 5, 10, 15, 20, 25]
        for i in range(0, len(raise_cutoff)):
            if ( i == len(raise_cutoff) - 1):
                raise_max = i
            elif ( raise_max >= raise_cutoff[i] ):
                continue
            else:
                raise_max = i
                break

        np.random.randint(5, size=(2, 4))
        states = list(itertools.product(raise_cutoff, stages, probability, pot_cutoff, stack_cutoff))
        qmatrix = np.random.randint(40, size = (len(states), 3) )
        return [my_stack_size, total_main_amount, stack_list, present_stage]

    # Setup Emulator object by registering game information
    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        global PLAYER_NUM
        PLAYER_NUM = game_info["player_num"]
        max_round = game_info["rule"]["max_round"]
        small_blind_amount = game_info["rule"]["small_blind_amount"]
        ante_amount = game_info["rule"]["ante"]
        blind_structure = game_info["rule"]["blind_structure"]

        for i in range(0, len(game_info['seats'])):
            if (game_info['seats'][i]['name'] == 'q-learning'):
                self._uuid = game_info['seats'][i]['uuid']

        self.emulator = Emulator()
        self.emulator.set_game_rule(PLAYER_NUM, max_round, small_blind_amount, ante_amount)
        self.emulator.set_blind_structure(blind_structure)
        print(PLAYER_NUM)
        # Register algorithm of each player which used in the simulation.
        for player_info in game_info["seats"]:
            self.emulator.register_player(player_info["uuid"], RandomPlayer())

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        game_state = restore_game_state(round_state)
        big_blind = round_state['small_blind_amount'] * 2
        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
                )
        self._probabilities.append([win_rate, round_state['street']])
        self._pot.append(round_state['pot']['main']['amount'] / big_blind)
        my_stack = 0
        for i in range(0, len(round_state['seats'])):
            if (round_state['seats'][i]['name'] == 'q-learning'):
                my_stack = round_state['seats'][i]['stack']
                self._stack.append(my_stack)
        
        # GET RAISED AMOUNT
        total_raised_amount = 0
        total_raised_amount = (total_raised_amount / PLAYER_NUM) / big_blind

        for i in range(0, len(self._raise_cutoff)):
            if ( i == len(self._raise_cutoff) - 1):
                self._raise.append(i)
            elif ( total_raised_amount >= self._raise_cutoff[i] ):
                continue
            else:
                self._raise.append(i)
                break


        if self.simul_result(round_state):
            return "call", 10
        else:
            return "fold", 0

    def simul_result(self, state):
        return True
    

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(round_state)

        present_stack = -1
        for i in range(0, len(round_state['seats'])):
            if (round_state['seats'][i]['name'] == 'q-learning'):
                present_stack = round_state['seats'][i]['stack']
        #print(round_state)

        for i in ["preflop", "flop", "turn", "river"]:
            if (i in round_state['action_histories']):
                for y in round_state['action_histories'][i]:
                    if (y['uuid'] == self._uuid):
                        self._previous_state.append([y['action'], i])
                    if (y['action'] == 'RAISE' and y['uuid'] != self._uuid):
                        total_raised_amount += y['amount']
        #print(round_state)
        big_blind = round_state['small_blind_amount'] * 2
            
        # GET PROBABILITIES
        probability_index = []
        for prob in range(0, len(self._probabilities)):
            for i in range(0, len(self._probability_cutoff)):
                if ( i == len(self._probability_cutoff) - 1):
                    #probability_index.append(i)
                    self._probabilities[prob][0] = i
                elif ( self._probabilities[prob][0] >= self._probability_cutoff[i] ):
                    continue
                else:
                    #probability_index.append(i)
                    self._probabilities[prob][0] = i
                    break 

        # GET POT
        pot_index = []

        for s in range(0, len(self._pot)):
            for i in range(0, len(self._pot_cutoff)):
                if ( i == len(self._pot_cutoff) - 1):
                    self._pot[s] = i
                elif ( self._pot[s] >= self._pot_cutoff[i] ):
                    continue
                else:
                    self._pot[s] = i
                    break
        
        # DISCRETIZE STACK
        stack_index = []
        for s in range(0, len(self._stack)):
            for i in range(0, len(self._stack_cutoff)):
                if ( i == len(self._stack_cutoff) - 1):
                    self._stack[s] = i
                elif ( self._stack[s] >= self._stack_cutoff[i] ):
                    continue
                else:
                    self._stack[s] = i
                    break
        
        # BUILD STATES
        print("OS")
        print(self._probabilities)
        for i in range(0, len(self._probabilities)):
            print(len(self._probabilities), len(self._raise), len(self._pot), len(self._stack))
        print("END ERGO")

        if (len(self._stack) > 0):
            reward = present_stack - self._stack[-1]
        self._stack = []
        self._previous_state = []
        self._probabilities = []
        self._pot = []
        self._raise = []

        pass
