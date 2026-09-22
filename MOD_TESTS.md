# Mystery Roster Test Plan

Run the automated suite from the repository root:

```powershell
.\.venv\Scripts\python.exe tools\run_mod_tests.py
```

Add `--checklist` to print this manual checklist after the automated results.
Use `--iso PATH` to test a different generated ISO.

The automated suite rebuilds `build/GALE01/main.dol`, validates its DOL
sections, checks the active mod contracts in the C source, and confirms that
`build/GALE01/melee-mystery-roster.iso` contains the exact current DOL without
overlapping any files in the disc filesystem.

## General Dolphin smoke test

- Enable MMU so invalid accesses fail immediately instead of being hidden.
- Boot the mystery-roster ISO and complete one two-player match.
- Exercise pause, stock loss, respawn, ledges, grabs, shields, and results.
- Repeat each modified action at least 20 times in succession.
- Treat any invalid read, hang, or unexpected state transition as a failure.

## Ganondorf

- Use up-tilt while facing both directions.
- Confirm it damages grounded and airborne opponents.
- Confirm it interacts with shields and can whiff without becoming stuck.
- Repeat it at least 20 times and use it again after losing a stock.

## Mario

- Confirm Mario begins at normal size.
- Taunt and confirm he remains 1.5 times his normal size afterward.
- Walk, run, jump, attack, shield, grab, use a ledge, and receive damage.
- Confirm a stock loss resets him to normal size.
- Check Super and Poison Mushroom interactions when items are enabled.

## Pikachu

- Use down-B with the Thunder column aligned over Pikachu and confirm that the
  move enters its normal self-hit state, finishes its ending animation, then
  triggers the Super Mushroom growth animation.
- Miss Pikachu with Thunder and confirm he remains normal size.
- While giant, verify movement, attacks, hitboxes, shield, grabs, ledges, and
  knockback behave like the native Super Mushroom state.
- Hit Pikachu with Thunder again while giant and confirm the native size timer is
  refreshed without stacking his scale or corrupting the move state.
- Confirm Pikachu returns to normal size when the native mushroom timer expires.
- Select Pichu and Kirby with Pikachu's copied neutral-B and confirm neither gains
  this Thunder growth effect.

## Pichu

- Begin above 20 percent and use every move that normally causes recoil.
- Confirm each recoil event lowers Pichu's displayed percent instead.
- At 0 percent, confirm recoil moves remain at 0 rather than underflowing.
- Confirm ordinary non-recoil attacks do not heal Pichu.
- Hit a standing opponent with both an uncharged and fully charged Skull Bash;
  confirm its hitbox, damage, and knockback still work while Pichu heals.
- Repeat Thunder and Quick Attack many times, including after a respawn.
- Select Pikachu and confirm the same actions retain their retail behavior.

## Bowser

- Use aerial up-B and confirm the initial rise is much higher than retail.
- Hold left and right during the move and confirm the stronger steering works
  in both directions without snapping or becoming stuck.
- Confirm every normal hitbox still damages grounded and airborne opponents
  and interacts with shields.
- Test walls, ceilings, stage edges, ledge grabs, landing, and special fall.
- Repeat aerial up-B at least 20 times, including after a stock loss.
- Confirm grounded up-B retains its normal movement and behavior.

## Mr. Game & Watch

- At full shield health, shield next to attacks aimed at his head and feet;
  confirm the larger bubble and its collision coverage agree.
- Shrink the shield by holding it and confirm its visual and collision size
  decrease normally from the larger starting radius.
- Fill Oil Panic, jump, and release with neutral stick; confirm Game & Watch
  launches diagonally backward and upward while the oil attack remains active.
- Repeat aerial releases and move the stick to each cardinal and diagonal
  direction during the first few startup frames; confirm the launch follows
  that aim at a consistent speed.
- Release a full bucket while grounded and confirm it retains retail grounded
  movement instead of unexpectedly launching upward.
- Lose a stock after both shielding and using the bucket rocket; confirm the
  larger shield returns and no launch velocity or bucket state persists.

## Jigglypuff

- Use Sing in the air and confirm Puff rises slowly throughout the move.
- Hold left and right and confirm Puff can steer smoothly in both directions.
- Confirm every normal Sing wave can still put nearby opponents to sleep.
- Start Sing on the ground and confirm its movement remains unchanged.
- Start aerial Sing and land during it; confirm it transitions cleanly to the
  grounded animation without retaining upward movement.
