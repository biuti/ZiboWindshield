# ZiboWindshield
Simple Python script to change precipitations depiction and ice on Zibo and LevelUp cockpit windshield

## Features
- The plugins changes values of some rain related datarefs to solve the issue of the uneffective wipers on the Zibo B737-800 Modified. It's been tested up to 200kt and the wipers maintain their effectiveness
- Also changes rain depiction to be a bit more realistic
- When started in Cold and Dark situation, and weather conditions are prone to ice formation, windshield will be fully covered with ice at startup, without any need to wait for ice to build up, adding immersion and realism

> [!NOTE]
> raindrops modification is not needed in present XP12 version, so it is disabled by default

## Requirements
- MacOS 10.14, Windows 7 and Linux kernel 4.0 and above
- X-Plane 12.1.4 and above (not tested with previous versions, may work)
- pbuckner's [XPPython3 plugin](https://xppython3.readthedocs.io/en/latest/index.html)
- [Zibo B737-800 Modified](https://forums.x-plane.org/index.php?/forums/forum/384-zibo-b738-800-modified/) for X-Plane 12 **ver. 4.04** and above (**may be compatible with some previous versions**) or [LevelUp B737NG Series](https://forum.thresholdx.net/files/file/3865-levelup-737ng-series/) for X-Plane 12 **ver. U1**

> [!IMPORTANT]
> **I strongly suggest to install latest available version of the XPPython3 plugin.
Starting from ver. 4.3.0 it is not needed to install Python3 on your system, and all needed libraries are already installed, so it's a lot easier to manage.\
\
Otherwise, in the very unfortunate case you stick with previous versions of the plugin, you'll need to download correct XPPython3 version according to your Python3 installed version.\
\
Read [instructions](https://xppython3.readthedocs.io/en/latest/usage/installation_plugin.html) on the website**

## Installation
Just copy or move the file _PI_ZiboWindshield.py_ to the folder:

    X-Plane/Resources/plugins/PythonPlugins/