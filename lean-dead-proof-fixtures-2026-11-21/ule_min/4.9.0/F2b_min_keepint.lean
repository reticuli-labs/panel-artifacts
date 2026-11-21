def Q (n : Nat) : Prop := n = 1

@[simp] theorem nq : ¬ Q 5 := by unfold Q; decide

theorem target : Q 5 = False := by simp
