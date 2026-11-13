#!/usr/bin/env python3
"""GBA-native Pokemon Rockstar EV/IV editor on Pokémon Summary > Skills.

Press A on a Pokémon's Skills page, then select a stat with Up/Down.
Left/Right allocate +/-1 EV; L/R allocate +/-10; A or B closes.
IVs are shown read-only. Existing saves are used directly; no new save format.
Only editing your own party is enabled, not rentals, trades or boxed Pokémon.
"""
import argparse
from pathlib import Path

PROTO = """/* ROCKSTAR EV IV EDITOR PROTOTYPES */
static void RockstarEvOpen(void);
static void RockstarEvInput(void);
"""
FUNCTIONS = r'''
/* ROCKSTAR EV IV EDITOR V1 */
#define ROCKSTAR_EV_TOTAL 510
#define ROCKSTAR_EV_PER_STAT 252
static u8 sRockstarEvWindow = WINDOW_NONE;
static bool8 sRockstarEvIsEditing = FALSE;
static u8 sRockstarEvRow = 0;
static const u16 sRockstarEvFields[6] = {
    MON_DATA_HP_EV, MON_DATA_ATK_EV, MON_DATA_DEF_EV,
    MON_DATA_SPATK_EV, MON_DATA_SPDEF_EV, MON_DATA_SPEED_EV,
};
static const u16 sRockstarIvFields[6] = {
    MON_DATA_HP_IV, MON_DATA_ATK_IV, MON_DATA_DEF_IV,
    MON_DATA_SPATK_IV, MON_DATA_SPDEF_IV, MON_DATA_SPEED_IV,
};
static const u8 sRockstarEvHp[] = _("HP");
static const u8 sRockstarEvAtk[] = _("ATK");
static const u8 sRockstarEvDef[] = _("DEF");
static const u8 sRockstarEvSpAtk[] = _("S.ATK");
static const u8 sRockstarEvSpDef[] = _("S.DEF");
static const u8 sRockstarEvSpeed[] = _("SPEED");
static const u8 *const sRockstarEvNames[6] = {
    sRockstarEvHp, sRockstarEvAtk, sRockstarEvDef,
    sRockstarEvSpAtk, sRockstarEvSpDef, sRockstarEvSpeed
};
static const struct WindowTemplate sRockstarEvTemplate = {
    .bg = 0,
    .tilemapLeft = 10,
    .tilemapTop = 4,
    .width = 20,
    .height = 13,
    .paletteNum = 6,
    .baseBlock = 740,
};
static const u8 sRockstarEvTitle[] = _("EV / IV - ROCKSTAR");
static const u8 sRockstarEvHead[] = _("STAT       EV    IV");
static const u8 sRockstarEvTotal[] = _("USED:");
static const u8 sRockstarEvOutOf[] = _("/510");
static const u8 sRockstarEvHelp[] = _("LEFT/RIGHT  L/R X10");
static const u8 sRockstarEvExit[] = _("A/B DONE");

static struct Pokemon *RockstarEvMon(void)
{
    return &sMonSummaryScreen->monList.mons[sMonSummaryScreen->curMonIndex];
}

static void RockstarEvRender(void)
{
    u8 i;
    u16 used = 0;
    struct Pokemon *mon = RockstarEvMon();
    if (sRockstarEvWindow == WINDOW_NONE)
        return;
    FillWindowPixelBuffer(sRockstarEvWindow, PIXEL_FILL(0));
    PrintTextOnWindow(sRockstarEvWindow, sRockstarEvTitle, 2, 0, 0, 0);
    PrintTextOnWindow(sRockstarEvWindow, sRockstarEvHead, 2, 12, 0, 0);
    for (i = 0; i < 6; i++)
    {
        u16 ev = GetMonData(mon, sRockstarEvFields[i]);
        u16 iv = GetMonData(mon, sRockstarIvFields[i]);
        used += ev;
        PrintTextOnWindow(sRockstarEvWindow, sRockstarEvNames[i], 12, 25 + i * 10, 0, 0);
        PrintTextOnWindow(sRockstarEvWindow, (i == sRockstarEvRow) ? (const u8 *)_(">") : (const u8 *)_(" "), 0, 25 + i * 10, 0, 0);
        ConvertIntToDecimalStringN(gStringVar1, ev, STR_CONV_MODE_RIGHT_ALIGN, 3);
        PrintTextOnWindow(sRockstarEvWindow, gStringVar1, 92, 25 + i * 10, 0, 0);
        ConvertIntToDecimalStringN(gStringVar1, iv, STR_CONV_MODE_RIGHT_ALIGN, 2);
        PrintTextOnWindow(sRockstarEvWindow, gStringVar1, 127, 25 + i * 10, 0, 0);
    }
    PrintTextOnWindow(sRockstarEvWindow, sRockstarEvTotal, 2, 85, 0, 0);
    ConvertIntToDecimalStringN(gStringVar1, used, STR_CONV_MODE_RIGHT_ALIGN, 3);
    PrintTextOnWindow(sRockstarEvWindow, gStringVar1, 45, 85, 0, 0);
    PrintTextOnWindow(sRockstarEvWindow, sRockstarEvOutOf, 67, 85, 0, 0);
    PrintTextOnWindow(sRockstarEvWindow, sRockstarEvExit, 105, 85, 0, 0);
    CopyWindowToVram(sRockstarEvWindow, COPYWIN_FULL);
    ScheduleBgCopyTilemapToVram(0);
}

static void RockstarEvUpdateStats(struct Pokemon *mon)
{
    struct PokeSummary *sum = &sMonSummaryScreen->summary;
    CalculateMonStats(mon);
    CopyMonToSummaryStruct(&sMonSummaryScreen->currentMon);
    sum->currentHP = GetMonData(mon, MON_DATA_HP);
    sum->maxHP = GetMonData(mon, MON_DATA_MAX_HP);
    sum->atk = GetMonData(mon, MON_DATA_ATK);
    sum->def = GetMonData(mon, MON_DATA_DEF);
    sum->spatk = GetMonData(mon, MON_DATA_SPATK);
    sum->spdef = GetMonData(mon, MON_DATA_SPDEF);
    sum->speed = GetMonData(mon, MON_DATA_SPEED);
}

static void RockstarEvAdjust(s16 delta)
{
    s16 i;
    u16 total = 0;
    u16 before;
    u8 after;
    struct Pokemon *mon = RockstarEvMon();
    for (i = 0; i < 6; i++)
        total += GetMonData(mon, sRockstarEvFields[i]);
    before = GetMonData(mon, sRockstarEvFields[sRockstarEvRow]);
    if (delta > 0)
    {
        if (total >= ROCKSTAR_EV_TOTAL || before >= ROCKSTAR_EV_PER_STAT)
            return;
        if (delta > ROCKSTAR_EV_PER_STAT - before)
            delta = ROCKSTAR_EV_PER_STAT - before;
        if (delta > ROCKSTAR_EV_TOTAL - total)
            delta = ROCKSTAR_EV_TOTAL - total;
    }
    else
    {
        if (before == 0)
            return;
        if (-delta > before)
            delta = -before;
    }
    after = before + delta;
    SetMonData(mon, sRockstarEvFields[sRockstarEvRow], &after);
    RockstarEvUpdateStats(mon);
    PlaySE(SE_SELECT);
    RockstarEvRender();
}

static void RockstarEvOpen(void)
{
    if (sRockstarEvIsEditing)
        return;
    if (sMonSummaryScreen->mode != SUMMARY_MODE_NORMAL
     || sMonSummaryScreen->monList.mons != gPlayerParty
     || sMonSummaryScreen->summary.isEgg
     || gMain.inBattle)
        return;
    sRockstarEvRow = 0;
    sRockstarEvWindow = AddWindow(&sRockstarEvTemplate);
    if (sRockstarEvWindow == WINDOW_NONE)
        return;
    sRockstarEvIsEditing = TRUE;
    PutWindowTilemap(sRockstarEvWindow);
    PlaySE(SE_SELECT);
    RockstarEvRender();
}

static void RockstarEvClose(void)
{
    if (sRockstarEvWindow != WINDOW_NONE)
    {
        ClearWindowTilemap(sRockstarEvWindow);
        RemoveWindow(sRockstarEvWindow);
        sRockstarEvWindow = WINDOW_NONE;
    }
    sRockstarEvIsEditing = FALSE;
    PrintSkillsPageText();
    ScheduleBgCopyTilemapToVram(0);
}

static void RockstarEvInput(void)
{
    if (JOY_NEW(A_BUTTON) || JOY_NEW(B_BUTTON))
    {
        PlaySE(SE_SELECT);
        RockstarEvClose();
    }
    else if (JOY_NEW(DPAD_UP))
    {
        sRockstarEvRow = (sRockstarEvRow + 5) % 6;
        PlaySE(SE_SELECT);
        RockstarEvRender();
    }
    else if (JOY_NEW(DPAD_DOWN))
    {
        sRockstarEvRow = (sRockstarEvRow + 1) % 6;
        PlaySE(SE_SELECT);
        RockstarEvRender();
    }
    else if (JOY_NEW(DPAD_LEFT))
        RockstarEvAdjust(-1);
    else if (JOY_NEW(DPAD_RIGHT))
        RockstarEvAdjust(1);
    else if (JOY_NEW(L_BUTTON))
        RockstarEvAdjust(-10);
    else if (JOY_NEW(R_BUTTON))
        RockstarEvAdjust(10);
}
/* END ROCKSTAR EV IV EDITOR V1 */
'''
def replace_once(s, before, after, label):
    if s.count(before) != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {s.count(before)}")
    return s.replace(before,after,1)

