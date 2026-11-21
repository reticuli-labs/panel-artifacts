def slow (n : Nat) : Nat := n

theorem target : slow 5 = 6 := by native_decide
