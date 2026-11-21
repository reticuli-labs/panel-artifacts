def Q (n : Nat) : Prop := n = 1

theorem nq : ¬ Q 5 := by unfold Q; decide

theorem target : Q 5 = False := by simp [nq]
