# Holo's Hanafuda Cards

**hololive Holo's Hanafuda** redraws the whole deck, so the art doesn't always look like traditional hanafuda. This page maps its cards to the engine's card IDs in [RULES.md section 1](RULES.md#1-equipment).

The game's card list shows each month's cards in the same order as the engine's IDs, so **a card's position decides its ID and type, not its picture.** Don't identify a card by what's drawn on it:

- Many plains show a creature, such as the bird on card 30 or the fox on card 27.
- Card 41 is the traditional swallow card and counts as an animal, but it shows a character and no swallow.
- Card 12 is the traditional cuckoo, and its bird looks more like a swallow.

The screenshots behind this page are in the local [`screenshots/`](../screenshots/README.md) folder, and `card_list.png` shows the whole deck. The checklist's [evidence log](HOLOS_HANAFUDA_CHECKLIST.md#evidence-log) lists them all.

## Card list

Each entry gives the card ID, its type and how to recognise it. A **✓** means a score or collected screen showed the card in that type's group. The other types come from the card's position in the list, and from the engine's deck.

| Month | First card | Second card | Third card | Fourth card |
|---|---|---|---|---|
| 1 Jan, 松 Pine | 0 bright: two characters, red sun | 1 poetry ribbon: red text ribbon | 2 plain: small moon, pink rabbit | 3 plain: white cat, dark figure |
| 2 Feb, 梅 Plum | 4 animal ✓: character with green binoculars | 5 poetry ribbon ✓: red text ribbon | 6 plain ✓: orange creature | 7 plain ✓: yellow cat, white ghost |
| 3 Mar, 桜 Cherry | 8 bright ✓: curtain, two characters | 9 poetry ribbon ✓: red text ribbon | 10 plain ✓: white cat, yellow figure | 11 plain ✓: black cat |
| 4 Apr, 藤 Wisteria | 12 animal ✓: orange bird, character | 13 ribbon ✓: red ribbon, character in a hat | 14 plain ✓: small yellow creature | 15 plain: black cat |
| 5 May, 杜若 Iris | 16 animal: character on yellow boxes | 17 ribbon ✓: red ribbon, white-haired character | 18 plain ✓: small blue creature at the base | 19 plain: yellow bird, bowl at the base |
| 6 Jun, 牡丹 Peony | 20 animal ✓: two characters with game controllers | 21 blue ribbon ✓: purple ribbon | 22 plain ✓: red curled shape | 23 plain ✓: lipstick and music notes |
| 7 Jul, 萩 Bush clover | 24 animal: orange boar shape, two characters | 25 ribbon ✓: red ribbon, pink-haired character | 26 plain: small orange creature | 27 plain ✓: fox |
| 8 Aug, 芒 Susuki | 28 bright: moon, character | 29 animal ✓: three orange birds, masked figure | 30 plain: white bird | 31 plain: small round creature at the base |
| 9 Sep, 菊 Chrysanthemum | 32 animal: sake cup, characters | 33 blue ribbon ✓: purple ribbon | 34 plain ✓: fan | 35 plain ✓: hat, black cat |
| 10 Oct, 紅葉 Maple | 36 animal ✓: characters, antlers | 37 blue ribbon: purple ribbon | 38 plain: hat, carrot | 39 plain: yellow figure, blue orb |
| 11 Nov, 柳 Willow | 40 bright: several characters, red sun | 41 animal ✓: blonde character in a white skirt | 42 ribbon ✓: red ribbon, dark-haired character | 43 plain ✓: red and black card |
| 12 Dec, 桐 Paulownia | 44 bright: phoenix colours, character | 45 plain ✓: text 秘密結社 | 46 plain ✓: text すたっふ on yellow | 47 plain ✓: hololive logo |

## Yaku names on score screens

| Game | Engine |
|---|---|
| タネ | Tane |
| タン | Tanzaku |
| カス | Kasu |

The other yaku names haven't appeared on a saved score screen yet.

## Tests

`tests/test_score_screens.py` holds the three rounds, as card IDs read from these screens. Round 3 has the full pile. Rounds 1 and 2 only show the cards that scored.
