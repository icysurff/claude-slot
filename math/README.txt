Math (Stake Engine Math SDK) - Wild-Respin 5x4

math-sdk-game/  -> in math-sdk/games/0_0_wildrespin/ kopieren, dann: python games/0_0_wildrespin/run.py
slot5x4.py      -> Prototyp zur Kalibrierung
Die fertigen Buecher fuer den Upload liegen in claude-slot-books.zip (Ordner publish_files).

Modi (alle 96,5 % RTP, Max Win 50.000x):
  base 1x | enhancer 1,5x | buy_normal 31x | buy_super 104x | buy_jackpot 1.700x | buy_wildreels 2.600x (ein Dreh, keine Respins)
Preise stehen in game_config.py. Bei Aenderung auch das Frontend anpassen (betModeMeta.ts, config.ts) und run.py neu ausfuehren.
Stake-Risikopruefung: buy_jackpot und buy_wildreels ueberschreiten die Grenzen fuer Grossgewinn-Haeufigkeit (senkt nur die max. Einsatzhoehe).
