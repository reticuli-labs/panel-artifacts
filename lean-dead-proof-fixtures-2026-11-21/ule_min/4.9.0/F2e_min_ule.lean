theorem target (x : Option Nat) : x.isSome = x.isSome :=
  match x with
  | some _ => rfl
  | none => rfl
