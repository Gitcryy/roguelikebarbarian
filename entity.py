from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from game_map import GameMap
    from entity_factories import MONSTER_GROUP_TEMPLATES

T = TypeVar("T", bound="Entity")



class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone



    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entitiy at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class   Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,
        archer:bool = False,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self
        self.archer = archer

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)
    
    


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self

class Usableentity(Entity):
    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        interaction_message: str = "You interact with the object.",
        blocks_movement: bool = False,
    ):
        super().__init__(
            parent=parent,
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=blocks_movement,
            render_order=RenderOrder.CORPSE,  # Или другой подходящий порядок
        )
        self.interaction_message = interaction_message

    def interact(self, player: Actor) -> None:
        """Метод, вызываемый при взаимодействии с игроком"""
        # Базовая реализация просто выводит сообщение
        from message_log import MessageLog
        self.gamemap.engine.message_log.add_message(self.interaction_message)
        
        # Здесь можно добавить любую логику:
        # - изменение состояния объекта
        # - добавление предметов в инвентарь
        # - запуск диалога
        # - изменение карты и т.д.
    
class Portal(Usableentity):
    def __init__(
        self,
        parent: Optional[Usableentity] = None,
        x: int = 0,
        y: int = 0,
        target_floor: int = 1,
    ):
        super().__init__(
            parent=parent,
            x=x,
            y=y,
            char="0",
            color=(0, 0, 255),  # Синий цвет
            name="Portal to the second floor",
            interaction_message="You step through the blue portal!",
            blocks_movement=False,
            
        )
        self.target_floor = target_floor

    @property
    def activated_or_not(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.entity)

    def interact(self, player: Actor) -> None:
        """Переопределяем метод для реализации перехода между уровнями"""
        super().interact(player)  # Выводим базовое сообщение
        
        # Здесь должна быть логика перехода на другой этаж
        # Например:
        if hasattr(self.gamemap.engine, 'game_world'):
            self.gamemap.engine.game_world.current_floor = self.target_floor
            self.gamemap.engine.game_world.generate_floor()
            # Размещаем игрока на новом уровне
            # (нужно адаптировать под вашу систему генерации уровней)

    pass