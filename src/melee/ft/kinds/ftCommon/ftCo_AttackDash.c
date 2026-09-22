#include "ftCo_AttackDash.h"

#include <Runtime/platform.h>

#include <melee/ft/forward.h>
#include <sysdolphin/baselib/forward.h>

#include "forward.h"
#include "ftCo_Attack100.h"
#include "ftCo_ItemThrow.h"
#include "ftCo_Wait.h"
#include "types.h"
#include <melee/ft/fighter.h>
#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_084E.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/ftswing.h>
#include <melee/ft/kinds/ftKirby/ftkirbyattackdash.h>
#include <melee/ft/types.h>
#include <melee/it/it_26B1.h>

/* 08B498 */ static void decideFighter(Fighter_GObj* gobj);
/* 08B4D4 */ static void doEnter(Fighter_GObj* gobj);

#define LUIGI_DASH_FINISHER_START 44.0f
#define LUIGI_DASH_FINISHER_END 47.0f
#define LUIGI_DASH_FINISHER_DAMAGE 25
#define LUIGI_DASH_FINISHER_ANGLE 361
#define LUIGI_DASH_FINISHER_KNOCKBACK_GROWTH 90
#define LUIGI_DASH_FINISHER_BASE_KNOCKBACK 60
#define LUIGI_DASH_FINISHER_HIT_GROUP 0x7F

static void ftCo_AttackDash_LuigiFinisher(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    HitCapsule* hit;
    int i;

    if (fp->kind != Ft_Kind_Luigi) {
        return;
    }

    if (fp->cur_anim_frame >= LUIGI_DASH_FINISHER_START &&
        fp->cur_anim_frame < LUIGI_DASH_FINISHER_END &&
        fp->x914[0].state == HitCapsule_Disabled)
    {
        for (i = 0; i < 2; i++) {
            hit = &fp->x914[i];
            hit->x4 = LUIGI_DASH_FINISHER_HIT_GROUP;
            hit->state = HitCapsule_Enabled;
            ftColl_800768A0(fp, hit);
            ftColl_8007ABD0(hit, LUIGI_DASH_FINISHER_DAMAGE, gobj);
            ftColl_8007AC9C(hit, LUIGI_DASH_FINISHER_ANGLE, gobj);
            hit->x24 = LUIGI_DASH_FINISHER_KNOCKBACK_GROWTH;
            hit->x28 = 0;
            hit->x2C = LUIGI_DASH_FINISHER_BASE_KNOCKBACK;
            hit->element = HitElement_Fire;
            hit->sfx_severity = 2;
            hit->scale *= 1.75f;
            ftColl_8007AD18(fp, hit);
        }
        fp->x2219_b3 = true;
        ftCommon_80080484(fp);
    } else if (fp->cur_anim_frame >= LUIGI_DASH_FINISHER_END) {
        fp->x914[0].state = HitCapsule_Disabled;
        fp->x914[1].state = HitCapsule_Disabled;
    }
}

bool ftCo_AttackDash_CheckInput(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    if (fp->input.pressed_buttons & HSD_PAD_A) {
        if (fp->item_gobj != NULL) {
            if (fp->input.held_buttons[0] & HSD_PAD_LR ||
                it_8026B30C(fp->item_gobj) == 0)
            {
                ftCo_800957F4(gobj, ftCo_MS_LightThrowDash);
                return true;
            }
            switch (it_8026B30C(fp->item_gobj)) {
            case 2:
                ftCo_Attack_800CCF58(gobj, 4);
                return true;
            }
        }
        decideFighter(gobj);
        return true;
    }
    return false;
}

static void decideFighter(Fighter_GObj* gobj)
{
    switch (GET_FIGHTER(gobj)->kind) {
    case Ft_Kind_Kirby:
        ftKb_SpecialN_800F1F68(gobj);
        return;
    default:
        doEnter(gobj);
        return;
    }
}

static void doEnter(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    fp->allow_interrupt = false;
    Fighter_ChangeMotionState(gobj, ftCo_MS_AttackDash, Ft_MF_None, 0, 1, 0,
                              NULL);
    ftAnim_8006EBA4(gobj);
    fp->mv.co.attackdash.x0 = 0;
}

void ftCo_AttackDash_Anim(Fighter_GObj* gobj)
{
    ftCo_AttackDash_LuigiFinisher(gobj);

    if (!ftAnim_IsFramesRemaining(gobj)) {
        ft_8008A2BC(gobj);
    }
}

void ftCo_AttackDash_SetMv0(HSD_GObj* gobj)
{
    u8 _[4] = { 0 };
    GET_FIGHTER(gobj)->mv.co.attackdash.x0 = p_ftCommonData->x68;
}

void ftCo_AttackDash_IASA(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    if (!ftCo_800D8AE0(gobj) && fp->allow_interrupt) {
        ftCo_Wait_IASA(gobj);
    }
}

void ftCo_AttackDash_Phys(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    ft_80085030(gobj, p_ftCommonData->x50 * fp->co_attrs.ground_friction,
                fp->facing_dir);
}

void ftCo_AttackDash_Coll(Fighter_GObj* gobj)
{
    ft_80084104(gobj);
}
