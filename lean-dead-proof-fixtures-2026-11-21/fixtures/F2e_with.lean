-- Fixture 2e: the same as 2d inside proofs. Two theorems match on the same shape; the second is the target.
theorem deadT (x : Option Nat) : x = x :=
  match x with
  | some _ => rfl
  | none => rfl

theorem target (x : Option Nat) : x.isSome = x.isSome :=
  match x with
  | some _ => rfl
  | none => rfl
