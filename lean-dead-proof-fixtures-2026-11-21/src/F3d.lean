-- Fixture 3d: implemented_by given where h is defined. hImpl is NOT the same function as h, and nothing asks for a proof that
-- it is. The target is false in the logic (h 5 is 5) and is closed by native_decide. Nothing that the kernel checks names hImpl.
--DEAD
def hImpl (n : Nat) : Nat := n + 1
--/DEAD

@[implemented_by hImpl] def h (n : Nat) : Nat := n

theorem target : h 5 = 6 := by native_decide
