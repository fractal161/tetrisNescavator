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

        return value

    def getPiece(self): # Returns piece and number of rerolls
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

    def advance(self, frames, extra):
        newSeed = State.prng(self.seed, frames + extra)
        newOff = (self.offset + frames) % 4
        return State(newSeed, self.pc, newOff, self.pieceBefore)

class StateChain:
    def __init__(self, startState):
        self.thirdState = startState
        self.tailState = copy(startState)
        self.frames = [-1] # Includes first entry as filler

    def __eq__(self):
        pass

    @staticmethod
    def rowToFrames(row, gravity):
        return gravity * row + (2 * ((22 - row) // 4) + 10)
    @staticmethod
    def rowToFramesLineClear(row, gravity, offset):
        # Compute framerule time
        rowcheck = 2 * ((22 - row) // 4) + 4
        framerule = (-1 * (offset + 1 + gravity * row + rowcheck)) % 4
        return 1 + gravity * row + (1 + rowcheck + framerule + 21)

    def addFrames(self, row, clear, gravity):
        if clear == 0:
            self.frames.append(StateChain.rowToFrames(row, gravity))
        else:
            self.frames.append(StateChain.rowToFramesLineClear(row, gravity, self.tailState.offset))


    def updateTail(self):
        piece, reroll = self.tailState.getPiece()
        self.tailState.setPieceBefore(piece)
        self.tailState.incPc()
        self.tailState = self.tailState.advance(self.frames[-1], reroll)


    def validate(self):
        if len(self.pieces) < 3:
            return True
        return True

if __name__ == "__main__":
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
