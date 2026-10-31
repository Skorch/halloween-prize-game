# Prize cards

The cards the spin flicks through and the winner screen shows. The 2026 set was made on 2026-10-30.

## Where they are

| Folder | Prize level | Cards |
|---|---|---|
| `assets/candy_2026/` | Mini candy | 8: disappointed kid monsters, each holding out one tiny candy |
| `assets/playdough_2026/` | Mini boss | 6: smug monsters shoving a tub of dough at the viewer |
| `assets/fullsize_2026/` | Final boss | 4: looming bosses shoving a full-size bar at the viewer |

`config.PRIZES.PRIZE_CATEGORIES` names these folders. The 2025 cards stay in `assets/candy/`, `assets/playdough/` and
`assets/fullsize/`.

Each card is a 1024x768 JPG, 4:3 like the Pi's display. The spin and winner screens scale a card to the whole square
canvas, and `render()` stretches the canvas back to 4:3, so the card shows at its own shape
(`tests/test_cards.py`).

## How a card is built

`tools/make_cards.py` builds every card listed in `assets/card_art/cards.json` from two parts:

- **The painting**, `assets/card_art/<name>.jpg`: the character in its scene, with no frame and no text.
- **The frame** for its prize level, `assets/card_frames/`: `mini_candy.png` (chipped dark wood),
  `mini_boss.png` (pewter with green slime, half its bulbs lit), `final_boss.png` (worn gold leaf over carved
  wood, dim amber bulbs). Every card of a level gets the same frame, so the level reads in a split second.

The script makes the frame's magenta centre see-through, scales the painting to fill it, lays the frame on top,
and stamps the level ("MINI CANDY", "MINI BOSS", "FINAL BOSS") on the top plaque and the character's name on the
bottom plaque, in the game's Creepster font. It needs Pillow, which the game does not:

```
uv run --with pillow python tools/make_cards.py            # every card
uv run --with pillow python tools/make_cards.py tiny_tut   # only the cards named
```

## Adding a card

1. Paint it with Runway's `nano-banana-pro` model, ratio 4:3, 2K (20 credits per image). The prompt is the style
   below, then the scene, the character, the prize line for its level, and "No text, no letters, no numbers, no
   logos anywhere."
   - **Style**: "Detailed semi-realistic digital painting in the look of high-end dark-fantasy concept art or a
     video game cover: believable textures and lighting, but clearly painted, slightly soft and stylized, not a
     photograph. Rich saturated color against deep shadow, high contrast, gentle vignette. The painting fills the
     entire image edge to edge: no border, no frame, no bars, no banner."
   - **The prize comes at the camera**: low camera, slightly wide-angle lens, the prize held toward the viewer
     with strong forced perspective, lit by its own light, the brightest thing in the image. Mini candy: a big
     open hand holding one tiny candy in a wrapper whose colour clashes with the scene, and a sad face behind it.
     Mini boss: an open, plain, unlabeled tub of chunky multicoloured dough. Final boss: a giant bar in a plain
     worn gold foil wrapper, the face grinning behind it.
   - **The scene** is where that creature would live: a carnival, its own home, a cursed sweet shop, or a
     graveyard.
   - Do not ask for the top and bottom edges to be kept plain: the model then adds bars. The script trims any
     flat bars it finds.
2. Save the painting as `assets/card_art/<name>.jpg` and add its line to `cards.json`.
3. Run the script, and look at the card.
