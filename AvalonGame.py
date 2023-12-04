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

        self.fails_required = {
            5: [1, 1, 1, 1, 1],
            6: [1, 1, 1, 1, 1],
            7: [1, 1, 1, 2, 1],
            8: [1, 1, 1, 2, 1],
            9: [1, 1, 1, 2, 1],
            10: [1, 1, 1, 2, 1]
        }[len(players)]

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
        self.assassination_time = False
        self.winner = ""

    def get_game_state(self):
        # Return the current game state information
        return {
            "current_turn": self.turn_order[self.current_turn],
            "turn order:": self.turn_order,
            "completed_missions": self.completed_missions,
            "consecutive_rejects": self.consecutive_rejects,
            "mission_participants": self.mission_participants[len(self.completed_missions)],
            "fails_required": self.fails_required[len(self.completed_missions)],
            "proposed_team": self.proposed_team
        }

    def get_player_known_info(self, player_name):
        # Check if the player is in the game
        if player_name not in self.player_characters:
            raise ValueError(f"Player {player_name} not found in the game")

        character = self.player_characters[player_name]
        info = {'character': character}

        # Providing information based on the character
        if character == "Merlin":
            info['known_players'] = [player for player, role in self.player_characters.items() if role in ["Morgana", "Assassin", "Oberon", "Minion"]]
        elif character == "Percival":
            info['known_players'] = [player for player, role in self.player_characters.items() if role in ["Merlin", "Morgana"]]
        elif character in ["Morgana", "Mordred", "Assassin", "Minion"]:
            evil_roles = ["Morgana", "Mordred", "Assassin", "Oberon", "Minion"]
            evil_roles.remove(character)
            info['known_players'] = [player for player, role in self.player_characters.items() if role in evil_roles]

        return info
    
    def propose_team(self, player_name, team):
        if self.winner:
            raise ValueError("This game is already over.")
        
        if self.assassination_time:
            raise ValueError("It is time for assassination.")
        
        if player_name != self.turn_order[self.current_turn]:
            raise ValueError("It is a different player's turn.")

        if self.proposed_team:
            raise ValueError("A team has already been proposed for this mission.")

        if len(team) != self.mission_participants[len(self.completed_missions)]:
            raise ValueError(f"Proposed team must have {self.mission_participants[len(self.completed_missions)]} members.")

        if not all(player in self.turn_order for player in team):
            raise ValueError("All players in the proposed team must be part of the game.")

        self.proposed_team = team
    
    def player_vote(self, player_name, vote):
        if self.winner:
            raise ValueError("This game is already over.")
        
        if self.assassination_time:
            raise ValueError("It is time for assassination.")
        
        if player_name not in self.player_characters:
            raise ValueError("Player is not part of the game.")

        if not self.proposed_team:
            raise ValueError("No team has been proposed yet.")

        if len(self.votes) == len(self.player_characters):
            raise ValueError("All players have already voted.")

        # Add or update the player's vote
        self.votes[player_name] = vote

        # Check if all players have voted
        if len(self.votes) == len(self.player_characters):
            true_votes = sum(self.votes.values())

            # Check if the vote fails
            if true_votes <= len(self.player_characters) / 2:
                self.consecutive_rejects += 1
                self.proposed_team = []
                self.votes = {}
                if self.consecutive_rejects == 5:
                    self.winner = "Evil Team"
                else:
                    self.current_turn = (self.current_turn + 1) % len(self.player_characters)

    def player_mission_act(self, player_name, succeed_mission):
        if self.winner:
            raise ValueError("This game is already over.")
        
        if self.assassination_time:
            raise ValueError("It is time for assassination.")

        if player_name not in self.proposed_team:
            raise ValueError("Player is not in the proposed team.")

        if len(self.votes) != len(self.player_characters):
            raise ValueError("All players have not voted yet.")

        if sum(self.votes.values()) <= len(self.player_characters) / 2:
            raise ValueError("The proposed team was not approved by the majority.")
        
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

            # Reset states for the next mission
            self.proposed_team = []
            self.votes = {}
            self.mission_actions = {}

            if sum([not m for m in self.completed_missions]) >= 3:
                self.winner = "Evil Team"
            elif sum(self.completed_missions) >= 3:
                self.assassination_time = True
            else:
                self.current_turn = (self.current_turn + 1) % len(self.player_characters)
        
    def assassination(self, player_name, target):
        if self.winner:
            raise ValueError("This game is already over.")

        if not self.assassination_time:
            raise ValueError("It is not time for assassination.")

        if self.player_characters[player_name] != "Assassin":
            raise ValueError("This player is not the Assassin.")
        
        if target not in self.player_characters:
            raise ValueError("Target is not part of the game.")
        
        if self.player_characters[target] == "Merlin":
            self.winner = "Evil Team"
        else:
            self.winner = "Good Team"
