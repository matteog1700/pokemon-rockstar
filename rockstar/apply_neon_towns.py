#!/usr/bin/env python3
"""Twelve musician-named neon town overlays + collectible Neon Note side missions.

Keeps Hoenn route connections, doors, scripted critical characters and
collisions intact. This is a safe visual/story phase, not a total region remake.
"""
import argparse
import colorsys
import json
from pathlib import Path
import re

# map id, musician town name, neon scene, collectible hint, NPC to repurpose,
# quest input item, one-time reward, neon hue, palette tileset
TOWNS = [
 ("LittlerootTown", "LIL PEEP TOWN", "BLACK ROSE SKY", "A midnight radio is calling.", "LittlerootTown_EventScript_Boy", "POKE_BALL", "PP_UP", 0.92, "petalburg"),
 ("OldaleTown", "OZZY CITY", "VIOLET RIOT", "The iron bells sing at dawn.", "OldaleTown_EventScript_Girl", "GREAT_BALL", "NUGGET", 0.81, "petalburg"),
 ("PetalburgCity", "BOWIE GROVE", "ELECTRIC FOREST", "Starlight moves through trees.", "PetalburgCity_EventScript_Gentleman", "ANTIDOTE", "LEAF_STONE", 0.48, "petalburg"),
 ("RustboroCity", "COBAIN CITY", "CYBERPUNK STREETS", "An alley hides a broken chord.", "RustboroCity_EventScript_Woman", "ESCAPE_ROPE", "MAX_REVIVE", 0.79, "rustboro"),
 ("LavaridgeTown", "HENDRIX ROCK", "LAVA GUITAR FIRE", "A burning solo shakes stone.", "LavaridgeTown_EventScript_OldMan", "SUPER_POTION", "FIRE_STONE", 0.03, "lavaridge"),
 ("DewfordTown", "AMY FALLS", "CRYSTAL WATER", "Blue reflections sing softly.", "DewfordTown_EventScript_Woman", "AWAKENING", "WATER_STONE", 0.55, "dewford"),
 ("SlateportCity", "PRINCE HARBOR", "MIDNIGHT HARBOR", "Purple waves carry the beat.", "SlateportCity_EventScript_Maniac", "HARBOR_MAIL", "RARE_CANDY", 0.75, "slateport"),
 ("FallarborTown", "CHESTER HOLLOW", "PHANTOM FOG", "A lost singer echoes here.", "FallarborTown_EventScript_Girl", "REPEL", "STAR_PIECE", 0.71, "fallarbor"),
 ("MauvilleCity", "MERCURY CITY", "THUNDER STAGE", "Lightning flashes in rhythm.", "MauvilleCity_EventScript_Maniac", "THUNDER_STONE", "MAX_ELIXIR", 0.61, "mauville"),
 ("LilycoveCity", "TOO POOR CITY", "STARLIGHT NEON", "Diamonds glow after midnight.", "LilycoveCity_EventScript_Girl", "PREMIER_BALL", "SUN_STONE", 0.96, "lilycove"),
 ("VerdanturfTown", "JUICE GARDEN", "RAINBOW PARADISE", "Flowers dance to a lost tune.", "VerdanturfTown_EventScript_Boy", "POTION", "PP_MAX", 0.36, "mauville"),
 ("EverGrandeCity", "ELVIS KINGDOM", "LEGENDARY CASTLE", "The last note guards the crown.", "EverGrandeCity_EventScript_CitySign", "RARE_CANDY", "MASTER_BALL", 0.13, "ever_grande"),
]
WEATHER = {
 "LittlerootTown": "WEATHER_SUNNY_CLOUDS",
 "OldaleTown": "WEATHER_SHADE",
 "PetalburgCity": "WEATHER_RAIN",
 "RustboroCity": "WEATHER_FOG_HORIZONTAL",
 "LavaridgeTown": "WEATHER_VOLCANIC_ASH",
 "DewfordTown": "WEATHER_SUNNY_CLOUDS",
 "SlateportCity": "WEATHER_SHADE",
 "FallarborTown": "WEATHER_FOG_HORIZONTAL",
 "MauvilleCity": "WEATHER_RAIN_THUNDERSTORM",
 "LilycoveCity": "WEATHER_SUNNY_CLOUDS",
 "VerdanturfTown": "WEATHER_SUNNY",
 "EverGrandeCity": "WEATHER_SUNNY_CLOUDS",
}
def replace_label(text, label, replacement):
    pat = re.compile(r"(?m)^"+re.escape(label)+r":\n(?:[ \t]*\.string[^\n]*\n)+")
    matches=list(pat.finditer(text))
    if len(matches)!=1:
        raise RuntimeError(f"Expected one city sign label {label}; found {len(matches)}")
    return text[:matches[0].start()] + label + ":\n" + replacement + text[matches[0].end():]

