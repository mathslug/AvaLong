# Voting Time

**Game ID:** {{ game_id }}

**{{ proposed_team }}** is the proposed mission.

{{ vote_string }}. Cast or re-cast your vote below.

<form action="/avalom/voting_result" method="get">
    <input type="hidden" name="game_id" value="{{ game_id }}">
    <input type="hidden" name="player_name" value="{{ player_name }}">

    <label>
        <input type="radio" name="vote" value="yes">
        Yes
    </label>
    <label>
        <input type="radio" name="vote" value="no">
        No
    </label>
    <br>
    <input type="submit" value="Submit Vote">
</form>

The game will proceed once everyone has voted.

## Your Info

Your name is {{ player_name }}. Here's your game info:

{{ known_info }}

## Game State

{{ game_state }}

## Game Parameters

{{ game_params }}

## Game Log

{{ game_log }}
