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

    def test_healing_clamps_at_zero_and_uses_the_native_damage_path(self) -> None:
        self.assertRegex(
            self.code,
            r"if \(amount > fp->dmg\.x1830_percent\)\s*"
            r"\{\s*amount = fp->dmg\.x1830_percent;\s*\}",
        )
        self.assertIn("amount = -amount", self.code)
        self.assertRegex(
            self.code,
            r"\}\s*Fighter_TakeDamage_8006CC7C\(fp, amount\);",
        )

    def test_every_other_fighter_keeps_normal_self_damage(self) -> None:
        self.assertEqual(self.code.count("amount = -amount"), 1)
        self.assertEqual(
            self.code.count("Fighter_TakeDamage_8006CC7C(fp, amount);"), 1
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


class GameWatchBucketRocketContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.init_code = source(
            "src/melee/ft/kinds/ftGameWatch/ftgamewatch.c"
        )
        cls.bucket_code = source(
            "src/melee/ft/kinds/ftGameWatch/ftgamewatchspeciallw.c"
        )

    def test_game_watch_starts_with_a_larger_shield(self) -> None:
        on_death = self.init_code.split("void ftGw_Init_OnDeath", 1)[1].split(
            "void ftGw_Init_OnLoad", 1
        )[0]
        on_load = self.init_code.split("void ftGw_Init_OnLoad", 1)[1].split(
            "void ftGw_Init_OnDamage", 1
        )[0]
        self.assertIn("fp->co_attrs.initial_shield_size *= 1.6f", on_death)
        self.assertNotIn("initial_shield_size", on_load)

    def test_aerial_bucket_release_uses_normalized_stick_direction(self) -> None:
        self.assertIn("fp->input.lstick[0].x", self.bucket_code)
        self.assertIn("fp->input.lstick[0].y", self.bucket_code)
        self.assertIn("lbVector_Normalize(&direction)", self.bucket_code)
        self.assertIn("FTGW_BUCKET_ROCKET_SPEED 3.0f", self.bucket_code)

    def test_rocket_aim_is_sampled_after_the_down_b_input_frame(self) -> None:
        self.assertIn("FTGW_BUCKET_ROCKET_AIM_FRAME 5.0f", self.bucket_code)
        self.assertRegex(
            self.bucket_code,
            r"cur_anim_frame >= FTGW_BUCKET_ROCKET_AIM_FRAME[\s\S]*?"
            r"ftGw_SpecialAirLwShoot_ApplyRocket\(fp\);[\s\S]*?"
            r"fp->cmd_vars\[2\] = 1;",
        )

    def test_neutral_release_defaults_backward_and_upward(self) -> None:
        self.assertIn("direction.x = -fp->facing_dir", self.bucket_code)
        self.assertIn("direction.y = 0.75f", self.bucket_code)

    def test_grounded_release_does_not_get_airborne_rocket_velocity(self) -> None:
        ground_release = self.bucket_code.split(
            "void ftGw_SpecialLwShoot_ReleaseOil", 1
        )[1].split("void ftGw_SpecialAirLwShoot_ReleaseOil", 1)[0]
        self.assertNotIn("ApplyRocket", ground_release)


class PuffFlyingKaraokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source(
            "src/melee/ft/kinds/ftPurin/ftpurinspecialhi.c"
        )

    def test_aerial_sing_has_constant_lift(self) -> None:
        self.assertIn("FTPR_KARAOKE_RISE_SPEED 0.35f", self.code)
        self.assertRegex(
            self.code,
            r"self_vel\.y\s*=\s*FTPR_KARAOKE_RISE_SPEED",
        )
        self.assertIn("fp->x74_self_accel.y = 0.0f", self.code)

    def test_aerial_sing_has_horizontal_steering(self) -> None:
        self.assertIn("FTPR_KARAOKE_DRIFT_ACCEL 2.0f", self.code)
        self.assertIn("FTPR_KARAOKE_MAX_SPEED 1.5f", self.code)
        self.assertRegex(
            self.code,
            r"ftCommon_CalcSelfAccel_DriftSimple\(\s*fp,\s*0\.0f,",
        )

    def test_grounded_sing_keeps_retail_physics(self) -> None:
        self.assertRegex(
            self.code,
            r"void ftPr_SpecialHi_Phys\(HSD_GObj\* gobj\)\s*"
            r"\{\s*ft_80084F3C\(gobj\);\s*\}",
        )


class LinkMachineGunBowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fighter_code = source(
            "src/melee/ft/kinds/ftLink/ftlinkspecialn.c"
        )
        cls.arrow_code = source("src/melee/it/kinds/itlinkarrow.c")

    def test_rapid_animation_is_guarded_to_regular_link(self) -> None:
        self.assertIn("FTLK_MACHINE_GUN_ANIM_RATE 3.0f", self.fighter_code)
        self.assertIn("fp->kind == Ft_Kind_Link", self.fighter_code)
        self.assertRegex(
            self.fighter_code,
            r"return retail_rate \* FTLK_MACHINE_GUN_ANIM_RATE",
        )

    def test_startup_and_recovery_both_use_the_fast_rate(self) -> None:
        self.assertGreaterEqual(
            self.fighter_code.count("ftLk_SpecialN_GetAnimRate"), 6
        )
        self.assertRegex(
            self.fighter_code,
            r"ftLk_SpecialN_GetAnimRate\(fp, 1\.0f\)",
        )

    def test_only_regular_link_arrows_get_laser_speed(self) -> None:
        self.assertIn(
            "IT_LINK_ARROW_MACHINE_GUN_SPEED 4.0f", self.arrow_code
        )
        self.assertIn(
            "ip->kind == It_Kind_Link_Arrow", self.arrow_code
        )
        self.assertIn(
            "ip->x40_vel.x *= IT_LINK_ARROW_MACHINE_GUN_SPEED",
            self.arrow_code,
        )
        self.assertIn(
            "ip->x40_vel.y *= IT_LINK_ARROW_MACHINE_GUN_SPEED",
            self.arrow_code,
        )


class YoungLinkGiantBombContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source("src/melee/it/kinds/itlinkbomb.c")

    def test_giant_bomb_is_guarded_to_young_link(self) -> None:
        self.assertGreaterEqual(
            self.code.count("item->kind == It_Kind_CLink_Bomb"), 2
        )

    def test_normal_bomb_uses_render_only_scale(self) -> None:
        self.assertIn("IT_CLINK_GIANT_BOMB_VISUAL_SCALE 3.0f", self.code)
        self.assertRegex(
            self.code,
            r"float scale = item->scl \* IT_CLINK_GIANT_BOMB_VISUAL_SCALE",
        )
        self.assertIn("HSD_JObjSetScaleX(gobj->hsd_obj, scale)", self.code)
        self.assertIn("HSD_JObjSetScaleY(gobj->hsd_obj, scale)", self.code)
        self.assertIn("HSD_JObjSetScaleZ(gobj->hsd_obj, scale)", self.code)

    def test_gameplay_scale_changes_only_in_explosion_state(self) -> None:
        self.assertIn("item->msid != 5", self.code)
        self.assertIn("IT_CLINK_GIANT_BOMB_BLAST_SCALE 3.0f", self.code)
        self.assertRegex(
            self.code,
            r"(?s)it_8029D9A4\(gobj, 5, 0x0\);.*?"
            r"item->scl \*= IT_CLINK_GIANT_BOMB_BLAST_SCALE",
        )
        self.assertIn(
            "lb_800119DC(&item_pos, 0x78, effect_scale", self.code
        )

    def test_explosion_damage_scales_with_the_giant_blast(self) -> None:
        self.assertIn("IT_CLINK_GIANT_BOMB_DAMAGE_SCALE 3.0f", self.code)
        self.assertRegex(
            self.code,
            r"(?s)hit->state != HitCapsule_Disabled.*?it_80272460\("
            r"\s*hit,\s*hit->unk_count \* "
            r"IT_CLINK_GIANT_BOMB_DAMAGE_SCALE",
        )


class MewtwoGrowingShadowBallContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source("src/melee/it/kinds/itmewtwoshadowball.c")

    def test_growth_is_guarded_to_mewtwo_not_kirby(self) -> None:
        self.assertGreaterEqual(
            self.code.count("ip->kind == It_Kind_Mewtwo_ShadowBall"), 3
        )
        self.assertIn("It_Kind_Kirby_MewtwoShadowBall", self.code)

    def test_growth_is_time_based_and_safely_capped(self) -> None:
        self.assertIn(
            "IT_MEWTWO_SHADOWBALL_GROWTH_PER_FRAME 0.06f", self.code
        )
        self.assertIn("IT_MEWTWO_SHADOWBALL_MAX_GROWTH 4.0f", self.code)
        self.assertRegex(
            self.code,
            r"growth \+= ip->xDD4_itemVar\.mewtwoshadowball\.x4C \*",
        )
        self.assertRegex(
            self.code,
            r"if \(growth > IT_MEWTWO_SHADOWBALL_MAX_GROWTH\)",
        )

    def test_released_ball_gets_a_longer_bounded_lifetime(self) -> None:
        self.assertIn(
            "IT_MEWTWO_SHADOWBALL_LIFETIME_MULTIPLIER 1.5f", self.code
        )
        self.assertRegex(
            self.code,
            r"lifetime \*= IT_MEWTWO_SHADOWBALL_LIFETIME_MULTIPLIER",
        )
        self.assertRegex(self.code, r"it_80275158\(gobj, lifetime\)")

    def test_visual_and_hitbox_use_the_same_growth(self) -> None:
        self.assertRegex(
            self.code,
            r"mewtwoshadowball\.x10 \* growth",
        )
        self.assertRegex(
            self.code,
            r"mewtwoshadowball\.x64 \* growth",
        )


class YoshiRedeadLickContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code = source("src/melee/ft/kinds/ftYoshi/ftyoshispecialn.c")

    def test_spawn_is_guarded_to_regular_yoshi_and_bounded(self) -> None:
        self.assertIn("fp->kind != Ft_Kind_Yoshi", self.code)
        self.assertIn("FT_YOSHI_REDEAD_LIMIT 3", self.code)
        self.assertRegex(
            self.code,
            r"it_8026B3C0\(It_Kind_Leadead\) >= FT_YOSHI_REDEAD_LIMIT",
        )

    def test_native_redead_spawner_is_used_behind_yoshi(self) -> None:
        self.assertIn("FT_YOSHI_REDEAD_SPAWN_HEIGHT 6.0f", self.code)
        self.assertRegex(
            self.code,
            r"pos\.x -= fp->facing_dir \* FT_YOSHI_REDEAD_SPAWN_OFFSET",
        )
        self.assertRegex(
            self.code,
            r"pos\.y \+= FT_YOSHI_REDEAD_SPAWN_HEIGHT",
        )
        self.assertRegex(self.code, r"it_802EA9FC\(&pos,")

    def test_only_successful_fighter_catch_callbacks_spawn(self) -> None:
        self.assertEqual(self.code.count("ftYs_SpecialN_SpawnRedead(gobj);"), 2)
        self.assertRegex(
            self.code,
            r"void fn_8012CF7C\(HSD_GObj\* gobj\)[\s\S]*?"
            r"ftYs_SpecialN_SpawnRedead\(gobj\);",
        )
        self.assertRegex(
            self.code,
            r"void fn_8012D0A0\(Fighter_GObj\* gobj\)[\s\S]*?"
            r"ftYs_SpecialN_SpawnRedead\(gobj\);",
        )


class KirbyRandomTauntCopyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kirby_code = source("src/melee/ft/kinds/ftKirby/ftkirby.c")
        cls.taunt_code = source("src/melee/ft/kinds/ftCommon/ftCo_AppealS.c")
        cls.preload_code = source("src/melee/lb/lbdvd.c")

    def test_completed_taunt_assigns_a_copy_only_to_kirby(self) -> None:
        self.assertRegex(
            self.taunt_code,
            r"if \(fp->kind == Ft_Kind_Kirby\) \{\s*"
            r"ftKb_SpecialN_AssignRandomLoadedCopy\(gobj\);",
        )

    def test_random_pool_contains_only_preloaded_valid_copy_archives(self) -> None:
        self.assertGreaterEqual(
            self.kirby_code.count("ftKb_Init_803CA9D0[kind].filename != NULL"),
            2,
        )
        self.assertGreaterEqual(self.kirby_code.count("archives[kind] != NULL"), 2)
        self.assertIn("selected = HSD_Randi(available);", self.kirby_code)

    def test_kirby_preloads_the_entire_copy_roster_for_every_match(self) -> None:
        self.assertRegex(
            self.preload_code,
            r"char_id == CKind_Kirby\) \{\s*CharacterKind kind;\s*"
            r"for \(kind = 0; kind < ChKind_Max; kind\+\+\) \{\s*"
            r"Player_80031D2C\(kind, game_cache->entries\[i\]\.color\);",
        )

    def test_assignment_uses_the_normal_copy_state_path(self) -> None:
        self.assertRegex(
            self.kirby_code,
            r"ftKb_SpecialN_800F1BAC\(gobj, kind, true\);",
        )


if __name__ == "__main__":
    unittest.main()