def quest_script(i, name, mood, hint, request, reward):
    flag=f"FLAG_UNUSED_0x{0x264+i:03X}"
    title=f"RockstarNote{i+1:02}_EventScript"
    req=f"RockstarNote{i+1:02}_Text_Request"
    done=f"RockstarNote{i+1:02}_Text_Done"
    need=f"RockstarNote{i+1:02}_Text_Need"
    received=f"RockstarNote{i+1:02}_Text_Received"
    no_room=f"RockstarNote{i+1:02}_Text_NoRoom"
    return f"""
@ ROCKSTAR NEON NOTE {i+1:02}/12: {name}
{title}::
    lock
    faceplayer
    goto_if_set {flag}, {title}_Finished
    msgbox {req}, MSGBOX_DEFAULT
    checkitem ITEM_{request}
    goto_if_eq VAR_RESULT, FALSE, {title}_Missing
    giveitem ITEM_{reward}
    goto_if_eq VAR_RESULT, FALSE, {title}_NoBagSpace
    removeitem ITEM_{request}
    setflag {flag}
    msgbox {received}, MSGBOX_DEFAULT
    release
    end

{title}_Missing::
    msgbox {need}, MSGBOX_DEFAULT
    release
    end

{title}_NoBagSpace::
    msgbox {no_room}, MSGBOX_DEFAULT
    release
    end

{title}_Finished::
    msgbox {done}, MSGBOX_DEFAULT
    release
    end

{req}:
    .string "{name} hides a NEON NOTE!\\p"
    .string "{hint}\\p"
    .string "Find one {request.replace('_',' ')}\\l"
    .string "to unlock its song.$"

{need}:
    .string "The signal still needs a\\l"
    .string "{request.replace('_',' ')}. Come back soon!$"

{received}:
    .string "NEON NOTE {i+1}/12 unlocked!\\p"
    .string "A new chord joins the legend.$"

{done}:
    .string "NEON NOTE {i+1}/12 is playing!\\p"
    .string "{mood}.$"

{no_room}:
    .string "Your BAG is full. Make room\\l"
    .string "before collecting this NOTE.$"
"""

def tint_palette(path:Path, base_hue:float, town_idx:int):
    rows=path.read_text().splitlines()
    if rows[:3] != ["JASC-PAL","0100","16"] or len(rows)!=19:
        raise RuntimeError(f"Palette not understood: {path}")
    # Preserve transparent slot, white highlights and all 16 indexed-color slots.
    out=rows[:5]
    for ci in range(2,16):
        r,g,b=[int(x) for x in rows[3+ci].split()]
        lum=(r*30+g*59+b*11)/25500
        if lum<0.07:
            out.append(f"{r} {g} {b}")
            continue
        # A saturated complementary palette gives architecture purple/pink/cyan
        # or red/gold highlights without changing GBA tile or collision indexing.
        h=(base_hue+(ci%4)*0.078+town_idx*0.004)%1
        sat=0.74 if ci%3 else 0.90
        val=max(0.18,min(1.0,0.18 + lum*0.91))
        col=colorsys.hsv_to_rgb(h,sat,val)
        out.append(" ".join(str(min(255,int(round(v*255/8)*8))) for v in col))
    if len(out)!=19:
        raise RuntimeError("Palette length changed")
    path.write_text("\n".join(out)+"\n")

