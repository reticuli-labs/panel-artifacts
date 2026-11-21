-- Fixture 3a: a true csimp lemma. slow and fast are the same function written twice. The target is closed by native_decide.
-- The trace option prints the code the compiler made for the target, so that one can read which of the two it calls.
def slow (n : Nat) : Nat := n + 0
def fast (n : Nat) : Nat := n

--DEAD
@[csimp] theorem slow_eq_fast : @slow = @fast := rfl
--/DEAD

set_option trace.compiler.ir.result true in
theorem target : slow 5 = 5 := by native_decide