def apply(engine):
    path=engine/"src"/"pokemon_summary_screen.c"
    if not path.is_file():
        raise RuntimeError("Missing Pokémon summary screen source")
    s=path.read_text()
    if "ROCKSTAR EV IV EDITOR V1" in s:
        print("Rockstar EV editor already applied")
        return
    s=replace_once(s,
        "static void Task_HandleInput(u8);\n",
        "static void Task_HandleInput(u8);\n"+PROTO,
        "input prototype")
    s=replace_once(s,
        "    sMonSummaryScreen = AllocZeroed(sizeof(*sMonSummaryScreen));\n",
        "    sMonSummaryScreen = AllocZeroed(sizeof(*sMonSummaryScreen));\n    sRockstarEvIsEditing = FALSE;\n    sRockstarEvWindow = WINDOW_NONE;\n",
        "editor initialize")
    s=replace_once(s,
        "static void Task_HandleInput(u8 taskId)\n{\n    if (MenuHelpers_ShouldWaitForLinkRecv() != TRUE && !gPaletteFade.active)\n    {\n",
        """static void Task_HandleInput(u8 taskId)
{
    if (MenuHelpers_ShouldWaitForLinkRecv() != TRUE && !gPaletteFade.active)
    {
        if (sRockstarEvIsEditing)
        {
            RockstarEvInput();
            return;
        }
""",
        "editor input handler")
    s=replace_once(s,
        "            if (sMonSummaryScreen->currPageIndex != PSS_PAGE_SKILLS)\n            {\n",
        """            if (sMonSummaryScreen->currPageIndex == PSS_PAGE_SKILLS)
            {
                RockstarEvOpen();
            }
            else
            {
""",
        "skills A editor")
    s=replace_once(s,
        "static void PrintMonInfo(void)\n{",
        FUNCTIONS+"\nstatic void PrintMonInfo(void)\n{",
        "editor implementation after text printer")
    # Show A:EV/IV within original top-right summary label on Skills page.
    s=replace_once(s,
        "    PrintExpPointsNextLevel();\n}\n\nstatic void Task_PrintSkillsPage",
        """    PrintExpPointsNextLevel();
    FillWindowPixelBuffer(PSS_LABEL_WINDOW_PROMPT_CANCEL, PIXEL_FILL(0));
    PrintTextOnWindow(PSS_LABEL_WINDOW_PROMPT_CANCEL, (const u8 *)_("A:EV/IV"), 1, 1, 0, 0);
    CopyWindowToVram(PSS_LABEL_WINDOW_PROMPT_CANCEL, COPYWIN_FULL);
}\n\nstatic void Task_PrintSkillsPage""",
        "editor discoverability label")
    s=replace_once(s,
        "    case PSS_PAGE_SKILLS:\n        PutWindowTilemap(PSS_LABEL_WINDOW_POKEMON_SKILLS_TITLE);",
        "    case PSS_PAGE_SKILLS:\n        PutWindowTilemap(PSS_LABEL_WINDOW_PROMPT_CANCEL);\n        PutWindowTilemap(PSS_LABEL_WINDOW_POKEMON_SKILLS_TITLE);",
        "editor visible prompt")
    s=replace_once(s,
        "    case PSS_PAGE_SKILLS:\n        ClearWindowTilemap(PSS_LABEL_WINDOW_POKEMON_SKILLS_STATS_LEFT);",
        "    case PSS_PAGE_SKILLS:\n        ClearWindowTilemap(PSS_LABEL_WINDOW_PROMPT_CANCEL);\n        ClearWindowTilemap(PSS_LABEL_WINDOW_POKEMON_SKILLS_STATS_LEFT);",
        "editor prompt cleanup")
    # Variables must be declared before ShowPokemonSummaryScreen / Task_HandleInput.
    # Function implementation is later, so put state definitions up near sMonSummaryScreen.
    state = r'''/* Rockstar EV editor controls */
static u8 sRockstarEvWindow;
static bool8 sRockstarEvIsEditing;
static u8 sRockstarEvRow;
'''
    s=replace_once(s,
        "EWRAM_DATA u8 gLastViewedMonIndex = 0;",
        state+"EWRAM_DATA u8 gLastViewedMonIndex = 0;",
        "editor state definitions")
    # Remove duplicate state definitions in helper body.
    s=replace_once(s,
        "static u8 sRockstarEvWindow = WINDOW_NONE;\nstatic bool8 sRockstarEvIsEditing = FALSE;\nstatic u8 sRockstarEvRow = 0;\n",
        "",
        "duplicate state")
    path.write_text(s)
    print("Rockstar EV/IV editor: Summary > Skills > A, 510 pool, 252/stat, +/-1/10, IV readout, persistent party stat recalculation.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("engine",type=Path)
    apply(parser.parse_args().engine)
