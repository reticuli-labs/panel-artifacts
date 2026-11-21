-- Fixture 2a: an auxiliary lemma that simp makes from a named theorem at the place of use. np and nq are negations, which simp
-- must turn into equations before it can rewrite with them.
def P (n : Nat) : Prop := n = 0
def Q (n : Nat) : Prop := n = 1
theorem np : ¬ P 5 := by unfold P; decide
theorem nq : ¬ Q 5 := by unfold Q; decide


theorem target : Q 5 = False := by simp [nq]
