-- Fixture 2b: the same with the simp attribute given where the theorem is stated.
def P (n : Nat) : Prop := n = 0
def Q (n : Nat) : Prop := n = 1
--DEAD
@[simp] theorem np : ¬ P 5 := by unfold P; decide
--/DEAD
@[simp] theorem nq : ¬ Q 5 := by unfold Q; decide

--DEAD
theorem dead : P 5 = False := by simp
--/DEAD

theorem target : Q 5 = False := by simp
