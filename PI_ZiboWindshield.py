"""
ZiboWindshield
X-Plane plugin

Copyright (c) 2025, Antonio Golfari
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""

import math

from datetime import datetime
from time import perf_counter

try:
    from XPPython3 import xp
    from XPPython3.utils.datarefs import find_dataref
except ImportError:
    print('xp module not found')
    pass


# Version
__VERSION__ = 'v2.0.0'

# Plugin parameters required from XPPython3
plugin_name = 'ZiboWindshield'
plugin_sig = 'xppython3.zibowindshield'
plugin_desc = 'Simple Python script to change rain or ice depiction on cockpit windshield'

# Other parameters
DEFAULT_SCHEDULE = 3  # positive numbers are seconds, 0 disabled, negative numbers are cycles
ICE_SCHEDULE = -1  # positive numbers are seconds, 0 disabled, negative numbers are cycles
IDLE_SCHEDULE = 30  # positive numbers are seconds, 0 disabled, negative numbers are cycles 

# Raindrops parameters
RAIN = False  # at the moment no raindrops adjustment is needed
ZIBO_RAIN_FORCE_FACTOR = 0.05
ZIBO_FRICTION_DYNAMIC = 0.1
ZIBO_HISTORY_RATE = 0.1
ZIBO_RAIN_MAX_FORCE = 50
ZIBO_RAIN_SCALE = 0.5
ZIBO_RAIN_SPAWN = 70000

DEFAULT_RAIN_FORCE_FACTOR = 0.1
DEFAULT_FRICTION_DYNAMIC = 0.3
DEFAULT_HISTORY_RATE = 0.04
DEFAULT_RAIN_MAX_FORCE = 50
DEFAULT_RAIN_SCALE = 1
DEFAULT_RAIN_SPAWN = 1000

# Ice parameters
ICE = True  # set full iced windshield at cold and dark start
ICE_ADDED_DELTA = 0.99

# Aircrafts
AIRCRAFTS = [
    ('Zibo', 'B737-800X'),
    ('LevelUp', 'LevelUp')
]


# widget parameters
try:
    FONT = xp.Font_Proportional
    FONT_WIDTH, FONT_HEIGHT, _ = xp.getFontDimensions(FONT) or (10, 10, 0)
except NameError:
    FONT_WIDTH, FONT_HEIGHT = 10, 10


class Dref:

    def __init__(self) -> None:
        self._rain_force_factor_dref = find_dataref('sim/private/controls/rain/force_factor')
        self._friction_dynamic_dref = find_dataref('sim/private/controls/rain/friction_dynamic')
        self._history_rate_dref = find_dataref('sim/private/controls/rain/history_rate')
        self._rain_max_force_dref = find_dataref('sim/private/controls/rain/max_force')
        self._rain_scale_dref = find_dataref('sim/private/controls/rain/scale')
        self._rain_spawn_dref = find_dataref('sim/private/controls/rain/spawn_adjust')

        self._window_ice = find_dataref('sim/flightmodel/failures/window_ice')
        self._window_ice_added_delta = find_dataref('sim/flightmodel/failures/window_ice_added_delta')
        self._window_ice_unheated = find_dataref('sim/flightmodel/failures/window_ice_unheated')

        self._battery_pos = find_dataref('laminar/B738/electric/battery_pos')
        self._on_ground = find_dataref('sim/flightmodel2/gear/on_ground')

    @property
    def rain_needs_adjustment(self) -> bool:
        try:
            return not math.isclose(self._rain_force_factor_dref.value, ZIBO_RAIN_FORCE_FACTOR, rel_tol=0.1)
        except SystemError as e:
            xp.log(f"ERROR: {e}")
            return False

    @property
    def cold_and_dark(self) -> bool:
        try:
            return self._battery_pos.value == 0 and any(self._on_ground.value)
        except SystemError as e:
            xp.log(f"ERROR: {e}")
            return False

    @property
    def icy_condition(self) -> bool:
        return self._window_ice_unheated.value > 0

    def _set(self, dref, value: float) -> None:
        try:
            dref.value = value
        except SystemError as e:
            xp.log(f"ERROR: {e}")

    def adjust_icing(self) -> None:
        self._set(self._window_ice_added_delta, ICE_ADDED_DELTA)

    def adjust(self) -> None:
        self._set(self._rain_force_factor_dref, ZIBO_RAIN_FORCE_FACTOR)
        self._set(self._friction_dynamic_dref, ZIBO_FRICTION_DYNAMIC)
        self._set(self._history_rate_dref, ZIBO_HISTORY_RATE)
        self._set(self._rain_max_force_dref, ZIBO_RAIN_MAX_FORCE)
        self._set(self._rain_scale_dref, ZIBO_RAIN_SCALE)
        self._set(self._rain_spawn_dref, ZIBO_RAIN_SPAWN)

    def reset(self) -> None:
        self._set(self._rain_force_factor_dref, DEFAULT_RAIN_FORCE_FACTOR)
        self._set(self._friction_dynamic_dref, DEFAULT_FRICTION_DYNAMIC)
        self._set(self._history_rate_dref, DEFAULT_HISTORY_RATE)
        self._set(self._rain_max_force_dref, DEFAULT_RAIN_MAX_FORCE)
        self._set(self._rain_scale_dref, DEFAULT_RAIN_SCALE)
        self._set(self._rain_spawn_dref, DEFAULT_RAIN_SPAWN)


class PythonInterface:

    def __init__(self) -> None:
        self.plugin_name = f"{plugin_name} - {__VERSION__}"
        self.plugin_sig = plugin_sig
        self.plugin_desc = plugin_desc

        # Dref init
        self.dref = False

        self.started = False  # started pre flight, to inhibit cold and dark

    @property
    def aircraft_path(self) -> str:
        _, acf_path = xp.getNthAircraftModel(0)
        return acf_path

    @property
    def aircraft_detected(self) -> bool:
        loaded = bool(any(p[1] in self.aircraft_path for p in AIRCRAFTS))
        if loaded and self.dref is False:
            self.dref = Dref()
        elif not loaded and isinstance(self.dref, Dref):
            self.dref.reset()
            self.dref = False
        return loaded

    def loopCallback(self, lastCall, elapsedTime, counter, refCon) -> int:
        """Loop Callback"""
        t = datetime.now()
        start = perf_counter()
        if self.aircraft_detected and isinstance(self.dref, Dref):
            # check if we need to change parameters
            if RAIN and self.dref.rain_needs_adjustment:
                self.dref.adjust()
            if ICE and self.dref.icy_condition and not self.started:
                if self.dref.cold_and_dark:
                    self.dref.adjust_icing()
                    return ICE_SCHEDULE
                else:
                    self.started = True
            return IDLE_SCHEDULE

        return DEFAULT_SCHEDULE

    def XPluginStart(self) -> tuple[str, str, str]:
        return self.plugin_name, self.plugin_sig, self.plugin_desc

    def XPluginEnable(self) -> int:
        # loopCallback
        self.loop = self.loopCallback
        self.loop_id = xp.createFlightLoop(self.loop, phase=1)
        xp.scheduleFlightLoop(self.loop_id, interval=DEFAULT_SCHEDULE)
        return 1

    def XPluginDisable(self) -> None:
        pass

    def XPluginStop(self) -> None:
        # Called once by X-Plane on quit (or when plugins are exiting as part of reload)
        xp.destroyFlightLoop(self.loop_id)
        xp.log("flightloop closed, exiting ...")
