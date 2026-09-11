# ShieldingCan

**ShieldingCan** is a KiCad 9 Action Plugin for creating PCB mounting
areas for shielding cans.

The plugin generates rows of stitching vias and solder-mask openings
around a selected rectangular area, making it easier to prepare a PCB
for soldered metal shielding cans.

## Features

-   Generates via fences around a rectangular area
-   Multiple via rows
-   Adjustable via diameter, drill size, pitch, offsets, and spacing
-   Optional staggered via pattern
-   Solder-mask openings on F.Mask, B.Mask, or both
-   Build inside or outside the selected rectangle
-   Automatic avoidance of tracks, pads, existing vias, and courtyard
    areas
-   Automatic via-pitch adjustment
-   Assigns generated vias to a selected net
-   mm and mil units
-   English, German, and Ukrainian interface
-   Settings are saved between sessions

## Requirements

-   KiCad 9.x

## Installation

Copy the plugin files into your KiCad Action Plugins directory:

-   `shieldingcan.py`
-   `shieldingcan.png`

Restart KiCad and open **PCB Editor**. ShieldingCan should appear in the
Action Plugins menu/toolbar.

## Usage

1.  Draw a rectangle on the **User.Drawings** layer.
2.  Select the rectangle.
3.  Run **ShieldingCan**.
4.  Configure the via fence and solder-mask parameters.
5.  Select the required net and click **OK**.

The generated objects are placed in the `SHIELDING_CAN` group.

> Zones and polygons are ignored when calculating obstacles.

## License

GPL-3.0
