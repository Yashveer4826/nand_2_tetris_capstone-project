import os
import sys

PREDEFINED_SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
}

COMP_TABLE = {
    # a = 0
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    # a = 1
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

JUMP_TABLE = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


def clean_line(raw_line: str) -> str:
    """Strip inline/full-line comments and surrounding whitespace."""
    no_comment = raw_line.split("//", 1)[0]
    return no_comment.strip()


def first_pass(lines: list[str], symbol_table: dict[str, int]) -> list[str]:
    """Remove comments/blank lines, record (LABEL) addresses, and return instruction lines."""
    instructions: list[str] = []
    rom_address = 0

    for raw_line in lines:
        cleaned = clean_line(raw_line)
        if not cleaned:
            continue
        if cleaned.startswith("(") and cleaned.endswith(")"):
            label = cleaned[1:-1].strip()
            if label not in symbol_table:
                symbol_table[label] = rom_address
        else:
            instructions.append(cleaned)
            rom_address += 1

    return instructions


def encode_c_instruction(instr: str) -> str:
    """Encode a C-instruction [dest=]comp[;jump] into 16-bit binary."""
    if "=" in instr:
        dest_part, rest = instr.split("=", 1)
    else:
        dest_part, rest = "", instr

    if ";" in rest:
        comp_part, jump_part = rest.split(";", 1)
    else:
        comp_part, jump_part = rest, ""

    dest_str = dest_part.strip()
    comp_str = comp_part.strip()
    jump_str = jump_part.strip()

    if comp_str not in COMP_TABLE:
        raise ValueError(f"Unsupported comp mnemonic: '{comp_str}' in instruction '{instr}'")
    if jump_str not in JUMP_TABLE:
        raise ValueError(f"Unsupported jump mnemonic: '{jump_str}' in instruction '{instr}'")

    d1 = "1" if "A" in dest_str else "0"
    d2 = "1" if "D" in dest_str else "0"
    d3 = "1" if "M" in dest_str else "0"

    return f"111{COMP_TABLE[comp_str]}{d1}{d2}{d3}{JUMP_TABLE[jump_str]}"


def second_pass(instructions: list[str], symbol_table: dict[str, int]) -> list[str]:
    """Convert instructions to 16-bit binary and allocate variables starting at RAM 16."""
    binary_lines: list[str] = []
    next_var_addr = 16

    for instr in instructions:
        if instr.startswith("@"):
            operand = instr[1:].strip()
            if operand.isdigit():
                addr = int(operand)
            else:
                if operand not in symbol_table:
                    symbol_table[operand] = next_var_addr
                    next_var_addr += 1
                addr = symbol_table[operand]
            binary_lines.append(f"{addr:016b}")
        else:
            binary_lines.append(encode_c_instruction(instr))

    return binary_lines


def write_symbols_file(symbol_table: dict[str, int], output_path: str) -> None:
    """Write all symbols (labels, variables, predefined) and addresses to symbols.txt."""
    out_dir = os.path.dirname(os.path.abspath(output_path))
    symbols_path = os.path.join(out_dir, "symbols.txt")

    with open(symbols_path, "w", encoding="utf-8") as f:
        for sym, addr in symbol_table.items():
            f.write(f"{sym}: {addr}\n")


def assemble(asm_path: str, hack_path: str | None = None) -> str:
    if hack_path is None:
        base, _ = os.path.splitext(asm_path)
        hack_path = base + ".hack"

    with open(asm_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    symbol_table = dict(PREDEFINED_SYMBOLS)
    instructions = first_pass(lines, symbol_table)
    binary_lines = second_pass(instructions, symbol_table)

    with open(hack_path, "w", encoding="utf-8") as f:
        for b_line in binary_lines:
            f.write(b_line + "\n")

    # K mod 3 == 0 feature: save all labels and variables with addresses in symbols.txt
    write_symbols_file(symbol_table, hack_path)
    return hack_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <input.asm> [output.hack]")
        sys.exit(1)

    asm_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) >= 3 else None
    result_path = assemble(asm_file, out_file)
    print(f"Assembled '{asm_file}' -> '{result_path}' (symbols.txt generated)")


if __name__ == "__main__":
    main()
