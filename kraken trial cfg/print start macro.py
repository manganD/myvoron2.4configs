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
variable_start_y: 339            # Start cleaning Y position (verify <= position_max: 340)
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

    STATUS_CLEANING
    CHAMBER_CLEANING

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
# Chamber LED Helpers (Matches [neopixel chamber_leds] in printer.cfg)
# ---------------------------------------------------------------------
[gcode_macro CHAMBER_LIGHTS_ON]
gcode:
    SET_LED LED=chamber_leds RED=0.8 GREEN=0.8 BLUE=0.8

[gcode_macro CHAMBER_LIGHTS_OFF]
gcode:
    SET_LED LED=chamber_leds RED=0.0 GREEN=0.0 BLUE=0.0

[gcode_macro CHAMBER_HEATING]
gcode:
    SET_LED LED=chamber_leds RED=0.8 GREEN=0.1 BLUE=0.0

[gcode_macro CHAMBER_CLEANING]
gcode:
    SET_LED LED=chamber_leds RED=0.0 GREEN=0.6 BLUE=0.8

[gcode_macro CHAMBER_READY]
gcode:
    SET_LED LED=chamber_leds RED=0.2 GREEN=0.8 BLUE=0.2

# ---------------------------------------------------------------------
# G32 - Full Home, Nozzle Clean & Quad Gantry Level
# ---------------------------------------------------------------------
[gcode_macro G32]
gcode:
    SAVE_GCODE_STATE NAME=STATE_G32
    G90
    STATUS_HOMING
    G28
    CLEAN_NOZZLE
    STATUS_LEVELING
    QUAD_GANTRY_LEVEL
    STATUS_HOMING
    G28
    PARK
    STATUS_READY
    CHAMBER_READY
    RESTORE_GCODE_STATE NAME=STATE_G32

# ---------------------------------------------------------------------
# PRINT_START (Voron Tap + Chamber Heatsoak + Nozzle Brush + Adaptive Mesh)
# ---------------------------------------------------------------------
[gcode_macro PRINT_START]
gcode:
    {% set target_bed = params.BED|int %}
    {% set target_extruder = params.EXTRUDER|int %}
    {% set target_chamber = params.CHAMBER|default("40")|int %}
    {% set x_wait = printer.toolhead.axis_maximum.x|float / 2 %}
    {% set y_wait = printer.toolhead.axis_maximum.y|float / 2 %}

    # Clear any previous bed mesh and home all axes
    BED_MESH_CLEAR
    STATUS_HOMING
    G28
    G90

    # Heat bed & handle chamber heatsoak for ABS/ASA (> 90C)
        # Heat bed & run 10-minute MIC6 aluminum plate thermal stabilization soak
    CHAMBER_HEATING
    STATUS_HEATING
    G0 X{x_wait} Y{y_wait} Z15 F9000

    {% if target_bed > 90 %}
        SET_DISPLAY_TEXT MSG="Bed: {target_bed}C"
        M106 S255                                           # Part fan on to circulate chamber air
        SET_FAN_SPEED FAN=exhaust_fan SPEED=1.0             # Turn on Nevermore / circulation fan
        M190 S{target_bed}
        SET_DISPLAY_TEXT MSG="MIC6 Soak: 10 min"
        G4 P600000                                          # 10-min thermal soak for 350mm MIC6 plate
        SET_DISPLAY_TEXT MSG="Chamber Wait: {target_chamber}C"
        TEMPERATURE_WAIT SENSOR="temperature_sensor chamber" MINIMUM={target_chamber}
    {% else %}
        SET_DISPLAY_TEXT MSG="Bed: {target_bed}C"
        M190 S{target_bed}
        SET_DISPLAY_TEXT MSG="MIC6 Soak: 10 min"
        G4 P600000                                          # 10-min thermal soak for 350mm MIC6 plate
    {% endif %}

    # Heat nozzle to 150C (safe probing temp for Voron Tap) & scrub tip before probing
    SET_DISPLAY_TEXT MSG="Hotend: 150C (Tap Prep)"
    M109 S150
    SET_DISPLAY_TEXT MSG="Cleaning Nozzle..."
    CLEAN_NOZZLE

    # Quad Gantry Leveling & Re-home Z with clean 150C nozzle
    SET_DISPLAY_TEXT MSG="Quad Gantry Level"
    STATUS_LEVELING
    QUAD_GANTRY_LEVEL
    STATUS_HOMING
    G28 Z

    # Native Klipper Adaptive Bed Mesh (requires [exclude_object] in printer.cfg)
    SET_DISPLAY_TEXT MSG="Adaptive Bed Mesh"
    STATUS_MESHING
    BED_MESH_CALIBRATE ADAPTIVE=1

    # Heat nozzle to final printing temperature & do a final wipe
    SET_DISPLAY_TEXT MSG="Hotend: {target_extruder}C"
    STATUS_HEATING
    G0 X{x_wait} Y{y_wait} Z15 F9000
    M107                                                    # Turn off part cooling fan
    M109 S{target_extruder}
    SET_DISPLAY_TEXT MSG="Final Nozzle Wipe..."
    CLEAN_NOZZLE

    # Purge line at front-left of bed
    SET_DISPLAY_TEXT MSG="Purging..."
    CHAMBER_LIGHTS_ON
    STATUS_PRINTING
    G0 X{x_wait - 50} Y4 F10000
    G0 Z0.4
    G91
    G1 X100 E20 F1000
    G90
    SET_DISPLAY_TEXT MSG="Printing..."

