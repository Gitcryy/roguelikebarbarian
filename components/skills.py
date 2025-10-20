from __future__ import annotations
from enum import auto, Enum
from typing import TYPE_CHECKING, Optional
from components.base_component import BaseComponent
from equipment_types import EquipmentType
import actions
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor

class SkillType(Enum):
    DAMAGE = auto()
    BUFF = auto()
    HEAL = auto()
    DEBUFF = auto()
    CREATION = auto()
    


class SkillBase(BaseComponent):
    def __init__(self, 
            id: int=0, 
            name: str= None,
            desc: str = None, 
            type:SkillType = None, 
            resource:str= None, 
            cost: int=0
            ): 
            self.name = name,
            self.id = id,
            self.desc = desc,
            self.type = type,
            self.resource = resource,
            self.cost = cost,

    def can_use(self, entity):
        # Проверка требований (уровень, атрибуты, наличие ресурса)
        # ...
        return True # или False

    def use(self, user, target):
        if self.can_use(user):
            for effect in self.effects:
                effect.apply(user, target)  # Применяем каждый эффект скилла
            # Уменьшаем ресурс пользователя
            user.resource -= self.cost
            return True
        else:
            return False
        
class Effect:
    def apply(self, user, target):
        pass  # Базовый класс, дочерние классы переопределяют этот метод

class DamageEffect(Effect):
    def __init__(self, damage_type, amount):
        self.damage_type = damage_type
        self.amount = amount

    def apply(self, user, target):
        target.take_damage(self.amount, self.damage_type)

    
    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()
