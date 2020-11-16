import sys
from copy import copy
orientationID = [2, 7, 8, 10, 11, 14, 18, 0]
pieces = ['t', 'j', 'z', 'o', 's', 'l', 'i']
pieceString = 'tjzosli'

class State:
    def __init__(self, seed, pc, offset, pieceBefore):
        self.seed = seed
        self.pc = pc
        self.offset = offset
        self.pieceBefore = pieceBefore

    def __str__(self):
        return f'[{self.seed // 256} {self.seed % 256}] {self.pc} {self.offset} {pieces[self.pieceBefore]}'

    @staticmethod
    def prng(value, rep):
        for i in range(rep):
            bit1 = (value >> 1) & 1
            bit9 = (value >> 9) & 1
            leftmostBit = bit1 ^ bit9
            value = (leftmostBit << 15) | (value >> 1)
            #print(str(value // 256) + " " + str(value % 256))

        return value

    def getPiece(self): # Have this also return the number of advance calls needed, so 1 or 2. Assumes there is no need to update the prng right before
        result = self.seed >> 8
        result += self.pc + 1
        result %= 8
        if result != 7 and result != self.pieceBefore:
            return result, 0
        newSeed = State.prng(self.seed, 1)
        result = newSeed >> 8
        result %= 8
        if self.pieceBefore < 7:
            result += orientationID[self.pieceBefore]
        result %= 7
        return result, 1

    def incPc(self):
        self.pc = (self.pc + 1) % 8

    def setPieceBefore(self, piece):
        self.pieceBefore = piece

    def advance(self, frames, extra): # last param is number of extra calls in the same frame
        newSeed = State.prng(self.seed, frames + extra)
        newOff = (self.offset + frames) % 4
        #SOMETHING WITH OFFSET LATER THIS IS ANNOYING
        return State(newSeed, self.pc, newOff, self.pieceBefore)

