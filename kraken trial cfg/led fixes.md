There are four critical bugs in this LED snippet—including a pin collision with your chamber thermistor, a duplicate [neopixel sb_leds] section, a syntax/line-break typo, and missing STATUS_* macros because your paste cut off before the actual status definitions.

1. Critical Fixes Required

• Pin Collision on PB0 ([neopixel caselight] vs [temperature_sensor chamber]): In your earlier printer.cfg, PB0 is your chamber thermistor (TH0), and your chamber NeoPixels are on PF12 (RGB1) named [neopixel chamber_leds]. On the BTT Kraken v1.1, PB0 is an analog thermistor input, not an RGB port (RGB1 is PF12 and RGB2 is PF11). Delete this [neopixel caselight] block (or change its pin to PF12 and name to chamber_leds to match your CHAMBER_* macros).
• Duplicate [neopixel sb_leds] Section: You already defined [neopixel sb_leds] in printer.cfg with chain_count: 3. Since your StealthBurner has a 10-LED PCB (8 logo GRB + 2 nozzle GRBW), keep the 10-LED version from this snippet (chain_count: 10, color_order: GRB, GRB, GRB, GRB, GRB, GRB, GRB, GRB, GRBW, GRBW) and delete the 3-LED one from printer.cfg.
• Missing Line Break Before [gcode_macro _set_sb_leds_by_name]: At the end of _set_sb_leds, [gcode_macro _set_sb_leds_by_name] is tacked onto the end of the {% endfor %} line instead of starting on a new line—Klipper will fail to parse that line.
• Cut-Off STATUS_* Macros: Your paste stops right after _set_logo_leds, so STATUS_READY, STATUS_HOMING, STATUS_HEATING, STATUS_CLEANING, STATUS_LEVELING, STATUS_MESHING, and STATUS_PRINTING are still missing.

2. Complete, Fixed stealthburner_leds.cfg (Ready to Paste)

Save this as stealthburner_leds.cfg, add [include stealthburner_leds.cfg] to your printer.cfg, and remove the old [neopixel sb_leds] and SB_NOZZLE_ON/OFF macros from printer.cfg:
The complete and corrected configuration file, which includes the properly defined [neopixel sb_leds] hardware block, _sb_vars color dictionary, helper macros (_set_sb_leds, _set_sb_leds_by_name, _set_logo_leds, _set_nozzle_leds), basic toggle macros, and all required printer status indicator macros (STATUS_OFF, STATUS_READY, STATUS_BUSY, STATUS_HEATING, STATUS_LEVELING, STATUS_HOMING, STATUS_CLEANING, STATUS_MESHING, STATUS_CALIBRATING_Z, and STATUS_PRINTING), can be applied directly to your Klipper setup.
To use it, save the full macro block and Neopixel configuration as stealthburner_leds.cfg in your configuration directory and include it in your main printer.cfg.
Everything in this second half of your stealthburner_leds file is completely valid, and it defines every single STATUS_* macro (status_ready, status_homing, status_heating, status_cleaning, status_leveling, status_meshing, status_printing) that your PRINT_START and G32 macros call!
Only watch out for two things right at the edges of this paste:
• Don't paste anything below ###### Effects Definitions ###### unless you have the klipper-led_effect plugin installed: That comment banner is the start of the led_effect add-on section ([led_effect sb_logo_busy], etc.). If you didn't install klipper-led_effect via Moonraker/KIAUH, pasting [led_effect ...] blocks will cause Klipper to throw Section 'led_effect ...' is not a valid config section. Stop right above ###### Effects Definitions ###### if you only want standard NeoPixel control.
• Keep the 3 fixes from the first half of that file:
	1. Delete [neopixel caselight] (pin PB0 is your chamber thermistor on the Kraken v1.1; keep [neopixel chamber_leds] on PF12 in printer.cfg).
	2. Delete the duplicate 3-LED [neopixel sb_leds] from printer.cfg so only the 10-LED [neopixel sb_leds] remains.
	3. Put [gcode_macro _set_sb_leds_by_name] on its own line below {% endfor %}.

