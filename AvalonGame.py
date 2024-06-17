import random

class AvalonGame:
    def __init__(self, players, roles=None):
        if len(players) not in [5, 6, 7, 8, 9, 10]:
            raise ValueError("Must have between 5 and 10 players.")
        
        if len(players) != len(set(players)):
            raise ValueError("Players must be unique.")
        
        if roles is not None:
            if len(roles) != len(players):
                raise ValueError("Roles must be None or a list of length equal to players.")
            if any([c not in ["Mordred", "Morgana", "Assassin", "Oberon", "Minion", "Merlin", "Percival", "Knight"] for c in roles]):
                raise ValueError("Unrecognized roles.")
        
        self.mission_participants = {
            5: [2, 3, 2, 3, 3],
            6: [2, 3, 4, 3, 4],
            7: [2, 3, 3, 4, 4],
            8: [3, 4, 4, 5, 5],
            9: [3, 4, 4, 5, 5],
            10: [3, 4, 4, 5, 5]
        }[len(players)]

        if len(players) <= 6:
            self.fails_required = [1, 1, 1, 1, 1]
        else:
            self.fails_required = [1, 1, 1, 2, 1]

        if roles is None:
            self.characters = {
                5: ["Morgana", "Assassin", "Merlin", "Percival", "Knight"],
                6: ["Morgana", "Assassin", "Merlin", "Percival", "Knight", "Knight"],
                7: ["Mordred", "Morgana", "Assassin", "Merlin", "Percival", "Knight", "Knight"],
                8: ["Mordred", "Morgana", "Assassin", "Merlin", "Percival", "Knight", "Knight", "Knight"],
                9: ["Mordred", "Morgana", "Assassin", "Merlin", "Percival", "Knight", "Knight", "Knight", "Knight"],
                10: ["Mordred", "Morgana", "Assassin", "Oberon", "Merlin", "Percival", "Knight", "Knight", "Knight", "Knight"]
            }[len(players)]
        else:
            self.characters = roles

        # Assign characters to players
        self.player_characters = {player: character for player, character in zip(players, random.sample(self.characters, len(players)))}

        # Shuffle players to determine turn order
        self.turn_order = random.sample(players, len(players))
        self.current_turn = 0

        # Game state variables
        self.completed_missions = []
        self.consecutive_rejects = 0
        self.proposed_team = []
        self.votes = {}
        self.mission_actions = {}
        self.mechanic_mode = "proposal"
        self.winner = ""
        self.log = []

    def get_game_params(self):
        return {
            "turn order:": self.turn_order,
            "mission_participants": self.mission_participants,
            "fails_required": self.fails_required,
            "characters": self.characters
        }

    def get_game_state(self):
        return {
            "completed_missions": self.completed_missions,
            "consecutive_rejects": self.consecutive_rejects,
            "current_turn": self.turn_order[self.current_turn],
            "current_mechanic_mode": self.mechanic_mode,
            "proposed_team": self.proposed_team
        }
    
    def get_game_results(self):
        if self.mechanic_mode != "ended":
            raise ValueError("Game must have ended to see results.")
        return {
            "winner": self.winner,
            "player_characters": self.player_characters,
            "log": self.log
        }

    def get_player_known_info(self, player_name):
        # Check if the player is in the game
        if player_name not in self.player_characters:
            raise ValueError(f"Player not found in the game")

        character = self.player_characters[player_name]
        info = {'character': character}
        
        evil_roles_noob = ["Morgana", "Mordred", "Assassin", "Minion"]

        # Providing information based on the character
        if character == "Merlin":
            info['known_players'] = [player for player, role in self.player_characters.items() if role in ["Morgana", "Assassin", "Oberon", "Minion"]]
        elif character == "Percival":
            info['known_players'] = [player for player, role in self.player_characters.items() if role in ["Merlin", "Morgana"]]
        elif character in evil_roles_noob:
            evil_roles_noob.remove(character)
            info['known_players'] = [player for player, role in self.player_characters.items() if role in evil_roles_noob]

        return info
    
    def propose_team(self, player_name, team):
        if self.mechanic_mode != "proposal":
            raise ValueError("It is not time for mission proposal.")
        
        if player_name != self.turn_order[self.current_turn]:
            raise ValueError("It is a different player's turn.")

        if len(team) != self.mission_participants[len(self.completed_missions)]:
            raise ValueError(f"Proposed team must have {self.mission_participants[len(self.completed_missions)]} members.")

        if not all(player in self.turn_order for player in team):
            raise ValueError("All players in the proposed team must be part of the game.")

        self.proposed_team = team
        self.mechanic_mode = "voting"
        self.log.append(f"{player_name} proposed {team}")
    
    def player_vote(self, player_name, vote):
        if self.mechanic_mode != "voting":
            raise ValueError("It is not time for voting on the proposed mission.")

        if player_name not in self.player_characters:
            raise ValueError("Player is not part of the game.")

        # Add or update the player's vote
        self.votes[player_name] = vote

        # Check if all players have voted
        if len(self.votes) == len(self.player_characters):
            true_votes = sum(self.votes.values())

            # Check if the vote fails
            if true_votes <= len(self.player_characters) / 2:
                self.log.append(f"rejected by {[k for (k, v) in self.votes.items() if not v]}")
                self.consecutive_rejects += 1
                self.proposed_team = []
                self.votes = {}
                if self.consecutive_rejects == 5:
                    self.winner = "evil"
                    self.mechanic_mode = "ended"
                    self.log.append("Evil team wins via rejections.")
                else:
                    self.current_turn = (self.current_turn + 1) % len(self.player_characters)
                    self.mechanic_mode = "proposal"
            else:
                self.log.append(f"approved by {[k for (k, v) in self.votes.items() if v]}")
                self.mechanic_mode = "mission"

    def player_mission_act(self, player_name, succeed_mission):
        if self.mechanic_mode != "mission":
            raise ValueError("It is not time to go on a mission.")

        if player_name not in self.proposed_team:
            raise ValueError("Player is not in the mission team.")

        if self.player_characters[player_name] in ["Merlin", "Percival", "Knight"] and not succeed_mission:
            raise ValueError("Good team can't sabotage missions.")

        # Add mission action
        self.mission_actions[player_name] = succeed_mission

        # Check if all required players have acted
        if len(self.mission_actions) == self.mission_participants[len(self.completed_missions)]:
            # Determine if the mission succeeds or fails
            mission_fail_count = sum(not action for action in self.mission_actions.values())
            mission_result = mission_fail_count < self.fails_required[len(self.completed_missions)]
            self.completed_missions.append(mission_result)
            self.log.append(f"mission {'passed' if mission_result else 'failed'} with {mission_fail_count} fails")

            # Reset states for the next mission
            self.proposed_team = []
            self.votes = {}
            self.mission_actions = {}

            if sum([not m for m in self.completed_missions]) >= 3:
                self.winner = "evil"
                self.mechanic_mode = "ended"
                self.log.append("Evil team wins via missions")
            elif sum(self.completed_missions) >= 3:
                if "Assassin" in self.player_characters.values():
                    self.mechanic_mode = "assassination" 
                else:
                    self.winner = "good"
                    self.mechanic_mode = "ended"
                    self.log.append("Good team wins")
            else:
                self.current_turn = (self.current_turn + 1) % len(self.player_characters)
                self.mechanic_mode = "proposal"
        
    def assassination(self, player_name, target):
        if self.mechanic_mode != "assassination":
            raise ValueError("It is not time for assassination.")

        if self.player_characters[player_name] != "Assassin":
            raise ValueError("This player is not the Assassin.")
        
        if target not in self.player_characters:
            raise ValueError("Target is not part of the game.")
        
        if self.player_characters[target] == "Merlin":
            self.winner = "evil"
            self.log.append("Evil team wins via assassination")
        else:
            self.winner = "good"
            self.log.append("Good team wins")
        self.mechanic_mode = "ended"