'''
How to refactor expensive method:
 - Reduce to two states: a starting state (which will be the third one overall) and a tail
 - Only other array needed is one that has frames between consecutive pieces (it will include extraneous data at the start for ease of computation)
 - Some stuff might be needed from the state before the tail idk, but this should be taken care of by the frame array.
 - Piece list, row list, and clear list should all be global, no need for a copy within each one
'''
class StateChain:
    def __init__(self, startState):
        self.thirdState = startState # Might actually be third piece???
        self.tailState = copy(startState)
        self.frames = [-1] # Includes first entry as a dummy, which is figured out later

    def __eq__(self):
        pass

    def getTail(self, back):
        return self.tailState

    @staticmethod
    def rowToFrames(row, gravity):
        return gravity * row + (2 * ((22 - row) // 4) + 10)
    @staticmethod
    def rowToFramesLineClear(row, gravity, offset):
        # Compute framerule time
        rowcheck = 2 * ((22 - row) // 4) + 4
        framerule = (-1 * (offset + 1 + gravity * row + rowcheck)) % 4
        return 1 + gravity * row + (1 + rowcheck + framerule + 21)

    def addFrames(self, row, clear, gravity,debug=False):
        if clear == 0:
            if debug:
                print(f'{StateChain.rowToFrames(row, gravity)} frames')
            self.frames.append(StateChain.rowToFrames(row, gravity))
        else:
            if debug:
                print(f'{StateChain.rowToFramesLineClear(row, gravity, self.tailState.offset)} frames')
            self.frames.append(StateChain.rowToFramesLineClear(row, gravity, self.tailState.offset))


    def updateTail(self):
        piece, reroll = self.tailState.getPiece()
        self.tailState.setPieceBefore(piece)
        self.tailState.incPc()
        # print(self.frames)
        # print(self.frames[-2])
        self.tailState = self.tailState.advance(self.frames[-1], reroll)
        # print(self.tailState)
        return self.tailState.getPiece()[0]


    def validate(self):
    #Assume this is well designed and that only the most recent piece needs to be checked or something.
        if len(self.pieces) < 3:
            return True
        return True

'''
RESEARCH FOR SMALL DETAILS

 - We define the starting seed as the combination of prng, cleared pieces, and global timer (mod 4) at the beginning of the frame where the Start button is registered
 - From here, it takes 4 frames to generate the next two pieces, which are basically called consecutively.
 - The seed of each piece is the combination of all those things at the beginning of the frame where the piece is initialized (exception is piece 2, which is weird)
 - In general, the number of frames it took for piece i - 1 added to piece i - 1's ARE (which happens after its lock) is the number of prng calls between the determination of piece i and piece i + 1;
'''


if __name__ == "__main__":
    # Init all possible starting states

    #This sucessfully generates the first 6 pieces, so everything except for line clears is accounted for.
    testState = State(242*256+77, 0, 0, 7)


    testState = testState.advance(4, 0)
    piece, reroll = testState.getPiece()
    offset = 0
    print(f'Seed: [{testState.seed // 256} {testState.seed % 256}] {testState.pc} {testState.offset}')
    print(f'{pieces[piece].upper()} {str(testState.offset)} after 4 frames')

    def action(frames):
        global testState, piece, reroll, offset
        testState.setPieceBefore(piece)
        testState.incPc()
        testState = testState.advance(frames, reroll)
        print(f'Seed: [{testState.seed // 256} {testState.seed % 256}] {testState.pc} {testState.offset}')
        piece, reroll = testState.getPiece()
        offset = testState.offset
        print(f'{pieces[piece].upper()} {str(testState.offset)} after {frames} frames')

    reroll += 1
    action(0)
    action(1 + 10 + (96 + (20 - 1) * 6))

    # def rowToFrames(row, gravity):
    #     return gravity * row + (2 * ((22 - row) // 4) + 10)
    # def rowToFramesLineClear(row, gravity, offset):
    #     # Compute framerule time
    #     rowcheck = 2 * ((22 - row) // 4) + 4
    #     framerule = (-1 * (offset + 1 + gravity * row + rowcheck)) % 4
    #     return 1 + gravity * row + (1 + rowcheck + framerule + 21)
    rowsAndClears = [(20,0),
                    (18,0),
                    (18,0),
                    (17,0),
                    (19,0),
                    (19,0),
                    (18,0),
                    (18,0),
                    (15,0),
                    (16,0),
                    (16,0),
                    (13,0),
                    (15,0),
                    (13,0),
                    (13,0),
                    (19,4),
                    (19,0),
                    (16,0),
                    (17,0),
                    (14,0), # t
                    (12,0), # z
                    (15,0), # O
                    (14,0),
                    (14,0),
                    (15,1),
                    (13,0),
                    (17,0),
                    (15,0),
                    (12,0),
                    (13,0),
                    (14,1),
                    (12,0),
                    (11,0),
                    (12,0),
                    (11,0),
                    (9,0),
                    (9,0),
                    (19,4),
                    (17,0),
                    (15,0),
                    (12,0),
                    (11,0),
                    (9,0),
                    (13,0),
                    (19,4),
                    (17,0),
                    (15,0),
                    (18,1),
                    (15,0),
                    (13,0),
                    (15,0),
                    (13,0)
                    ]
    for row, clear in rowsAndClears:
        print(f"Dropped {row} rows and cleared {clear} lines")
        if clear == 0:
            action(StateChain.rowToFrames(row, 6))
        else:
            action(StateChain.rowToFramesLineClear(row, 6, offset))
    # action(rowToFrames(20, 6))
    # action(rowToFrames(18, 6))
    # action(rowToFrames(18, 6))
    # action(rowToFrames(17, 6))
    # action(rowToFrames(19, 6))
    # action(rowToFrames(19, 6))
    # action(rowToFrames(18, 6))
    # action(rowToFrames(18, 6))
    # action(rowToFrames(15, 6))
    # action(rowToFrames(16, 6))
    # action(rowToFrames(16, 6))
    # action(19 * 6 + 25 + 2) Previous offset of 2
    # action(rowToFrames(19, 6))
    # action(rowToFrames(16, 6))
    # action(6 * 15 + 30) #Previous offset of 3
