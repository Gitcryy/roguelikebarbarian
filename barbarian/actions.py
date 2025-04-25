from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING
import color
import exceptions
import tile_types
from components.fighter import Fighter
from components.Dices import dices
from components import equipment
if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) in self.engine.game_map.downstairs_locations:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):

    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        if self.entity.equipment and self.entity.equipment.weapon and self.entity.equipment.weapon.equippable:
            power_bonus = self.entity.equipment.weapon.equippable.get_power_bonus() # Получаем случайный бонус из оружия
        else:
            power_bonus = 0 #Если нет оружия, нет бонуса
        damage = self.entity.fighter.power + power_bonus
        pen = self.entity.fighter.pen
        dice = dices.roll(1,20)   

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if dice == 20:
            self.engine.message_log.add_message(
                f"{attack_desc} for crit {(damage*2)} hit points.[{dice}]", attack_color
            )
            target.fighter.hp -= (damage*2)
        elif dice + pen >= target.fighter.defense:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.[{dice} + {pen}]", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.[{dice} + {pen}]", attack_color
            )

    
class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        
        if self.entity is self.engine.player:
            # Increment move counter
            self.engine.move_counter += 1
            if self.engine.move_counter % 15 == 0:
                self.entity.fighter.heal(1)
            # Check and update existing portals
            portals_to_remove = []
            if hasattr(self.engine, "portal_locations"):
                for portal in self.engine.portal_locations:
                    portal["lifetime"] -= 1
                    if portal["lifetime"] <= 0:
                        portals_to_remove.append(portal)
                        x, y = portal["location"]
                        self.engine.game_map.tiles[x, y] = tile_types.floor
                        self.engine.message_log.add_message(
                            "A red portal fades away...", color.red
                        )
                
                for portal in portals_to_remove:
                    self.engine.portal_locations.remove(portal)
            else:
                self.engine.portal_locations = []
            # Try to spawn new portal every 10 moves
            if self.engine.move_counter >= 1000:
                player_x, player_y = self.engine.player.x, self.engine.player.y
                # Try to spawn portal 2 tiles to the right
                portal_x = player_x + 2
                portal_y = player_y
                
                # Check if the location is valid
                if (self.engine.game_map.in_bounds(portal_x, portal_y) and 
                    self.engine.game_map.tiles["walkable"][portal_x, portal_y]):
                    self.engine.game_map.tiles[portal_x, portal_y] = tile_types.portal_red
                    self.engine.portal_locations.append({
                        "location": (portal_x, portal_y),
                        "lifetime": 10  # Portal will exist for 10 moves
                    })
                    self.engine.message_log.add_message(
                    "A mysterious red portal appears nearby!", color.red
                    )
                    self.engine.move_counter = 0  # Reset counter after spawning portal
                    self.engine.message_log.add_message(
                        "A mysterious red portal appears nearby!", color.red
                    )
                    
        if self.engine.game_map.tiles[dest_x, dest_y] == tile_types.portal_blue:
            self.engine.game_world.current_floor = 1  # Set to first dungeon floor
            self.engine.game_world.generate_floor()
            
            # Get all party members before changing map
            party_members = [
                entity for entity in self.engine.game_map.actors
                if hasattr(entity, "ai") and hasattr(entity.ai, "in_party") and entity.ai.in_party
            ]
            
            # Place player and party in dungeon
            center_x = self.engine.game_map.width // 2
            center_y = self.engine.game_map.height // 2
            self.entity.place(center_x, center_y, self.engine.game_map)
            
            # Place party members around the player
            for i, member in enumerate(party_members):
                dx = [-1, 1, 0, 0][i % 4]
                dy = [0, 0, -1, 1][i % 4]
                member.place(center_x + dx, center_y + dy, self.engine.game_map)
            
            self.engine.message_log.add_message(
                "You step through the blue portal and enter the dungeon!", color.blue
            )
            return
            
        # Handle red portal (dungeon to city)
        
        if self.engine.game_map.tiles[dest_x, dest_y] == tile_types.portal_red:
                self.engine.game_world.current_floor = 0  # Return to city
                self.engine.game_world.generate_floor()
                
                # Get party members
                party_members = [
                    entity for entity in self.engine.game_map.actors
                    if hasattr(entity, "ai") and hasattr(entity.ai, "in_party") and entity.ai.in_party
                ]
                
                # Place player and party in city
                center_x = self.engine.game_map.width // 2
                center_y = self.engine.game_map.height // 2
                self.entity.place(center_x, center_y, self.engine.game_map)
                
                # Place party members
                for i, member in enumerate(party_members):
                    dx = [-1, 1, 0, 0][i % 4]
                    dy = [0, 0, -1, 1][i % 4]
                    member.place(center_x + dx, center_y + dy, self.engine.game_map)
                
                self.engine.message_log.add_message(
                    "You step through the red portal and return to the city!", color.red
                )
                return

        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")
        self.entity.move(self.dx, self.dy)



class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

class DialogueAction(ActionWithDirection):
    def perform(self) -> None:
        from components.ai import FriendlyNPC
        dest_x, dest_y = self.dest_xy
        
        # Check if target location is within one tile range
        if abs(self.entity.x - dest_x) > 1 or abs(self.entity.y - dest_y) > 1:
            raise exceptions.Impossible("That NPC is too far away to talk to.")
            
        target = self.target_actor
        if target and isinstance(target.ai, FriendlyNPC):
            target.ai.toggle_party_membership()
        else:
            raise exceptions.Impossible("You can only talk to friendly NPCs nearby.")