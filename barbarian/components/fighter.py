from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from render_order import RenderOrder
import entity

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, 
                 hp: int, 
                 base_defense: int, 
                 base_power: int, 
                 base_pen: int, 
                 base_ms: int,
                 base_qn:int,
                 mp:int,
                 base_mdef: int,
                 base_mpow:int,
                 magic_qn:int,
                 mental:int,
                 slots:int,
                 holy:int,
                 luck:int,
                 equip: int,
                 ):
        self.max_hp = hp
        self._hp = hp
        self.base_pen = base_pen
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_qn = base_qn
        self.base_ms = base_ms
        self.qn_remainder = 0
        self.ms_remainder = 0  # Остаток скорости
        self.max_mp = mp
        self._mp = mp
        self.base_mdef = base_mdef
        self.base_mpow = base_mpow
        self.magic_qn = magic_qn
        self.max_mental = mental
        self._mental = mental
        self.max_slots = slots
        self._slots = slots
        self.max_holy = holy
        self._holy = holy
        self._luck = luck
        self._equip = equip

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def mp(self) -> int:
        return self._mp
    
    @mp.setter
    def mp(self, value:int) -> None:
        self._mp = max(0,min(value, self.max_mp))
    
    @property
    def holy(self) -> int:
        return self._holy
    
    @holy.setter
    def holy(self, value:int) -> None:
        self._mp = max(0,min(value, self.max_holy))

    @property
    def luck(self) -> int:
        return self._luck + self.luck_bonus

    @property
    def luck_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.luck_bonus
        else:
            return 0

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def equip(self) -> int:
        return self.parent.equipment.equiprate

    @property
    def power(self) -> int:
        return self.base_power

    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0
    
    @property
    def pen(self) -> int:
        return self.base_pen + self.pen_bonus
    
    @property
    def pen_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.pen_bonus
        else:
            return 0
    
    @property
    def ms(self) -> int:
        return self.base_ms + self.ms_bonus
    
    @property
    def ms_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.ms_bonus
        else:
            return 0

    @property
    def qn(self) -> int:
        return self.base_qn + self.qn_bonus + self.qn_remainder
    
    @qn.setter
    def qn(self, value:int):
        self.qn_remainder = value
    
    @property
    def qn_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.qn_bonus
        else:
            return 0
        



    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        monster_type = self.parent.name
        if monster_type not in self.engine.tracked_monsters:
            self.engine.tracked_monsters.add(monster_type)
            self.engine.player.level.add_xp(self.parent.level.xp_given)
        else:
            self.engine.message_log.add_message(
                f"You've already defeated a {monster_type} before.", color.invalid
            )

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def can_move(self) -> bool:
        """Проверяет, может ли сущность совершить ход на текущем ходу.

        Возвращает True, если у сущности достаточно MS для хода, False в противном случае."""
        self.ms_remainder += self.ms
        if self.ms_remainder >= 100:
            return True
        return False

    def consume_move(self) -> None:
        """Уменьшает ms_remainder после совершения хода."""
        self.ms_remainder -= 100  # Потребляем 100 MS для хода
        self.ms_remainder = max(0, self.ms_remainder)  # Не даем остатку уйти в минус

    def get_extra_moves(self) -> int:
        """Возвращает количество дополнительных ходов, которые можно совершить."""
        return self.ms_remainder // 100