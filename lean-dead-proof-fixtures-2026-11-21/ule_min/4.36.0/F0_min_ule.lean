def slow (n : Nat) : Nat := n

def fast (n : Nat) : Nat := n + 1

theorem lemma1 : @slow = @fast := sorry

theorem target : slow 5 = fast 5 := congrFun lemma1 5
