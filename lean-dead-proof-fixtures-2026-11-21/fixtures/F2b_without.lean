-- Fixture 2b: the same with the simp attribute given where the theorem is stated.
def P (n : Nat) : Prop := n = 0
def Q (n : Nat) : Prop := n = 1
@[simp] theorem nq : ¬ Q 5 := by unfold Q; decide


theorem target : Q 5 = False := by simp
