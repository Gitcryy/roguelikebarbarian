from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod
import color

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.aggression_config = {
            "player": 1.0,  # Полная агрессия к игроку
            "friendly_npc": 0.5,  # Половинная агрессия к NPC
            "hostile_enemy": 0.0,  # Нет агрессии к другим врагам
        }

    def set_aggression(self, target_type: str, value: float) -> None:
        """Установить уровень агрессии к определенному типу целей"""
        if value < 0.0 or value > 1.0:
            raise ValueError("Уровень агрессии должен быть между 0.0 и 1.0")
        self.aggression_config[target_type] = value

    def get_target_aggression(self, target: Actor) -> float:
        """Получить уровень агрессии к конкретной цели"""
        if target is self.engine.player:
            return self.aggression_config["player"]
        elif isinstance(target.ai, FriendlyNPC):
            return self.aggression_config["friendly_npc"]
        elif isinstance(target.ai, HostileEnemy):
            return self.aggression_config["hostile_enemy"]
        elif isinstance(target.ai, HostileRanged):
            return self.aggression_config["hostile_enemy"]
        return 0.0
    
    def perform(self) -> None:
        # Поиск ближайшей цели с учетом агрессии
        closest_target = None
        closest_distance = float('inf')
        
        # Проверяем всех акторов
        for actor in self.engine.game_map.actors:
            if actor is self.entity:
                continue
                
            aggression = self.get_target_aggression(actor)
            if aggression <= 0:
                continue
                
            distance = self.entity.distance(actor.x, actor.y)
            # Учитываем агрессию при расчете эффективного расстояния
            effective_distance = distance / aggression
            
            if effective_distance < closest_distance:
                closest_target = actor
                closest_distance = effective_distance
        if not closest_target:
            return WaitAction(self.entity).perform()
        dx = closest_target.x - self.entity.x
        dy = closest_target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(closest_target.x, closest_target.y)
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        return WaitAction(self.entity).perform()

class HostileRanged(HostileEnemy):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.target_entity = None
        self.max_range = 6  # Максимальная дальность атаки
        self.min_range = 3
        self.cooldown = 0  # Текущее время перезарядки       
        self.last_known_position: Optional[Tuple[int, int]] = None
    
    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an enitiy blocks movement and is not the AI itself.
            if entity.blocks_movement and entity != self.entity:
                # Modify the cost of all passable neighbor cells to convey blockage.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute a path to the destination.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # If the path is empty, then there was no path to the target.
        if not path:
            return []

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

    def perform(self) -> None:
        """Выполняет действия ИИ."""
        target = self.engine.player #Всегда цель - игрок
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance

        if self.cooldown > 0:
            self.cooldown -= 1  # Уменьшаем перезарядку
            self.engine.message_log.add_message(
                            "Goblin have to reload...", color.white
                        )
            return WaitAction(self.entity).perform()  # Ждем

        if self.engine.game_map.known[self.entity.x, self.entity.y]:
            if distance < self.min_range:
                #Пытаемся отойти от цели
                new_x = self.entity.x - dx  # Двигаемся в противоположном направлении от игрока
                new_y = self.entity.y - dy
                if self.engine.game_map.tiles["walkable"][new_x, new_y] and not self.engine.game_map.get_blocking_entity_at_location(new_x, new_y):
                    #Если клетка проходима и не заблокирована, двигаемся туда
                    return MovementAction(self.entity, -dx, -dy).perform()
                else:
                    #Если отойти некуда, ждем
                    return WaitAction(self.entity).perform()
            if distance <= self.max_range:
                self.cooldown = 2
                # Атакуем, если цель в пределах досягаемости
                return MeleeAction(self.entity, dx, dy).perform()
            elif distance > self.max_range:
                # Двигаемся ближе к цели
                self.path = self.get_path_to(target.x, target.y)
                if self.path: #Проверяем, что путь не пустой
                    dest_x, dest_y = self.path.pop(0)
                    return MovementAction(
                        self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                    ).perform()
        else: #Если не знаем ничего - ждём
            return WaitAction(self.entity).perform()

class Player(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

class FriendlyNPC(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.in_party = False
        self.current_target = None

    def toggle_party_membership(self) -> None:
        """Переключает статус членства NPC в группе"""
        self.in_party = not self.in_party
        if self.in_party:
            self.engine.message_log.add_message(
                f"{self.entity.name} joined in the group."
            )
        else:
            self.engine.message_log.add_message(
                f"{self.entity.name} leaved your group."
            )

    def perform(self) -> None:
        if not self.in_party:
            # Если NPC не в группе, просто стоит на месте
            return WaitAction(self.entity).perform()
        # Поиск ближайшего врага
        closest_enemy = None
        closest_distance = float('inf')
        
        for actor in self.engine.game_map.actors:
            if actor.ai and isinstance(actor.ai, HostileEnemy):
                distance = self.entity.distance(actor.x, actor.y)
                if distance < closest_distance:
                    closest_enemy = actor
                    closest_distance = distance
                    
        # Если есть враг поблизости
        if closest_enemy and closest_distance <= 8:  # Радиус обнаружения
            self.current_target = closest_enemy
            
            if closest_distance <= 1:  # Если враг рядом - атакуем
                dx = closest_enemy.x - self.entity.x
                dy = closest_enemy.y - self.entity.y
                return MeleeAction(self.entity, dx, dy).perform()
            else:  # Иначе двигаемся к врагу
                self.path = self.get_path_to(closest_enemy.x, closest_enemy.y)
                if self.path:
                    dest_x, dest_y = self.path.pop(0)
                    return MovementAction(
                        self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                    ).perform()
                    
        # Если нет врагов - следуем за игроком
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        if distance > 3:  # Держим дистанцию в 3 клетки
            self.path = self.get_path_to(target.x, target.y)
            if self.path:
                dest_x, dest_y = self.path.pop(0)
                return MovementAction(
                    self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                ).perform()
        return WaitAction(self.entity).perform()


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()

class FearedAi(BaseAI):
    pass