- Test beneath platforms and ceilings, beside walls and ledges, and after a
  stock loss.
- Repeat aerial Sing at least 20 times and confirm it always returns to fall.

## Link

- Tap neutral-B repeatedly on the ground and in the air; confirm Link draws,
  fires, and recovers much faster than retail.
- Confirm uncharged and charged arrows travel dramatically faster while
  retaining their normal damage, angle, gravity, and collision behavior.
- Fire arrows into opponents, shields, walls, floors, and slopes from both
  facing directions.
- Confirm reflected arrows travel correctly and do not become stuck.
- Hold neutral-B to charge and confirm the charging loop still works.
- Repeat at least 30 rapid shots, then test again after a stock loss.
- Select Young Link and Kirby with Link's copied ability and confirm their bow
  speed and arrow speed remain unchanged.

## Young Link

- Pull a bomb and confirm its model is roughly three times normal size while
  held, thrown, airborne, and resting on the ground.
- Confirm Young Link can hold, throw, catch, pick up, and drop the giant bomb
  without unexpected collision or movement.
- Detonate it by timer, impact, and incoming damage; confirm the visible blast
  and damaging radius are both dramatically larger, and that the explosion
  deals roughly three times the original damage.
- Test the blast against grounded and airborne opponents, shields, walls,
  platforms, and stage edges.
- Confirm reflected and shield-bounced bombs still behave normally.
- Repeat at least 20 bombs, including simultaneous bombs and after a stock
  loss.
- Select regular Link and confirm his bombs retain normal size and blast range.

## Mewtwo

- Fire uncharged, partially charged, and fully charged Shadow Balls; confirm
  each grows continuously while traveling, lasts noticeably longer than the
  retail projectile, and stops growing at a finite cap.
- Confirm the damaging hitbox expands with the visible ball rather than
  remaining at its original size.
- Test hits against grounded and airborne opponents, shields, walls, floors,
  slopes, and stage edges at several different growth sizes.
- Reflect and shield-bounce growing Shadow Balls and confirm they continue to
  travel and grow correctly.
- Fire at least 30 Shadow Balls in succession and test again after a stock
  loss.
- Use Kirby's copied Shadow Ball and confirm it retains retail size behavior.

## Yoshi

- Catch an opposing fighter with grounded and aerial Egg Lay; confirm exactly
  one ReDead appears just behind and slightly above Yoshi for each successful
  catch, then falls cleanly onto the stage.
- Whiff Egg Lay and catch an item; confirm neither action spawns a ReDead.
- Spawn three ReDeads, then catch another fighter; confirm the active ReDead
  count remains capped at three.
- Defeat or remove one ReDead, catch another fighter, and confirm a replacement
  can spawn.
- Test near platforms, slopes, walls, and stage edges; confirm the ReDead falls
  onto valid ground or safely leaves the stage.
- Use Kirby's copied Egg Lay and confirm it does not spawn a ReDead.

## Kirby

- Start repeated normal VS matches with Kirby; confirm each match loads normally
  and taunting grants one copy ability selected from the full playable cast.
- Confirm the granted ability has its matching hat and that its neutral-B works;
  this verifies the preloaded file was also parsed into Kirby's runtime table.
- Confirm repeated taunts within one match consistently grant that match's
  selected ability, while starting new matches produces varied abilities that
  do not need to match an opponent.
- Confirm repeated taunts never grant Kirby's, Nana's, or a boss character's
  invalid/nonexistent copy ability.
- Interrupt Kirby's taunt with an attack; confirm he loses his previous copy
  ability but does not receive a replacement.
- Exercise projectile, chargeable, transformation, and held-item copy abilities,
  then taunt again; confirm the previous ability cleans itself up correctly.
- Lose a stock while holding a taunt-granted ability and confirm Kirby returns
  without stale projectiles, charge state, or hat graphics.
- Complete at least 30 taunts in one match and confirm memory and gameplay remain
  stable.

## Current limitation

The automated suite validates code contracts and binary packaging, but it does
not emulate a match. The Dolphin checklist remains the behavioral integration
test until deterministic input playback and result capture are added.
