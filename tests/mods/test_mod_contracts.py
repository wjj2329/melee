"""Source-level contracts for each active mystery-roster behavior."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def source(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class GanonUpTiltContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source(
            "src/melee/ft/kinds/ftCommon/ftCo_AttackHi3.c"
        )

    def test_change_is_guarded_to_ganondorf(self) -> None:
        self.assertIn("fp->kind == Ft_Kind_Ganon", self.code)

    def test_fast_windup_preserves_the_hitbox_window(self) -> None:
        self.assertIn("anim_speed = 16.0f", self.code)
        self.assertRegex(self.code, r"cur_anim_frame\s*>=\s*80\.0f")
        self.assertRegex(self.code, r"cur_anim_frame\s*<\s*84\.0f")
        self.assertIn("ftAnim_SetAnimRate(gobj, 1.0f)", self.code)
        self.assertIn("ftAnim_SetAnimRate(gobj, 16.0f)", self.code)


class MarioScaleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source(
            "src/melee/ft/kinds/ftCommon/ftCo_AppealS.c"
        )

    def test_change_is_guarded_to_mario(self) -> None:
        self.assertIn("fp->kind == Ft_Kind_Mario", self.code)

    def test_taunt_finishes_at_the_selected_scale(self) -> None:
        self.assertRegex(
            self.code,
            r"ftCo_800D2770\(gobj,\s*fp->x34_scale\.x\s*\*\s*1\.5f\)",
        )


class PichuHealingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source("src/melee/ft/ftaction.c")

    def test_change_is_guarded_to_pichu(self) -> None:
        self.assertIn("fp->kind == Ft_Kind_Pichu", self.code)

    def test_healing_clamps_at_zero_and_updates_the_hud(self) -> None:
        self.assertRegex(
            self.code,
            r"if \(amount > fp->dmg\.x1830_percent\)\s*"
            r"\{\s*amount = fp->dmg\.x1830_percent;\s*\}",
        )
        self.assertIn("fp->dmg.x1830_percent -= amount", self.code)
        self.assertIn("Player_SetHPByIndex", self.code)
        self.assertIn("pl_80040B8C", self.code)

    def test_every_other_fighter_keeps_normal_self_damage(self) -> None:
        self.assertRegex(
            self.code,
            r"else\s*\{\s*Fighter_TakeDamage_8006CC7C\(fp, amount\);\s*\}",
        )


class BowserHelicopterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source(
            "src/melee/ft/kinds/ftKoopa/ftkoopaspecialhi.c"
        )

    def test_change_is_guarded_to_ordinary_bowser(self) -> None:
        self.assertGreaterEqual(
            self.code.count("fp->kind == Ft_Kind_Koopa"), 2
        )

    def test_aerial_up_b_gets_extra_lift_and_horizontal_speed(self) -> None:
        self.assertIn("FTKP_HELICOPTER_INITIAL_LIFT 2.0f", self.code)
        self.assertIn("FTKP_HELICOPTER_MAX_SPEED 2.5f", self.code)
        self.assertRegex(
            self.code,
            r"initial_lift\s*\*=\s*FTKP_HELICOPTER_INITIAL_LIFT",
        )
        self.assertRegex(
            self.code,
            r"max_speed\s*\*=\s*FTKP_HELICOPTER_MAX_SPEED",
        )

    def test_helicopter_has_sustained_lift_and_stronger_steering(self) -> None:
        self.assertIn("FTKP_HELICOPTER_GRAVITY 0.4f", self.code)
        self.assertIn("FTKP_HELICOPTER_TERMINAL_VELOCITY 0.6f", self.code)
        self.assertIn("FTKP_HELICOPTER_DRIFT_ACCEL 3.0f", self.code)
        self.assertRegex(
            self.code,
            r"gravity\s*\*=\s*FTKP_HELICOPTER_GRAVITY",
        )
        self.assertRegex(
            self.code,
            r"terminal_velocity\s*\*=\s*"
            r"FTKP_HELICOPTER_TERMINAL_VELOCITY",
        )

    def test_grounded_up_b_keeps_its_original_physics(self) -> None:
        self.assertIn(
            "ftCommon_CalcGroundAccel_AccelToLStickX(fp, 0.0f, da->x68, "
            "da->x60);",
            self.code,
        )


if __name__ == "__main__":
    unittest.main()
