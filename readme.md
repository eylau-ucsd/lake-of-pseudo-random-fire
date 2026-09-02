## Lake of Pseudo-Random Fire

| Author | Category | Difficulty |
| --- | --- | --- |
| Eugene Lau | cryptography | easy |

### Description

> Greetings! You are a weary traveller, searching for a long-lost treasure  - the Beacon of True Randomness. However, in your quest to obtain it, you must go through a series of rooms to get to the Beacon. In each room there are two doors - one leads you closer to the Beacon, but the other leads to Lake of Pseudo-Random Fire - your demise!
> 
> Accompanying you in your journey is a high priest named Orycull. They are your only way to tell which door is which. When Orycull utters an incantation of your choosing, the doors emit different signals. The door leading you closer to the Beacon will emit a fully random signal, while the door leading you to the Lake will emit a pseudorandom signal.
> 
> A clever traveller may be able to distinguish the random and pseudorandom signals and safely get to the treasure. However, be careful as Orycull can only utter so many incantations...

### original specification

A text-based RPG game, where the goal is to clear the 50 rooms and get to the treasure, where they will be presented with the flag. In each room there are 2 doors, one leading closer to the Beacon and one leading to the Lake of Pseudo-Random Fire (i.e. instant death). To win, they must correctly choose the right door 50 times in a row. The correct door will be the door which emits a fully random response to utterances made by Orycull, while the wrong door will be the door which emits a pseudorandom response to utterances made by Orycull. The player can choose the message Orycull utters to the doors, in the form of a 32-character hexstring representing 16 bytes. Orycull can utter a total of 100 incantations for the whole duration of the game.

For those who have taken a theoretical cryptography class, you may notice that this game is very similar to the PRF game. This is intentional - it is why the game is called "The Lake of **P**seudo-**R**andom **F**ire". 

We will concretely define what the random and pseudorandom response is. Note that these definitions are made available to CTF participants as the source code to the game is made available for them to see (the only thing redacted is the flag itself).

The random response randomly generates a 64-character hexstring from /dev/urandom and returns it. The random response is also *consistent*: within one room, if Orycull sends two identical messages to the random door, the random door will respond with the same hexstring, by keeping a record of the messages sent by Orycull. This record is reset from room to room, so this consistency is only within individual rooms.

The pseudorandom response takes Orycull's uttered incantation, performs the following computation on it, and returns the result as a 64-character hexstring:

`f(x) = AESEncrypt(K, x) || AESDecrypt(K, !x)`

Where `x` refers to the 16-byte bytestring that corresponds to the 32-character hexstring uttered by Orycull, `||` refers to bytestring concatenation, `AESEncrypt(K, x)` and `AESDecrypt(K, x)` are the respective AES encryption and decryption algorithms for a key `K` and message `x`, and `!x` refers to the bitwise complement of `x` (i.e. if you flipped each bit in `x` once). A new value for key `K` is generated for every new room the player enters, and does not change until the player advances to a new room. The player does not have access to this key `K`.

To beat this game, the player cannot rely on pure luck and blindly guess 50 coin flips correctly in a row - that is mathematically infeasible. Rather, they must design an algorithm that can distinguish between the pseudorandom response and the random response to queries. In theoretical cryptography, this is called an *adversary*.

With some inspiration, the player may realize that they can "cancel" out the AESEncrypt with the AESDecrypt in the pseudorandom response, through a series of two messages. Something like this: 

1. First query: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, Pseudorandom Response: 45aa67c25466bf0f15152b08612313a407fe7ba3dd9ac0265ca2896f62efe499
2. Second query: ba55983dab9940f0eaead4f79edcec5b (bitwise complement of first half of first response), Pseudorandom Response: 49a18b1c4b5a08272c41910a82bf8575aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

As you observe, the second half of the second message's response matches the first message we sent to the pseudorandom door. Why is this? Let's use a bit of algebra to explain this. Let `x` be the initial message we send in the first query. When we send `x` to the pseudorandom door, the response will be `AESEncrypt(K, x) || AESDecrypt(K, !x)`. The first half of that is `AESEncrypt(K, x)`. If we bitwise complement that, we get `!AESEncrypt(K, x)` which is the second message we send to the door.

After sending the second message, the door will respond with `AESEncrypt(K, !AESEncrypt(K, x)) || AESDecrypt(K, !(!AESEncrypt(K, x)))`. The second half of that is `AESDecrypt(K, !(!AESEncrypt(K, x)))`. Since two bitwise complements cancel each other out, we can simplify further and get `AESDecrypt(K, AESEncrypt(K, x))`. Since the encryption and decryption algorithms cancel each other out when they share the same key, we can simplify further, and find the second half of the second response to be equal to just `x`. That's why we get our first message back with this scheme.

With this observation, we can already come up with an *adversary* that can distinguish the random and pseudorandom door:

1. Send the message `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` (hexstring) to the doors.
2. Take the bitwise complement of the first half of the left door's response, and send that as a message to the doors.
3. Take the second half of the left door's response. If it is equal to `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, the message we sent initially, there is a very high likelihood that the left door is the pseudorandom door - it is very improbable that the actual RNG generated that specific string - so choose the right door, since it is very likely to be the random door. If not, then we are certain the left door is the random door, so we will choose the left door in that case.
 
The player can implement this algorithm and automate the solving of this challenge using a script. `exploit.py` in the root directory of this repository is an example of such a script. After going through the 50 rooms, they will be rewarded with the flag, ending the challenge.

### Challenge Files

[lake-prf.zip](dist)

[Solution](solution)