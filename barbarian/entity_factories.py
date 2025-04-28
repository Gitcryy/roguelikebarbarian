from components.ai import HostileEnemy, FriendlyNPC, Player, HostileRanged
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item


player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=Player,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=10, base_power=2, base_pen = 0),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=5),
)
npc = Actor(
    char="@",
    color=(173, 255, 47),
    name="NPC",
    ai_cls=FriendlyNPC,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=14, base_power=2, base_pen = 0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=350),
)

"tier 9"
gob = Actor(
    char="g",
    color=(112,255,93),
    name="Goblin",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=6, base_power=2, base_pen = 1),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1),
)
gobf=Actor(
    char="f",
    color=(84,255,88),
    name="Goblin Fighter",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=8, base_defense=6, base_power=3, base_pen = 2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1),
)
goba=Actor(
    char="a",
    color=(84,255,88),
    name="Goblin Archer",
    ai_cls=HostileRanged,
    equipment=Equipment(),
    fighter=Fighter(hp=4, base_defense=6, base_power=3, base_pen = 2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1),
)
skel=Actor(
    char="f",
    color=(47,50,54),
    name="Skeleton",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=4, base_defense=6, base_power=3, base_pen = 2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1),
)
"tier 8"
death=Actor(
    char="f",
    color=(192,128,129),
    name="Death Fiend",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=10, base_power=5, base_pen = 5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=2),
)

orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=13, base_power=3, base_pen = 3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=350),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=16, base_power=6, base_pen = 6),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1000),
)
boss = Actor(
    char="B",
    color=(255, 0, 0),
    name="Boss",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=18, base_power=10, base_pen = 10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1000),
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=16, radius=3, pen=16),
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=30, maximum_range=5, pen = 20),
)

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)


MONSTER_GROUP_TEMPLATES = [
    {
        "name": "Группа гоблинов",
        "members": [goba, goba, goba],
    },
    {
        "name": "Пара троллей",
        "members": [troll, troll],
    },
    {
        "name": "Гоблин и тролль",
        "members": [goba, troll],
    },
]