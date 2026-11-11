#!/usr/bin/env python3
"""Install first playable ROCKSTAR MADNESS battle status.

Madness v1 uses Emerald's existing battle-only volatile confusion timer.
Common inflicting effects become Madness: 1.5x normal damage, ~55% accuracy.
The original battle-status icons and out-of-battle party ailments are retained
for compatibility; this is not yet a full replacement of every status source.
"""
import argparse
from pathlib import Path

def replace_once(data, old, new, label):
    count = data.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return data.replace(old, new, 1)

def apply(engine: Path):
    commands = engine/"src"/"battle_script_commands.c"
    messages = engine/"src"/"battle_message.c"
    util = engine/"src"/"battle_util.c"
    for f in (commands, messages, util):
        if not f.is_file():
            raise RuntimeError(f"Missing {f}")
    s = commands.read_text()
    if "/* ROCKSTAR MADNESS STATUS V1 */" not in s:
        s = replace_once(s,
            "    if (gBattleMons[gEffectBattler].ability == ABILITY_SHIELD_DUST",
            """    /* ROCKSTAR MADNESS STATUS V1 */
    /* Convert normal primary status effects to temporary battle-only Madness.
     * Preserve the AFFECTS_USER bit previously extracted above.
     * Existing confusion infrastructure manages finite turns and cure timing.
     */
    if (gBattleCommunication[MOVE_EFFECT_BYTE] >= MOVE_EFFECT_SLEEP
     && gBattleCommunication[MOVE_EFFECT_BYTE] <= MOVE_EFFECT_TOXIC)
        gBattleCommunication[MOVE_EFFECT_BYTE] = MOVE_EFFECT_CONFUSION;

    if (gBattleMons[gEffectBattler].ability == ABILITY_SHIELD_DUST""",
            "standard status conversion")
        s = replace_once(s,
            "        if (holdEffect == HOLD_EFFECT_EVASION_UP)\n            calc = (calc * (100 - param)) / 100;",
            """        if (holdEffect == HOLD_EFFECT_EVASION_UP)
            calc = (calc * (100 - param)) / 100;

        /* Madness destabilizes precision in exchange for raw power. */
        if (gBattleMons[gBattlerAttacker].status2 & STATUS2_CONFUSION)
            calc = (calc * 55) / 100;""",
            "madness accuracy")
        s = replace_once(s,
            "    gBattleMoveDamage = gBattleMoveDamage * gCritMultiplier * gBattleScripting.dmgMultiplier;\n\n    if (gStatuses3[gBattlerAttacker] & STATUS3_CHARGED_UP",
            """    gBattleMoveDamage = gBattleMoveDamage * gCritMultiplier * gBattleScripting.dmgMultiplier;
    if ((gBattleMons[gBattlerAttacker].status2 & STATUS2_CONFUSION) && gBattleMoveDamage > 0)
        gBattleMoveDamage = (gBattleMoveDamage * 3) / 2;

    if (gStatuses3[gBattlerAttacker] & STATUS3_CHARGED_UP""",
            "madness damage")
        commands.write_text(s)
    s = messages.read_text()
    replacements = [
        ('sText_PkmnIsConfused[] = _("{B_ATK_NAME_WITH_PREFIX} is\\nconfused!");',
         'sText_PkmnIsConfused[] = _("{B_ATK_NAME_WITH_PREFIX} is gripped\\nby MADNESS!");'),
        ('sText_PkmnHealedConfusion[] = _("{B_ATK_NAME_WITH_PREFIX} snapped\\nout of confusion!");',
         'sText_PkmnHealedConfusion[] = _("{B_ATK_NAME_WITH_PREFIX} escaped\\nthe MADNESS!");'),
        ('sText_PkmnWasConfused[] = _("{B_EFF_NAME_WITH_PREFIX} became\\nconfused!");',
         'sText_PkmnWasConfused[] = _("{B_EFF_NAME_WITH_PREFIX} fell\\ninto MADNESS!");'),
        ('sText_PkmnAlreadyConfused[] = _("{B_DEF_NAME_WITH_PREFIX} is\\nalready confused!");',
         'sText_PkmnAlreadyConfused[] = _("{B_DEF_NAME_WITH_PREFIX} already\\nhas MADNESS!");'),
        ('sText_ItHurtConfusion[] = _("It hurt itself in its\\nconfusion!");',
         'sText_ItHurtConfusion[] = _("MADNESS takes its toll!");'),
    ]
    for old, new in replacements:
        if new not in s:
            s=replace_once(s,old,new,"madness dialogue")
    messages.write_text(s)
    s=util.read_text()
    # Madness v1 is intended as accuracy-risk rather than randomly
    # inflicting confusion's self-hit effect. Keep normal turn countdown.
    old = "                if (gBattleMons[gBattlerAttacker].status2 & STATUS2_CONFUSION)\n                {\n                    if (Random() & 1)"
    new = "                if (gBattleMons[gBattlerAttacker].status2 & STATUS2_CONFUSION)\n                {\n                    if (TRUE) /* Madness: accuracy penalty replaces random self-hits. */"
    if new not in s:
        s=replace_once(s,old,new,"madness self-hit rule")
    util.write_text(s)
    # Original deep-violet / rose / teal battle textbox palette.
    pal=engine/"graphics"/"battle_interface"/"textbox_0.pal"
    rows=pal.read_text().splitlines()
    if rows[:3]!=["JASC-PAL","0100","16"] or len(rows)!=19:
        raise RuntimeError("Unexpected battle box palette")
    rows[5]="255 28 70"
    rows[6]="67 29 101"
    rows[7]="117 43 155"
    rows[9]="21 152 160"
    rows[15]="165 60 185"
    rows[17]="241 56 116"
    pal.write_text("\n".join(rows)+"\n")
    print("Applied Madness v1 (status moves, 1.5x damage, 55% accuracy, text, neon palette).")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("engine",type=Path)
    apply(parser.parse_args().engine)
