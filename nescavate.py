from states import State, StateChain
from tqdm import tqdm
from copy import copy


'''
TODO
 - Finish the part that figures out the first two pieces.
 - Once the number of seeds becomes small, start asking if the user wants to finish, from which true first seed is computed.
-------------------
 - Assume an offset of 0 initially, then create new states for each offset around the first line clear. Should save lots of time/space
 - Determine all prng values that are reasonably reached from the menu.
 - Sort starting seed possibilities by "niceness," which factors in reasonable prng starts and first piece frame count.
 - Let user read lots of initial data from a csv.
 - Make user input nicer
 - Add undo button/allow backtracking
 - Implement score/lines tracking, ask for pushdown values to estimate frame counts.
 - Alternatively, see if it's possible to narrow stuff down without using those.
 - Smarter algorithm using more space?
 - Turn the thing into a GUI, where everything is much much more intuitive.
 - Make it work with OCR?
'''
def getNumber(message):
    while True:
        try:
            n = input(message)
            n = int(n)
            break
        except ValueError:
            print("Invalid input")

def pieceToNum(piece):
    return 'tjzosli'.index(piece)

def fetchData(pieceNum):
    global pieceList, rowList, clearList
    pieceString = 'tjzosli'
    currentPiece = pieceString.index(input(f'Enter piece number {pieceNum}: ').lower())
    row = int(input('Enter final row (1-20): '))
    clear = int(input('Enter number of line clears (0-4): '))
    pieceList.append(currentPiece)
    rowList.append(row)
    clearList.append(clear)

def rowToFrames(row, gravity):
    return gravity * row + (2 * ((22 - row) // 4) + 10)

def rowToFramesLineClear(row, gravity, offset):
    # Compute framerule time
    rowcheck = 2 * ((22 - row) // 4) + 4
    framerule = (-1 * (offset + 1 + gravity * row + rowcheck)) % 4
    return 1 + gravity * row + (1 + rowcheck + framerule + 21)

gravityTable = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]

if __name__ == "__main__":
    N = 32767
    seed = 0x8898
    testSeed = [84*256+130, 2, 1] # For testing purposes atm
    chainList = []
    level = int(input('Enter starting level (0-19): '))
    gravity = gravityTable[level]
    pieceList = []
    rowList = []
    clearList = []

    fetchData(1)
    fetchData(2)

    print("Initializing possible seeds...")
    with tqdm(total=N*8*4,leave=True) as pbar:
        for i in range(N):
            for j in range(8):
                    for k in range(4):
                        thirdState = State(seed, j, k, pieceList[-1])
                        if seed == testSeed[0] and j == testSeed[1] and k == testSeed[2]:
                            testState = thirdState
                        newChain = StateChain(thirdState)
                        newChain.addFrames(rowList[-1], clearList[-1], gravity, debug=False)
                        chainList.append(newChain)

            pbar.update(8*4)
            seed = State.prng(seed, 1)

    #Start inserting pieces and deriving info
    pieceNum = 3
    while len(chainList) > 0:
        print(f'{len(chainList)} possible third piece seeds.')
        if len(chainList) < 10:
            for chain in chainList:
                print(f'{chain.thirdState}, {chain.tailState}')
        fetchData(pieceNum) # Can probably make this all shared
        newChainList = []

        # Now that we have all the information about the nth piece landing
        # Advance the (n-1)th state by the frame count for the (n-2)th, check if it generates the desired piece.
        with tqdm(total=len(chainList),leave=False) as pbar:
            for chain in chainList:
        #Calculate number of frames in between
                # print(chain.tailState)
                newPiece, _ = chain.tailState.getPiece()
                #print(str(newPiece) + " " + str(pieceList[-1]))
                if newPiece == pieceList[-1]:

                    chain.updateTail()
                    chain.addFrames(rowList[-1], clearList[-1], gravity, debug=False)
                    newChainList.append(chain)
                    # Update framedata for chain
                elif chain.thirdState == testState:
                    print("TEST STATE ELIMINATED")
                pbar.update(1)
        chainList = newChainList
        answer = input('Finish search now (0-1)? ')
        if answer:
            break
        pieceNum += 1
    # Final stretch