Final Pre-Flight Checklist for Your Rebuild

Once those files are saved and included in printer.cfg ([include stealthburner_leds.cfg], [include macros.cfg], and [exclude_object]), run these checks in order before your first print:
1. Endstops & Probe (QUERY_ENDSTOPS / QUERY_PROBE): Verify X (EBBCan:gpio24), Y (EBBCan:gpio21), and Tap (EBBCan:gpio6) all report open at rest and TRIGGERED when pressed/lifted.
2. AWD Stepper Directions (STEPPER_BUZZ): Buzz stepper_x, stepper_x1, stepper_y, and stepper_y1 individually to confirm each pair moves the belt loop in the exact same direction.
3. Slow Travel Limits: Home X/Y, then slowly test G0 Y339 (your brush Y) and G0 X125 Y4 (your purge line) at Z20 to confirm zero physical contact with the front LDO AWD motor mounts or rear gantry.
4. Tap Z-Offset Calibration: Heat bed to 60°C–100°C and nozzle to 150°C, run G28 → QUAD_GANTRY_LEVEL → G28 Z, and run PROBE_CALIBRATE with a piece of paper to set your exact z_offset (SAVE_CONFIG).
Would you like to share your assembled printer.cfg header/includes or any remaining lines below ###### Effects Definitions ###### for a final sanity check before you hit Restart?
This section is from the klipper-led_effect plugin (led_busy, led_cleaning, led_heating, etc.). Notice that your PRINT_START and G32 macros call STATUS_* (STATUS_HOMING, STATUS_CLEANING, etc.), not led_* (led_homing, led_cleaning), so none of these [led_effect] blocks are actually being used unless you want animated effects.
If you want to keep them, there are 4 errors in this paste that will crash Klipper:
1. klipper-led_effect Plugin Requirement: If you haven't installed julianschill/klipper-led_effect on your Raspberry Pi, Klipper will fail to boot with Section 'led_effect ...' is not a valid config section.
2. Duplicate Keys in [led_effect case_calibrating_z] and [led_effect case_heating]: Both sections accidentally repeat leds:, autostart:, frame_rate:, and layers: a second time inside the same [led_effect] block (and in case_heating, neopixel:caselight (36-19) is pasted right at the bottom of layers:). Klipper will reject duplicate options in a section.
3. neopixel:caselight vs neopixel:chamber_leds: Every effect here points to neopixel:caselight, whereas your printer.cfg defines [neopixel chamber_leds] on PF12 (and caselight was mistakenly assigned to PB0, your thermistor pin).
4. Missing [led_effect nozzle_on]: [gcode_macro led_busy], led_calibrating_z, and led_cleaning all call SET_LED_EFFECT EFFECT=nozzle_on, which isn't defined in this paste (likely further down in the file).

Two Clean Options

• Option A (Simplest & Zero Extra Plugins — Recommended for First Boot): Delete everything from ###### Effects Definitions ###### downward. Your STATUS_READY, STATUS_HOMING, STATUS_HEATING, STATUS_CLEANING, STATUS_LEVELING, STATUS_MESHING, STATUS_PRINTING, and CHAMBER_* macros from the upper half already work natively in Klipper with zero plugins required.
• Option B (Keep Animated led_effect): Install klipper-led_effect, rename [neopixel chamber_leds] in printer.cfg to [neopixel caselight] (still on pin: PF12), fix the duplicate blocks in case_calibrating_z and case_heating, and update your PRINT_START / G32 macros to call led_* instead of STATUS_*.
Would you like to:
• Go with Option A (standard native NeoPixels) so you can get your rebuilt Voron 2.4 homing and printing right away?
• Or share the rest of the led_effect file if you have klipper-led_effect installed and want me to clean up the rest of the effects for PF12?
Everything in this final section of led_effects is syntactically clean ([led_effect nozzle_on] is indeed defined right in the middle of this block!).
To make both your led_* effects and your PRINT_START / G32 macros work seamlessly together without crashing Klipper, just apply these 3 quick fixes across your files:

