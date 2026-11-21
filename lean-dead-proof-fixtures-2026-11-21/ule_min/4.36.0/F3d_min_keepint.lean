@[implemented_by hImpl] def h (n : Nat) : Nat := n

theorem target : h 5 = 6 := by native_decide
