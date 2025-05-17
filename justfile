default:
    uv run main.py

update:
    uv sync -U --compile-bytecode

update-frozen:
    uv sync -U --compile-bytecode --frozen
