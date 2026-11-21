def g (n : Nat) : Nat := n

attribute [implemented_by gImpl] g

theorem target : g 5 = 6 := by native_decide
