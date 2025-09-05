from typing import Tuple

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), (128, 128, 128), (50, 50, 150)),
    light=(ord("."), (204, 204, 204), (200, 180, 50)),
)
wall = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
    light=(ord(" "), (255, 255, 255), (130, 110, 50)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
    light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)
city_wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (130, 110, 50), (0, 0, 100)),
    light=(ord("#"), (130, 110, 50), (200, 180, 50)),
)
door = new_tile(
    walkable=True,
    transparent=False,
    dark=(ord("+"), (0xE0, 0x64, 0x1E), (0x99, 0x45, 0x15)),
    light=(ord("+"), (0xFF, 0x8C, 0x33), (0xCC, 0x5C, 0x1C)),
)
portal_blue = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("O"), (0, 0, 255), (0, 0, 100)),
    light=(ord("O"), (0, 128, 255), (0, 0, 150)),
)
portal_red = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("O"), (255, 0, 0), (100, 0, 0)),
    light=(ord("O"), (255, 128, 128), (150, 0, 0)),
)