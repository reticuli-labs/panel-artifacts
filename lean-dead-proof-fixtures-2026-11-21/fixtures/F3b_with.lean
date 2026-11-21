-- Fixture 3b: implemented_by, given in a command of its own. gImpl is NOT the same function as g, and nothing asks for a proof
-- that it is. The target is false in the logic (g 5 is 5) and is closed by native_decide all the same.
def g (n : Nat) : Nat := n

def gImpl (n : Nat) : Nat := n + 1
attribute [implemented_by gImpl] g

theorem target : g 5 = 6 := by native_decide