# ---------------------------------------------------------------------
# PRINT_END
# ---------------------------------------------------------------------
[gcode_macro PRINT_END]
gcode:
    {% set th = printer.toolhead %}
    {% set x_safe = th.position.x + 20 * (1 if th.axis_maximum.x - th.position.x > 20 else -1) %}
    {% set y_safe = th.position.y + 20 * (1 if th.axis_maximum.y - th.position.y > 20 else -1) %}
    {% set z_safe = [th.position.z + 2, th.axis_maximum.z]|min %}

    SAVE_GCODE_STATE NAME=STATE_PRINT_END

    M400                                                    # Wait for buffer to clear
    G92 E0                                                  # Zero the extruder
    G1 E-5.0 F1800                                          # Retract filament

    TURN_OFF_HEATERS

    G90
    G0 X{x_safe} Y{y_safe} Z{z_safe} F20000                 # String-break move
    G0 X{th.axis_maximum.x//2} Y{th.axis_maximum.y - 5} F3600  # Park nozzle at rear
    M107                                                    # Turn off part fan
    SET_FAN_SPEED FAN=exhaust_fan SPEED=0.0                 # Turn off Nevermore / exhaust fan

    BED_MESH_CLEAR
    STATUS_READY
    CHAMBER_READY
    RESTORE_GCODE_STATE NAME=STATE_PRINT_END

# ---------------------------------------------------------------------
# Full Hotend + Bed PID Calibration Helper
# ---------------------------------------------------------------------
[gcode_macro PID_TUNE_FULL]
gcode:
    {% set noz_temp = params.NOZZLE_TARGET|default(250)|float %}
    {% set bed_temp = params.BED_TARGET|default(100)|float %}
    {% set x_park = printer.toolhead.axis_maximum.x|float / 2 %}
    {% set y_park = printer.toolhead.axis_maximum.y|float / 2 %}

    STATUS_BUSY
    G90
    {% if "xyz" not in printer.toolhead.homed_axes %}
        STATUS_HOMING
        G28
    {% endif %}

    G0 X{x_park} Y{y_park} Z15 F9000
    M106 S155
    STATUS_HEATING
    SET_DISPLAY_TEXT MSG="PID Tuning Extruder ({noz_temp}C)..."
    PID_CALIBRATE HEATER=extruder TARGET={noz_temp}
    M400
    M106 S0

    G0 Z50 F9000
    SET_DISPLAY_TEXT MSG="PID Tuning Bed ({bed_temp}C)..."
    PID_CALIBRATE HEATER=heater_bed TARGET={bed_temp}
    M400

    STATUS_READY
    SET_DISPLAY_TEXT MSG="PID Complete! Run SAVE_CONFIG"
