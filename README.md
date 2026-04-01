This project is a simple regex-based parser that converts RISC-V assembly code into a pure hexidecimal format.
Output is of the form 0xAAAABBBBBBBB, where A represents the 2-bytes used for the "address" of the instruction, and B represents the 4 bytes for the actual instruction.
Additional command-line support will eventually be added to allow for variable-length address spaces, as well as a choice to simply remove the addresses.
| Extension | Level of Support |
|:---:|:---:|
|RV32I|In Progress|
|RV32M|No|
|RV32A|No|
|RV32F|No|
|RV32D|No|
|RV32C|No|
|RV32B|No|
|RV32V|No|