def apply(engine:Path):
    maps=engine/"data"/"maps"
    regions=engine/"src"/"data"/"region_map"/"region_map_sections.json"
    items=engine/"include"/"constants"/"items.h"
    if not maps.is_dir() or not regions.is_file() or not items.is_file():
        raise RuntimeError("Source checkout missing maps or region map")
    item_header=items.read_text()
    for t in TOWNS:
        for item in (t[5],t[6]):
            if "ITEM_"+item not in item_header:
                raise RuntimeError("Unknown quest item: "+item)
    sections=json.loads(regions.read_text())
    by_id={m["id"]:m for m in sections["map_sections"]}
    tile_hues={}
    notes=[]
    for i,(mid,name,mood,hint,old_script,required,reward,hue,tileset) in enumerate(TOWNS):
        mpath=maps/mid/"map.json"
        obj=json.loads(mpath.read_text())
        if obj["name"]!=mid:
            raise RuntimeError("Map identity mismatch: "+mid)
        obj["weather"]=WEATHER[mid]
        # Never move an existing warp, linked route, cutscene NPC or trigger.
        events=obj["bg_events"] if mid=="EverGrandeCity" else obj["object_events"]
        changed=0
        for e in events:
            if e.get("script")==old_script:
                e["script"]=f"RockstarNote{i+1:02}_EventScript"
                changed+=1
        if changed!=1:
            raise RuntimeError(f"Could not identify exactly one safe quest NPC/sign in {mid}: {changed}")
        mpath.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
        scpath=maps/mid/"scripts.inc"
        s=scpath.read_text()
        if f"RockstarNote{i+1:02}_EventScript" in s:
            raise RuntimeError("Quest already applied: "+mid)
        suffix="TownSign" if mid.endswith("Town") else "CitySign"
        # Old names in labels remain; only displayed text changes.
        textlabel=f"{mid}_Text_{suffix}"
        sign=f'    .string "{name}\\p"\n    .string "{mood} - NEON NOTE {i+1}/12.$"\n'
        s=replace_label(s,textlabel,sign)
        s+=quest_script(i,name,mood,hint,required,reward)
        scpath.write_text(s)
        sect=obj["region_map_section"]
        if sect not in by_id:
            raise RuntimeError("Region map missing "+sect)
        by_id[sect]["name"]=name
        notes.append((mid,name,mood))
        # One Emerald secondary tileset may be shared by several towns.
        # Recolor once per actual tileset, while weather + scripts distinguish maps.
        if tileset not in tile_hues:
            tile_hues[tileset]=(hue,i)
    regions.write_text(json.dumps(sections,ensure_ascii=False,indent=2)+"\n")
    for tileset,(hue,i) in tile_hues.items():
        folder=engine/"data"/"tilesets"/"secondary"/tileset/"palettes"
        if not folder.is_dir():
            raise RuntimeError("Missing secondary tileset palette: "+tileset)
        n=0
        for palette in sorted(folder.glob("*.pal")):
            tint_palette(palette,hue,i)
            n+=1
        if not n:
            raise RuntimeError("No palette files for "+tileset)
        print(f"{tileset}: {n} neon palettes tinted for musician landmark")
    # Fix the opening to match the actual renamed home town.
    opener=maps/"LittlerootTown"/"scripts.inc"
    st=opener.read_text()
    st=st.replace("MOM: Welcome to ROCKSTAR TOWN!", "MOM: Welcome to LIL PEEP TOWN!")
    st=st.replace("ROCKSTAR TOWN", "LIL PEEP TOWN")
    opener.write_text(st)
    print("Twelve musician region names, town signs, 12 one-time item-fetch Neon Note missions, and neon architecture palettes: "+", ".join(n for _,n,_ in notes))

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("engine",type=Path)
    apply(parser.parse_args().engine)
