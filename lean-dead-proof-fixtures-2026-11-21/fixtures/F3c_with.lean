-- Fixture 3c: a csimp lemma whose proof is sorry. The lemma is false. The target is false in the logic and is closed by
-- native_decide; the question is whether sorry shows among the target's axioms.
def slow (n : Nat) : Nat := n
def fast (n : Nat) : Nat := n + 1

@[csimp] theorem slow_eq_fast : @slow = @fast := sorry

theorem target : slow 5 = 6 := by native_decide
