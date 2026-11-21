def Q (n : Nat) : Prop := n = 1

theorem target : Q 5 = False := by simp [nq]
