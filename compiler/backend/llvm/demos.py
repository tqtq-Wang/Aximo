from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoModule:
    name: str
    description: str
    ir: str


_ADD_IR = """; Aximo LLVM backend feasibility spike
; Demo: add
source_filename = "aximo-spike-add"

define i32 @ax_add(i32 %lhs, i32 %rhs) {
entry:
  %sum = add i32 %lhs, %rhs
  ret i32 %sum
}
"""


_HELLO_IR = """; Aximo LLVM backend feasibility spike
; Demo: hello
source_filename = "aximo-spike-hello"

@.str = private unnamed_addr constant [6 x i8] c"hello\\00", align 1

declare i32 @puts(ptr noundef)

define i32 @main() {
entry:
  %message = getelementptr inbounds [6 x i8], ptr @.str, i64 0, i64 0
  %ignored = call i32 @puts(ptr noundef %message)
  ret i32 0
}
"""


DEMOS: dict[str, DemoModule] = {
    "add": DemoModule(
        name="add",
        description="Minimal integer addition function.",
        ir=_ADD_IR,
    ),
    "hello": DemoModule(
        name="hello",
        description="Minimal main-style hello example using puts.",
        ir=_HELLO_IR,
    ),
}


def get_demo(name: str) -> DemoModule:
    try:
        return DEMOS[name]
    except KeyError as error:
        known = ", ".join(sorted(DEMOS))
        raise ValueError(f"unknown demo {name!r}; expected one of: {known}") from error