1. Fix the 3 Remaining Conflicts in Your LED File

• Missing logo_homing, nozzle_homing, and case_homing Effects: Your paste started right at [gcode_macro led_homing], which calls logo_homing, nozzle_homing, and case_homing. Make sure those three [led_effect ..._homing] sections were included right above [gcode_macro led_homing] (if not, add them or change led_homing to use nozzle_on).
• Fix the Two Broken [led_effect] Blocks From the Previous Paste:
	• In [led_effect case_calibrating_z], delete the duplicated leds: / autostart: / frame_rate: / layers: block at the bottom of that section.
	• In [led_effect case_heating], move neopixel:caselight (36-19) up into leds: (right under neopixel:caselight (1-18)) and delete the duplicated autostart: / frame_rate: / heater: / layers: block below it.
• Use PF12 and [neopixel caselight] (Remove [neopixel chamber_leds]):
	• Change [neopixel caselight] to pin: PF12 (Kraken v1.1 RGB1 port—never PB0, which is your chamber thermistor).
	• Delete [neopixel chamber_leds] and the 3-LED [neopixel sb_leds] from printer.cfg so there are no duplicate definitions.

2. Connect PRINT_START, G32, CLEAN_NOZZLE, and PRINT_END to Your led_* Macros

Right now, your PRINT_START, G32, CLEAN_NOZZLE, and PRINT_END call STATUS_* and CHAMBER_* instead of your animated led_* macros. Update those calls in macros.cfg so your chamber progress bar and toolhead effects actually run:

Old Call in macros.cfg	Replace With (led_effect Macro)
STATUS_HOMING	led_homing
STATUS_HEATING + CHAMBER_HEATING	led_heating
STATUS_CLEANING + CHAMBER_CLEANING	led_cleaning
STATUS_LEVELING	led_leveling
STATUS_MESHING	led_meshing
STATUS_PRINTING + CHAMBER_LIGHTS_ON	led_printing (runs your left/right chamber progress bars!)
STATUS_READY + CHAMBER_READY	led_standby (also starts your 2-hour auto-sleep timer)

(Note: Keep klipper-led_effect installed on your Pi—if you ever get Section 'led_effect ...' is not a valid config section on reboot, reinstall julianschill/klipper-led_effect via KIAUH or SSH).
Would you like me to output a clean, single consolidated macros.cfg with led_* calls wired into G32, CLEAN_NOZZLE, PRINT_START, and PRINT_END, or are you ready to load these onto the printer and run your first QUERY_ENDSTOPS / STEPPER_BUZZ tests?
Here is your clean, consolidated macros.cfg, pre-wired to your led_* effects, Voron Tap 150°C probing sequence, and 350mm LDO CNC AWD travel limits (Y340 max).

Before Pasting This macros.cfg

Make sure your printer.cfg has these 3 exact items (and no duplicate [neopixel] or macro definitions at the bottom):
1. [include macros.cfg] and [include stealthburner_leds.cfg] at the top of printer.cfg.
2. [exclude_object] added anywhere in printer.cfg (required for BED_MESH_CALIBRATE ADAPTIVE=1).
3. [neopixel caselight] set to pin: PF12 (Kraken v1.1 RGB1, not PB0) and [neopixel sb_leds] set to chain_count: 10 inside stealthburner_leds.cfg (delete [neopixel chamber_leds] and the old 3-LED [neopixel sb_leds] from printer.cfg).

Clean macros.cfg

ini
# =====================================================================
# Custom Macros - Voron 2.4 350mm AWD (Kraken v1.1 + EBB SB2209 + Tap)
# =====================================================================

