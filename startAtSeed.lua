f = assert(io.open("seedData.txt", "r"))
seed1, seed2, pc, offset = f:read("*number", "*number", "*number", "*number")
f.close()

function startAtSeed(address, value)
  -- Check if in level select and start was just pressed.
  -- If so, set the desired seed values and the like
  if emu.read(0x00C0, emu.memType.cpuDebug) == 3 and emu.read(0x00B5, emu.memType.cpuDebug) & 16 > 0 then
    emu.write(0x0017, seed1, emu.memType.cpuDebug)
    emu.write(0x0018, seed2, emu.memType.cpuDebug)
    emu.write(0x001A, pc, emu.memType.cpuDebug)
    emu.write(0x00B1, offset, emu.memType.cpuDebug)
  end
end

emu.addMemoryCallback(startAtSeed, emu.memCallbackType.cpuExec, 0x84AE)
