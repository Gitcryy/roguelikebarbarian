from __future__ import annotations
import random as r
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from equipment_types import EquipmentType
from actions import MeleeAction

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_min:int = 0,
        power_max:int=0,
        pen_bonus: int = 0,
        defense_bonus: int = 0,
        ms_bonus: int = 0,
        qn_bonus:int = 0,
        luck_bonus:int = 0,
        equiprate: int = 0,
    ):
        self.power_min = power_min
        self.power_max = power_max
        self.equipment_type = equipment_type
        self.defense_bonus = defense_bonus
        self.pen_bonus = pen_bonus
        self.ms_bonus = ms_bonus
        self.qn_bonus = qn_bonus
        self.luck_bonus = luck_bonus
        self.equiprate = equiprate

    def get_power_bonus(self) -> int:
        """Returns a random power bonus based on power_min and power_max."""
        return r.randint(self.power_min, self.power_max)


class Dagger(Equippable):   
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON,power_min = 1, power_max=2, pen_bonus=2)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON,power_min = 1, power_max=4, pen_bonus=4) 


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1, pen_bonus=0, ms_bonus=0)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3, pen_bonus=0)
