# GarMyFriend-LyraZeroW scope

Current stage: Linux simulator and physical Lyra Zero W bring-up. The owner has
connected the board selected in `.gar/device.json` by USB and completed the documented wiring.
`hardware/WIRING.md` and `hardware/connections.csv` own the 40-pin-header wiring.
`hardware/gpio.csv` and `hardware/spi.csv` are the single canonical physical binding.
Generate simulation I/O in `.gar/hardware/simulation/` from `hardware/simulation-overrides.csv`.
Do not add a second hand-maintained copy of the GPIO/SPI binding.
Only report display appearance and physical input as verified when supported by
device logs and the owner's observations. Use `tools/device.py` for the physical
target; keep its ARMv7 build separate from the simulator's native build.
For simulator work, use only Product VM `gar-myfriend-lyra-zero-w-sim`, SSH port 2232 and local
panel port 8774, configured in `config/simulator.json`. Never operate the
original Orange Pi VM `gar-myfriend-sim`. This VM runs x86_64 Linux and checks
GPIO/SPI interfaces; it does not emulate the RK3506 CPU or electrical timing.

The user's current WebPanel scope is exactly two physical substitutes: the
GC9A01 face display and a rotary encoder. Preserve the shared parts' appearance
and basic input. Do not add dashboards, sensor controls, servos, scenarios,
record/replay, direct expression selectors or execution controls to this scope.

Application behavior belongs in the `gar-my-friend` submodule at
`sources/gar-my-friend/application/`. Keep Product launch configuration in
`scripts/run-face.cjs`; it must not choose expressions. The face application reads
GPIO and writes SPI and must operate independently of the WebPanel process.
`simulation/` and `simulator/` relay physical input and driver-produced pixels;
they must not choose expressions, animate faces or generate application output.

Pin `sources/gar-my-friend` and `sources/gar-tools` to exact commits.
Commit and push shared changes before updating Product pointers.
Reuse gar-tools through the submodule. Keep reusable hardware models there,
Product wiring and face behavior here. Follow the submodule's Web simulator
design guidance when changing the part composition.

Hardware data follows GAR's CSV headers: `hardware/components.csv` owns part
numbers, `connections.csv` owns the physical wiring plan, and `gpio.csv` /
`spi.csv` own the selected runtime I/O assignment. Do not create parallel part
or pin-plan JSON files. Keep physical header numbers distinct from Linux line
offsets. Application and virtual driver startup must read I/O values from CSV.

## Board composition

The current user-selected architecture pins application, gar-tools and a separate board repository.
Read `product.json` and `docs/COMPOSITION.md`. Board/OS/resource/toolchain facts belong to
`sources/board-lyra-zero-w/`; Product wiring and runtime choices stay here.
Keep Product hooks thin; generic build/deployment/startup mechanisms belong in gar-tools.
Never commit `.gar/device.json` or SDK/ROM/compiler bytes. Do not operate a board to test an offline refactor.
