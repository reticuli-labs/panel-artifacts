def slow (n : Nat) : Nat := n + 0

set_option trace.compiler.ir.result true in

theorem target : slow 5 = 5 := by native_decide