[gcode_macro PARK]
gcode:
    {% set th = printer.toolhead %}
    G0 X{th.axis_maximum.x//2} Y{th.axis_maximum.y//2} Z30 F6000

# ---------------------------------------------------------------------
# Nozzle Brush Variables (Adjusted for AWD Y max = 340)
# ---------------------------------------------------------------------
[gcode_macro _CLEAN_VARIABLES]
variable_start_x: 115            # Start cleaning X position
variable_start_y: 339            # Start cleaning Y position (must stay <= position_max: 340)
variable_start_z: 3.0            # Bristle scrub Z height (test at Z10 first!)

variable_wipe_dist: 60           # Wipe stroke distance in X (+60 -> X115 to X175)
variable_wipe_qty: 6             # Number of back-and-forth wipes
variable_wipe_spd: 200           # Wipe speed (mm/s)

variable_raise_distance: 25      # Safe Z height after wiping
variable_end_position_x: 155     # Exit X position
variable_end_position_y: 330     # Exit Y position
variable_end_position_z: 25      # Exit Z position
gcode:

# ---------------------------------------------------------------------
# CLEAN_NOZZLE Macro
# ---------------------------------------------------------------------
[gcode_macro CLEAN_NOZZLE]
gcode:
    {% set cv = printer["gcode_macro _CLEAN_VARIABLES"] %}
    {% set spd = cv.wipe_spd * 60 %}

    {% if "xyz" not in printer.toolhead.homed_axes %}
        G28
    {% endif %}

    SAVE_GCODE_STATE NAME=STATE_CLEAN_NOZZLE
    G90

    led_cleaning

    # Move safely above brush before dropping Z
    G0 Z{cv.raise_distance} F3000
    G0 X{cv.start_x} Y{cv.start_y} F9000
    G0 Z{cv.start_z} F1500

    # Wipe back and forth across the brush
    {% for i in range(cv.wipe_qty) %}
        G0 X{cv.start_x + cv.wipe_dist} F{spd}
        G0 X{cv.start_x} F{spd}
    {% endfor %}

    # Lift and move to safe exit position
    G0 Z{cv.raise_distance} F3000
    G0 X{cv.end_position_x} Y{cv.end_position_y} Z{cv.end_position_z} F6000

    RESTORE_GCODE_STATE NAME=STATE_CLEAN_NOZZLE

# ---------------------------------------------------------------------
# G32 - Full Home, Nozzle Clean & Quad Gantry Level
# ---------------------------------------------------------------------
[gcode_macro G32]
gcode:
    SAVE_GCODE_STATE NAME=STATE_G32
    G90
    led_homing
    G28
    CLEAN_NOZZLE
    led_leveling
    QUAD_GANTRY_LEVEL
    led_homing
    G28 Z
    PARK
    led_standby
    RESTORE_GCODE_STATE NAME=STATE_G32

# ---------------------------------------------------------------------
# PRINT_START (Voron Tap + Smart Chamber Soak + Brush + Adaptive Mesh)
# ---------------------------------------------------------------------
[gcode_macro PRINT_START]
gcode:
    {% set target_bed = params.BED|int %}
    {% set target_extruder = params.EXTRUDER|int %}
    {% set target_chamber = params.CHAMBER|default("40")|int %}
    {% set x_wait = printer.toolhead.axis_maximum.x|float / 2 %}
    {% set y_wait = printer.toolhead.axis_maximum.y|float / 2 %}
    {% set current_chamber = printer["temperature_sensor chamber"].temperature|float %}

    # Clear any previous bed mesh and home all axes
    BED_MESH_CLEAR
    led_homing
    G28
    G90

    # Heat bed & handle chamber heatsoak for ABS/ASA (> 90C)
    led_heating
    G0 X{x_wait} Y{y_wait} Z15 F9000

    {% if target_bed > 90 %}
        SET_DISPLAY_TEXT MSG="Bed: {target_bed}C"
        M106 S255                                           # Part fan on to circulate chamber air
        SET_FAN_SPEED FAN=exhaust_fan SPEED=1.0             # Turn on Nevermore / circulation fan
        M190 S{target_bed}

        # Run 10-min MIC6 soak only if chamber isn't already warm from a previous print
        {% if current_chamber < (target_chamber - 2) %}
            SET_DISPLAY_TEXT MSG="MIC6 Soak: 10 min"
            G4 P600000
        {% endif %}

        SET_DISPLAY_TEXT MSG="Chamber Wait: {target_chamber}C"
        TEMPERATURE_WAIT SENSOR="temperature_sensor chamber" MINIMUM={target_chamber}
    {% else %}
        SET_DISPLAY_TEXT MSG="Bed: {target_bed}C"
        M190 S{target_bed}
        {% if printer.heater_bed.temperature < (target_bed - 5) %}
            SET_DISPLAY_TEXT MSG="MIC6 Soak: 5 min"
            G4 P300000
        {% endif %}
    {% endif %}

    # Heat nozzle to 150C (safe probing temp for Voron Tap) & scrub tip before probing
    SET_DISPLAY_TEXT MSG="Hotend: 150C (Tap Prep)"
    M109 S150
    SET_DISPLAY_TEXT MSG="Cleaning Nozzle..."
    CLEAN_NOZZLE

    # Quad Gantry Leveling & Re-home Z with clean 150C nozzle
    SET_DISPLAY_TEXT MSG="Quad Gantry Level"
    led_leveling
    QUAD_GANTRY_LEVEL
    led_homing
    G28 Z

    # Native Klipper Adaptive Bed Mesh (requires [exclude_object] in printer.cfg)
    SET_DISPLAY_TEXT MSG="Adaptive Bed Mesh"
    led_meshing
    BED_MESH_CALIBRATE ADAPTIVE=1

    # Heat nozzle to final printing temperature & do a final wipe
    SET_DISPLAY_TEXT MSG="Hotend: {target_extruder}C"
    led_heating
    G0 X{x_wait} Y{y_wait} Z15 F9000
    M107                                                    # Turn off part cooling fan
    M109 S{target_extruder}
    SET_DISPLAY_TEXT MSG="Final Nozzle Wipe..."
    CLEAN_NOZZLE

    # Purge line at front-center-left (Y10 is safe for front AWD mounts; verify clearance)
    SET_DISPLAY_TEXT MSG="Purging..."
    led_purge
    G0 X{x_wait - 50} Y10 F10000
    G0 Z0.4
    G91
    G1 X100 E20 F1000
    G90

    # Start print & activate progress bar LEDs
    led_printing
    SET_DISPLAY_TEXT MSG="Printing..."

# ---------------------------------------------------------------------
# PRINT_END (Retract, Safe AWD Park, Cooldown & Standby LEDs)
# ---------------------------------------------------------------------
[gcode_macro PRINT_END]
gcode:
    {% set th = printer.toolhead %}
    {% set x_safe = th.position.x + 20 * (1 if th.axis_maximum.x - th.position.x > 20 else -1) %}
    {% set y_safe = th.position.y + 20 * (1 if th.axis_maximum.y - th.position.y > 20 else -1) %}
    {% set z_safe = [th.position.z + 10, th.axis_maximum.z]|min %}

    SAVE_GCODE_STATE NAME=STATE_PRINT_END

    M400                                                    # Wait for buffer to clear
    G92 E0                                                  # Zero the extruder
    G1 E-5.0 F1800                                          # Retract filament out of meltzone

    TURN_OFF_HEATERS
    M107                                                    # Turn off part cooling fan

    G90                                                     # Absolute positioning
    G0 X{x_safe} Y{y_safe} Z{z_safe} F20000                 # String-breaking wipe move
    G0 X{th.axis_maximum.x//2} Y{th.axis_maximum.y - 15} F3600  # Park rear-center (Y325, safe for AWD)

    BED_MESH_CLEAR
    led_standby
    SET_DISPLAY_TEXT MSG="Print Complete"

    RESTORE_GCODE_STATE NAME=STATE_PRINT_END
Use code with caution.
Once you upload this file and restart Klipper, let me know if Klipper boots cleanly or if you hit any startup messages or endstop/stepper check questions during commissioning!
