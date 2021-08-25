import time
from random import randrange
import pyautogui
import keyboard
import asyncio

from enum import Enum, auto

from matching import Matcher
from Item import Item
from Commands import Commands
from Cords import Cords
from vision import Vision

from mob import blaze

class Keyboard:
    '''
    The keyboard class handles all valid user input used in this bot.
    '''

    def __init__(self, stop_key: str ="9", resume_key: str ="9"):
        self.stop_key = stop_key
        self.resume_key = resume_key
        self.is_active = True
        self.start_keyboard_listener()

    def start_keyboard_listener(self) -> None:
        '''
        Start all the keyboard listeners and handles the same stop/resume key
        scenario.

        The current listeners are:
        stop_key: stops the execution of the program.
        resume_key: resumes ...

        '''
        if self.stop_key != self.resume_key:
            keyboard.on_press_key(self.stop_key, self._deactivate)
            keyboard.on_press_key(self.resume_key, self._activate)

        else:
            keyboard.on_press_key(self.stop_key, self._switch)

    def send_command(self, command: Commands) -> None:
        '''
        Writes a command in Minecraft.
        '''
        keyboard.send("t")
        time.sleep(0.1)
        keyboard.write(command.value)
        keyboard.send("enter")

    def send_key(self, key: str) -> None:
        keyboard.send("esc")

    ###########
    # State changing logic

    def _switch(self, _) -> None:
        if self.is_active:
            self._deactivate(_)
        else:
            self._activate(_)

    def _activate(self, _) -> None:
        self.is_active = True
        print("Activate")

    def _deactivate(self, _) -> None:
        self.is_active = False
        print("Deactivate")

    # End of state changing logic
    ############

class Mouse:
    def __init__(self) -> None:
        pass

    def click(self, x, y, button: str="left") -> None:
        '''
        Clicks once at the given coordinates.
        '''
        pyautogui.moveTo(x, y)
        time.sleep(0.1)
        pyautogui.click(button=button)

class MinecraftBot:
    class State(Enum):
        HITTING = auto(),
        SELLING = auto(),
        WAITING = auto(),
        HUNTING = auto(),


    def __init__(self, keyboard: Keyboard, mouse: Mouse, matcher: Matcher, eyes: Vision):
        self.state = self.State.HITTING
        self.keyboard = keyboard
        self.mouse = mouse
        self.matcher = matcher
        self.eyes = eyes

        self.blaze_stacks = 0

        self.mob_cords = {
            "x": 800,
            "y": 800
        }
        self.last_hit = 0

    def state_machine(self):
        if self.state == self.State.HITTING:
            self.handle_hitting()

        elif self.state == self.State.HUNTING:
            self.handle_hunting()

        elif self.state == self.State.SELLING:
            self.handle_selling()

    def change_state(self, target: State) -> None:
        if self.state == self.State.HUNTING:
            if target == self.State.WAITING: # Didn't find the mob. What should it do?
                if self.check_for_item(Item.BLAZEROD): # CHANGE IT HERE!
                    target = self.state.SELLING # Sell it in the meantime.
                else:
                    print("No mobs... Nothing to sell... Trying again later.")
                    exit("1337")

        print(f"Old: {self.state} -> new: {target}")
        self.state = target

    def check_for_item(self, item: Item) -> int:
        '''
        Returns the quantity of a given item
        '''
        pass

    def handle_hitting(self):
        time_elapsed = time.time() - self.last_hit
        if time_elapsed > 0.4 + randrange(22) / 10.0:
            self.mouse.click(self.mob_cords["x"], self.mob_cords["y"])
            self.last_hit = time.time()

            self.change_state(self.state.HUNTING)

    def handle_hunting(self):
        self.mob_cords = self.eyes.get_mob_position(lower_bound, upper_bound, sct)
        print(self.mob_cords)
        if self.mob_cords == None:
            self.change_state(self.State.WAITING)
        else:
            #isInventoryFull?
            self.change_state(self.State.HITTING)

    def handle_selling(self):
        '''
        Sells all the blaze rods in the inventory.
        '''

        self.keyboard.send_command(Commands.SHOP)
        time.sleep(0.5)

        cord = self.matcher.detect_item(Item.ANVIL)[0]
        self.mouse.click(cord.x, cord.y)
        time.sleep(0.5)

        cord = self.matcher.detect_item(Item.BLAZEROD)[0]
        self.mouse.click(cord.x, cord.y, "right")
        time.sleep(0.5)

        cord = self.matcher.detect_item(Item.FIRECHARGE_PACK)[0]
        self.mouse.click(cord.x, cord.y)
        time.sleep(0.5)

        # Tries to sell the whole inventory (lazy solution)
        cord = self.matcher.detect_item(Item.ACCEPT)[0]
        for i in range(4):
            self.mouse.click(cord.x, cord.y)
            time.sleep(0.1)

        self.keyboard.send_key("esc")

    def loop(self):
        while True:
            if self.keyboard.is_active:
                self.state_machine()



async def main():
    k = Keyboard()
    m = Mouse()
    matcher = Matcher()
    vision = Vision()
    bot = MinecraftBot(k, m, matcher, vision)

    #listener_routine = asyncio.ensure_future(m.start_keyboard_listener())

    await asyncio.sleep(3)
    bot.handle_selling()

    await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
