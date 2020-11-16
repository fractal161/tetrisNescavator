# tetrisNescavator
Utility for determining the starting seed of a NES Tetris game.

# Installation
Fork the repository and run ``pip3 install -r requirements.txt``.

# Usage
Upon running ``python3 nescavate.py``, you will be prompted to enter the starting level. From here, for each piece you will need to enter its type as a letter, the row its center rests on (the center starts at row 1 and can go as low as row 20), and the number of lines the piece cleared. After the third piece has been entered, you will be notified of the number of possible seeds remaining. Due to how the line clear framerule works, it is not guaranteed that only one seed is valid. Eventually, you will be asked if you want to finish the determination. Upon accepting, all possibilities for the location of the first two pieces will be calculated and the most likely possibility will be stored in ``seedData.txt``.

Seeds are displayed in the form ``[prngByte1 prngByte2] pieceCount frameCount``, where ``pieceCount`` is taken modulo 8 and ``frameCount`` is taken modulo 4. The ``startAtSeed.lua`` script can be loaded into the Mesen NES emulator, which will force every game to start at the determined seed.

# Implementation
Messy notes of mine. May cleanup later.

 - We define the starting seed as the combination of prng, cleared pieces, and global timer (mod 4) at the beginning of the frame where the Start button is registered
 - From here, it takes 4 frames to generate the next two pieces, which are called consecutively with one prng scramble.
 - The seed of each piece is the combination of all those things at the beginning of the frame where the piece is initialized (exception is piece 2: see previous note)
 - For non line clears, the number of frames it took for piece i - 1 added to piece i - 1's entry delay (which happens after its lock) is the number of prng calls between the determination of piece i and piece i + 1

# TODO
## Important
- Finish the part that figures out the first two pieces.
- Once the number of seeds becomes small, start asking if the user wants to finish, from which true first seed is computed.
- Modify startup so that we don't need 0.6 GiB of memory.
- Implement score/lines tracking, ask for pushdown values to estimate frame counts.
- Alternatively, see if it's possible to narrow stuff down without using those.

## Cosmetic/QOL
- Assume an offset of 0 initially, then create new states for each offset around the first line clear to save time/space.
- Determine all prng values that are reasonably reached from the menu.
- Sort starting seed possibilities by "niceness," which factors in reasonable prng starts and first piece frame count.
- Let user read lots of initial data from a csv.
- Make user input nicer
- Add undo button/allow backtracking
- Smarter algorithm?
- Convert into a GUI, where everything is much much more intuitive.
- Integrate with OCR
- Profit
