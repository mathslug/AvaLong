# Play Avalon Across Time and Space

## Create a Game

Input a username and the number of players.

<form action="/create_game" method="get">
    <input type="text" name="username">
    <input type="number" name="num_players">
    <input type="submit" value="Create Game">
</form>

## Join or Rejoin a Game

Input your username and the game ID.

<form action="/join_game" method="get">
    <input type="text" name="username">
    <input type="number" name="game_id">
    <input type="submit" value="Join Game">
</form>

There's nothing that stops you from impersonating another player except your honor.
