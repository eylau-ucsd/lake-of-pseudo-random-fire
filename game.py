from Crypto.Cipher import AES
from os import urandom
import random
import binascii

flag = "flag\{testflag\}"

class PRFGame:
    def __init__(self, mode): # mode = 1 is pseudorandom, move = 0 is random
        self.plaintext_ciphertext = {}
        self.key = urandom(16)
        self.mode = mode
    
    def encrypt(self, msg):
        msg_comp = bytes(x ^ 1 for x in msg)
        cipher = AES.new(self.key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(msg) + cipher.encrypt(msg_comp)
        return ciphertext
    
    def oracle(self, msg): # msg is a bytestring that is 16 bytes long
        if (len(msg) != 16):
            return None
        if (self.mode == 0):
            if (msg in self.plaintext_ciphertext):
                return self.plaintext_ciphertext[msg]
            random_string = urandom(32)
            self.plaintext_ciphertext[msg] = random_string
            return random_string
        else: # mode = 1 (pseudorandom oracle)
            return self.encrypt(msg)
    
    def guess(mode_guess):
        return (self.mode == mode_guess)

doors = """
          ┌---------┐                         ┌---------┐          
          |         |                         |         |          
          |         |                         |         |          
          |         |                         |         |          
          |       O |                         |       O |          
          |         |                         |         |          
          |         |                         |         |          
          └---------┘                         └---------┘          
"""
intro_dialog = """Greetings!
You are a weary traveller, searching for a long-lost treasure  - the Beacon of True Randomness. However, in your quest to obtain it, you must enter a maze of 50 rooms.
In each room there are two doors - one leads you closer to the Beacon, but the other leads to the Lake of Pseudo-Random Fire! There is no way to distinguish which door is which, except for one:
Accompanying you is a high priest named Orycull. They claim to be able to speak to both the Beacon and the Lake transmitting a hexadecimal message chosen by you. Every time they speak, both entities will respond with a strange song, also in hexadecimal, echoed through their respective doors. Orycull loses their voice quickly, so they can only do this 100 times.
While Orycull may not be able to point you directly to the correct door, a clever traveller may be able to use their gift to guide themselves safely to the treasure..."""
enter_dialog = "You enter a room. Inside the room are two doors. How do you proceed?" 
options = """1 - Choose left door
2 - Choose right door
3 - Call on Orycull the High Priest
Enter a number: """
options_fail = "Invalid option."
left_dialog = "You walk through the left door..."
right_dialog = "You walk through the right door..."
fail_dialog = "Oh no! You fell straight into the Lake of Pseudo-Random Fire. Better luck next time!"
succeed_dialog = "Phew! You didn't walk into the Lake of Pseudo-Random Fire. Onwards..."
orycull_dialog = "Enter the message you wish Orycull to communicate to the entities: "
orycull_error_dialog = "Sorry, Orycull only relays 16-byte messages, in hexadecimal format."
orycull_response_dialog = """The left door sings: {left_response}
The right door sings: {right_response}"""
orycull_run_out_dialog = "Oh no! Orycull voice broke! They can't talk anymore for the rest of the quest."
orycull_remaining_dialog = "Orycull can still speak {n:d} more times."
rooms_remaining_dialog = "There are {n:d} rooms remaining."
win_dialog = """Magnificent! You have survived the 50 rooms. Unfortunately, to your chargrin, the Beacon of True Randomness is in another castle...
Oh well. Here's a consolation prize: {flag:s}"""

def orycull(messages_left, left_game, right_game):
    while True:
        if (messages_left == 0):
            print(orycull_run_out_dialog)
            continue
        hex_message = input(orycull_dialog)
        try:
            message = binascii.unhexlify(hex_message)
        except binascii.Error:
            print(orycull_error_dialog)
            continue
        if (len(message) != 16):
            print(orycull_error_dialog)
            continue
        left_response = binascii.hexlify(left_game.oracle(message)).decode("utf-8")
        right_response = binascii.hexlify(right_game.oracle(message)).decode("utf-8")
        print(orycull_response_dialog.format(left_response=left_response, right_response=right_response))
        print(orycull_remaining_dialog.format(n=(messages_left - 1)))
        return (messages_left - 1)

def main():
    rooms = 50
    messages_left = 100
    print(intro_dialog)
    while (rooms > 0):
        correct_door = random.getrandbits(1) # 0 is left, 1 is right
        left_game = PRFGame(correct_door) # game for left door
        right_game = PRFGame(correct_door ^ 1) # game for right door
        print(doors)
        print(enter_dialog)
        decision = input(options)
        while True:
            match decision:
                case "1": # left door
                    if (correct_door == 0):
                        print(succeed_dialog)
                        rooms -= 1
                        print(rooms_remaining_dialog.format(n=rooms))
                        break
                    else:
                        print(fail_dialog)
                        return
                case "2": # right door
                    if (correct_door == 1):
                        print(succeed_dialog)
                        rooms -= 1
                        print(rooms_remaining_dialog.format(n=rooms))
                        break
                    else:
                        print(fail_dialog)
                        return
                case "3": # Orycull
                    messages_left = orycull(messages_left, left_game, right_game)
                case other:
                    print(options_fail)
    print(win_dialog.format(flag=flag))

if (__name__ == "__main__"):
    main()