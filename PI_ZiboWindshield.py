"""
ZiboWindshield
X-Plane plugin

Copyright (c) 2023, Antonio Golfari
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""

import math

from datetime import datetime
from time import perf_counter

try:
    from XPPython3 import xp
except ImportError:
    print('xp module not found')
    pass


# Version
__VERSION__ = 'v1.0-beta'

# Plugin parameters required from XPPython3
plugin_name = 'ZiboWindshield'
plugin_sig = 'xppython3.zibowindshield'
plugin_desc = 'Simple Python script to change rain depiction on cockpit windshield'

# Other parameters
DEFAULT_SCHEDULE = 3  # positive numbers are seconds, 0 disabled, negative numbers are cycles

ZIBO_RAIN_FORCE_FACTOR = 0.005
ZIBO_FRICTION_DYNAMIC = 0.05
ZIBO_RAIN_MAX_FORCE = 20
ZIBO_RAIN_SCALE = 0.5
ZIBO_RAIN_SPAWN = 2000

DEFAULT_RAIN_FORCE_FACTOR = 0.1
DEFAULT_FRICTION_DYNAMIC = 0.3
DEFAULT_RAIN_MAX_FORCE = 50
DEFAULT_RAIN_SCALE = 1
DEFAULT_RAIN_SPAWN = 1000


# widget parameters
try:
    FONT = xp.Font_Proportional
    FONT_WIDTH, FONT_HEIGHT, _ = xp.getFontDimensions(FONT)
except NameError:
    FONT_WIDTH, FONT_HEIGHT = 10, 10


class Dref(object):

    def __init__(self) -> None:
        self._rain_force_factor_dref = xp.findDataRef('sim/private/controls/rain/force_factor')
        self._friction_dynamic_dref = xp.findDataRef('sim/private/controls/rain/friction_dynamic')
        self._rain_max_force_dref = xp.findDataRef('sim/private/controls/rain/max_force')
        self._rain_scale_dref = xp.findDataRef('sim/private/controls/rain/scale')
        self._rain_spawn_dref = xp.findDataRef('sim/private/controls/rain/spawn_adjust')

    @property
    def need_adjustment(self) -> bool:
        try:
            return not math.isclose(xp.getDataf(self._rain_force_factor_dref), ZIBO_RAIN_FORCE_FACTOR, rel_tol=0.2)
        except SystemError as e:
            xp.log(f"ERROR: {e}")
            return False

    def _set(self, dref, value: float) -> bool:
        try:
            xp.setDataf(dref, value)
        except SystemError as e:
            xp.log(f"ERROR: {e}")
            return False

    def adjust(self) -> bool:
        self._set(self._rain_force_factor_dref, ZIBO_RAIN_FORCE_FACTOR)
        self._set(self._friction_dynamic_dref, ZIBO_FRICTION_DYNAMIC)
        self._set(self._rain_max_force_dref, ZIBO_RAIN_MAX_FORCE)
        self._set(self._rain_scale_dref, ZIBO_RAIN_SCALE)
        self._set(self._rain_spawn_dref, ZIBO_RAIN_SPAWN)

    def reset(self) -> bool:
        self._set(self._rain_force_factor_dref, DEFAULT_RAIN_FORCE_FACTOR)
        self._set(self._friction_dynamic_dref, DEFAULT_FRICTION_DYNAMIC)
        self._set(self._rain_max_force_dref, DEFAULT_RAIN_MAX_FORCE)
        self._set(self._rain_scale_dref, DEFAULT_RAIN_SCALE)
        self._set(self._rain_spawn_dref, DEFAULT_RAIN_SPAWN)


class PythonInterface(object):

    def __init__(self) -> None:
        self.plugin_name = f"{plugin_name} - {__VERSION__}"
        self.plugin_sig = plugin_sig
        self.plugin_desc = plugin_desc

        # Dref init
        self.dref = False

    @property
    def aircraft_path(self) -> str:
        _, acf_path = xp.getNthAircraftModel(0)
        return acf_path

    @property
    def zibo_loaded(self) -> bool:
        loaded = 'B737-800X' in self.aircraft_path
        # load drefs if needed
        if loaded and not self.dref:
            self.dref = Dref()
        elif not loaded and self.dref:
            self.dref = False
        return loaded

    def loopCallback(self, lastCall, elapsedTime, counter, refCon):
        """Loop Callback"""
        t = datetime.now()
        start = perf_counter()
        if self.zibo_loaded:
            # check if we need to change parameters
            if self.dref and self.dref.need_adjustment:
                xp.log(f" {t.strftime('%H:%M:%S')} - Rain needs adjustment")
                self.dref.adjust()
            return DEFAULT_SCHEDULE * 10

        return DEFAULT_SCHEDULE

    def XPluginStart(self):
        return self.plugin_name, self.plugin_sig, self.plugin_desc

    def XPluginEnable(self):
        # loopCallback
        self.loop = self.loopCallback
        self.loop_id = xp.createFlightLoop(self.loop, phase=1)
        xp.scheduleFlightLoop(self.loop_id, interval=DEFAULT_SCHEDULE)
        return 1

    def XPluginDisable(self):
        pass

    def XPluginStop(self):
        # Called once by X-Plane on quit (or when plugins are exiting as part of reload)
        xp.destroyFlightLoop(self.loop_id)
        xp.log("flightloop closed, exiting ...")
