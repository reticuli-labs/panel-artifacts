def liveM (x : Option Nat) : Nat :=
  match x with
  | some n => n + 1
  | none => 7

theorem target : liveM none = 7 := rfl
