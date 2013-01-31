Contributing cards/cardsets
===========================

The cards are all defined in YAML format files in the `src/data` directory. Each card file (`white_cards.yml`, `black_cards.yml`) consists of a sequence of YAML strings associated with a mapping.

To add a card to an existing cardset, find the tag for the set you wish to add to, and add items to the sequence. If you follow the existing format, you'll be fine. Note that blank spaces in black cards should be replaced with `{}`, and any cards that start with a `{}` or use a `:` must be quoted.

To add a new cardset, add an entry in `cardsets.yml`, then add the white and black cards to their respective files, using the `tag` you have chosen in `cardsets.yml`.

Contributing code
=================

Standard GitHub process: fork, branch, commit, and pull request. For anything else, check up on IRC at [#berrycah on P2P-NET](irc://irc.p2p-network.net/berrycah).
