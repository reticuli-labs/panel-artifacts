-- Fixture 2e: the same as 2d inside proofs. Two theorems match on the same shape; the second is the target.
--DEAD
theorem deadT (x : Option Nat) : x = x :=
  match x with
  | some _ => rfl
  | none => rfl
--/DEAD

theorem target (x : Option Nat) : x.isSome = x.isSome :=
  match x with
  | some _ => rfl
  | none => rfl
