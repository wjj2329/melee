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

## Pichu

- Begin above 20 percent and use every move that normally causes recoil.
- Confirm each recoil event lowers Pichu's displayed percent instead.
- At 0 percent, confirm recoil moves remain at 0 rather than underflowing.
- Confirm ordinary non-recoil attacks do not heal Pichu.
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

## Current limitation

The automated suite validates code contracts and binary packaging, but it does
not emulate a match. The Dolphin checklist remains the behavioral integration
test until deterministic input playback and result capture are added.
