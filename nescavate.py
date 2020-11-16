from states import State, StateChain
from tqdm import tqdm

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
    currentPiece = pieceToNum(input(f'Enter piece number {pieceNum}: ').lower())
    row = int(input('Enter final row (1-20): '))
    clear = int(input('Enter number of line clears (0-4): '))
    pieceList.append(currentPiece)
    rowList.append(row)
    clearList.append(clear)

gravityTable = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]

if __name__ == "__main__":
    N = 32767
    seed = 0x8898
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
                        newChain = StateChain(State(seed, j, k, pieceList[-1]))
                        newChain.addFrames(rowList[-1], clearList[-1], gravity)
                        chainList.append(newChain)

            pbar.update(8*4)
            seed = State.prng(seed, 1)

    pieceNum = 3
    while len(chainList) > 1:
        print(f'{len(chainList)} possible third piece seeds.')
        if len(chainList) < 10:
            for chain in chainList:
                print(f'{chain.thirdState}, {chain.tailState}')
        fetchData(pieceNum)
        newChainList = []

        # Now that we have all the information about the nth piece landing
        # Advance the (n-1)th state by the frame count for the (n-2)th, check if it generates the desired piece.
        with tqdm(total=len(chainList),leave=False) as pbar:
            for chain in chainList:
                newPiece, _ = chain.tailState.getPiece()
                if newPiece == pieceList[-1]:
                    chain.updateTail()
                    chain.addFrames(rowList[-1], clearList[-1], gravity)
                    newChainList.append(chain)
                pbar.update(1)
        chainList = newChainList
        answer = input('Finish search now (0-1)? ')
        if answer == 1:
            break
        pieceNum += 1
    '''
    Game plan:
    The max hang time for the first piece is 1 + 96 + (row - 1) * gravity + ARE. For each chain in the chainList,
    we take the thirdPiece's seed, backtrack it by that much + 3 (one for each reroll and the call in between).
    Then starting from there and ending at like 30 frame separation (the min possible on level 29)
    we generate the first two states, verify that they give the correct pieces, and measure how far away they are from the thirdState.
    For now, sort by largest frame space first. For the best case, create a pretty printout of the first few pieces.
    '''

    '''
    Print format sample:

    Piece 1: T that falls to row 20 and clears 0 lines. 221 frames between piece 2 and piece 3.
    Piece 2: J that falls to row 20 and clears 0 lines. 130 frames between piece 3 and piece 4.
    So on so forth.
    '''
