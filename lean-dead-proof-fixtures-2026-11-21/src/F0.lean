-- Fixture 0, a control for the reader itself: here the target DOES use a lemma closed by sorry, in its proof term. The reader
-- must list lemma1 among what the target reaches, and sorryAx among the target's axioms. If it does not, its silence elsewhere
-- means nothing. The dead part is a theorem nothing uses.
def slow (n : Nat) : Nat := n
def fast (n : Nat) : Nat := n + 1

--DEAD
theorem unused : True := trivial
--/DEAD

theorem lemma1 : @slow = @fast := sorry

theorem target : slow 5 = fast 5 := congrFun lemma1 5
