from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate, evaluate_hand
from pypokerengine.utils.game_state_utils import restore_game_state

import numpy as np
from random_player import RandomPlayer
import random as rand
import itertools

NB_SIMULATION = 10
QVALUE_MATRIX = np.random.randint(100, size = (108, 3) )
PLAYER_NUM = 0
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1


class RLPlayer(BasePokerPlayer):

    def __init__(self, nplayers, uuid):
        self._probability_cutoff = [0.2, 0.62, 0.92]
        self._stack_cutoff = [5, 20, 32.5]
        self._raise_cutoff = [4, 10, 20]
        self._stages = [0, 1, 2, 3]
        self._pot_cutoff = [4, 15, 32.5]
        #self.STATES = list(itertools.product(self._raise_cutoff, self._stages, self._probability_cutoff, self._pot_cutoff, self._stack_cutoff))
        self.STATES = list(itertools.product(self._raise_cutoff, self._stages, self._probability_cutoff, self._stack_cutoff))
        self.ACTIONS = ['FOLD','RAISE','CALL']
        self._pot = []
        self._previous_state = []
        self._stack = []
        self._uuid = uuid
        self._probabilities = []
        self._state = []
        self._raise = []
        self.nb_player = nplayers
        

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


    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        game_state = restore_game_state(round_state)
        big_blind = round_state['small_blind_amount'] * 2

        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card))

        if np.random.rand() <= EPSILON:
            choice = np.random.choice(["fold","call","raise"], 1)[0]
            print(valid_actions[2])
            if choice == "raise":
                #amount = rand.randrange(valid_actions[2]['amount']["min"], max(valid_actions[2]['amount']["min"], valid_actions[2]['amount']["max"]) + 1)
                #amount = valid_actions[2]['amount']['min']
                amount = np.random.randint(valid_actions[2]['amount']["min"],  valid_actions[2]['amount']["max"] + 1, 1)[0]
                print(amount)
                return 'raise', amount
            elif (choice == "fold"):
                return "fold", 0
            elif (choice == "call"):
                return "call", valid_actions[1]['amount']

        self._probabilities.append([win_rate, round_state['street']])
        self._pot.append(round_state['pot']['main']['amount'] / big_blind)
        my_stack = 0
        for i in range(0, len(round_state['seats'])):
            if (round_state['seats'][i]['name'] == 'q-learning'):
                my_stack = round_state['seats'][i]['stack']
                self._stack.append(my_stack)

        # GET RAISED AMOUNT AND STAGES
        total_raised_amount = 0
        for i in ["preflop", "flop", "turn", "river"]:
            if (i in round_state['action_histories']):
                for y in round_state['action_histories'][i]:
                    if (y['uuid'] == self._uuid):
                        self._previous_state.append([y['action'], ["preflop", "flop", "turn", "river"].index(i)])
                    if (y['action'] == 'RAISE' and y['uuid'] != self._uuid):
                        total_raised_amount += y['amount']

        total_raised_amount = (total_raised_amount / self.nb_player) / big_blind

        for i in range(0, len(self._raise_cutoff)):
            if ( i == len(self._raise_cutoff) - 1):
                self._raise.append(self._raise_cutoff[i])
            elif ( total_raised_amount >= self._raise_cutoff[i] ):
                continue
            else:
                self._raise.append(self._raise_cutoff[i])
                break
        
        # GET PRESENT POT
        for i in range(0, len(self._pot_cutoff)):
            if ( i == len(self._pot_cutoff) - 1):
                self._pot[-1] = self._pot_cutoff[i]
            elif ( self._pot[-1] >= self._pot_cutoff[i] ):
                continue
            else:
                self._pot[-1] = self._pot_cutoff[i]
                break

        # DISCRETIZE PRESENT STACK
        for i in range(0, len(self._stack_cutoff)):
            if ( i == len(self._stack_cutoff) - 1):
                self._stack[-1] = self._stack_cutoff[i]
            elif ( self._stack[-1] >= self._stack_cutoff[i] ):
                continue
            else:
                self._stack[-1] = self._stack_cutoff[i]
                break
        
        # DISCRETIZE PROBABILITIES
        for i in range(0, len(self._probability_cutoff)):
            if ( i == len(self._probability_cutoff) - 1):
                self._probabilities[-1][0] = self._probability_cutoff[i]
            elif ( self._probabilities[-1][0] >= self._probability_cutoff[i] ):
                continue
            else:
                self._probabilities[-1][0] = self._probability_cutoff[i]
                break 

        if (len(self._stack) > 1):
            self.update_qmatrix()

        #present_state = self.STATES.index( (self._raise[-1], ["preflop", "flop", "turn", "river"].index(self._probabilities[-1][1]), self._probabilities[-1][0], self._pot[-1], self._stack[-1]) )
        present_state = self.STATES.index( (self._raise[-1], ["preflop", "flop", "turn", "river"].index(self._probabilities[-1][1]), self._probabilities[-1][0], self._stack[-1]) )
        #present_state = self.STATES.index( (self._probabilities[-1][0]) )
        action_todo = self.ACTIONS[np.argmax(QVALUE_MATRIX[present_state])]
        #print("**************************", action_todo)
        #print(QVALUE_MATRIX[0], self._stack[-1])
        if (action_todo == 'FOLD'):
            return "fold", 0
        elif (action_todo == 'CALL'):
            return "call", valid_actions[1]['amount']
        else:
            #avg_raise = (valid_actions[2]['amount']['max'] + valid_actions[2]['amount']['min']) / 2.0
            #if (avg_raise/3 <= 0):
            #    return "raise", valid_actions[2]['amount']['min']
            #raise_amount = int(np.random.poisson(avg_raise/200, 1))
            raise_amount = valid_actions[2]['amount']['min']
            print("raise_amount",raise_amount)
            #print(raise_amount)
            return "raise", raise_amount

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def update_qmatrix(self):
        i = -1
        #print(self._stack)
        reward = self._stack[-1] - self._stack[-2]
        #index = self.STATES.index( (self._raise[i], self._previous_state[i][1], self._probabilities[i][0], self._pot[i], self._stack[i]) )
        index = self.STATES.index( (self._raise[i], self._previous_state[i][1], self._probabilities[i][0], self._stack[i]) )
        #index = self.STATES.index( (self._probabilities[i][0]) )
        if (i+1 == len(self._probabilities)):
            index_next_state = index
        else:
            #index_next_state = self.STATES.index( (self._raise[i+1], self._previous_state[i+1][1], self._probabilities[i+1][0], self._pot[i+1], self._stack[i+1]) )
            index_next_state = self.STATES.index( (self._raise[i+1], self._previous_state[i+1][1], self._probabilities[i+1][0], self._stack[i+1]) )
            #index_next_state = self.STATES.index( (self._probabilities[i+1][0]) )
        if ( (self._previous_state[i][0] == "SMALLBLIND") or (self._previous_state[i][0] == "BIGBLIND") ):
            self._previous_state[i][0] = "CALL"
        action = self.ACTIONS.index(self._previous_state[i][0])
        maxi = np.amax(QVALUE_MATRIX[index_next_state])
        QVALUE_MATRIX[index][action] = QVALUE_MATRIX[index][action] + ALPHA * (reward + GAMMA * maxi - QVALUE_MATRIX[index][action])
    
    def clear_stack(self):
        self._probabilities = []
        self._stack = []
        self._raise = []
        self._pot = []
        self._previous_state = []
        self._raise = []