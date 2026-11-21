-- Fixture 2d: a match is compiled into an auxiliary definition. Two definitions match on the same shape.
--DEAD
def deadM (x : Option Nat) : Nat :=
  match x with
  | some n => n
  | none => 0
--/DEAD

def liveM (x : Option Nat) : Nat :=
  match x with
  | some n => n + 1
  | none => 7

theorem target : liveM none = 7 := rfl
