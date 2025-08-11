# Clang Parser

## Usage

```bash
python cli.py your_file.c \
  --language c \
  --std c99 \
  --target arm-none-eabi \
  -D __arm__ \
  -D __ARM_ARCH_7M__ \
  --detailed-pp-record \
  --ast-include-pp \
  --print-ast \
  --libclang "U:\Users\Enlink\Documents\clang+llvm-20.1.0-x86_64-pc-windows-msvc\bin\libclang.dll"
```