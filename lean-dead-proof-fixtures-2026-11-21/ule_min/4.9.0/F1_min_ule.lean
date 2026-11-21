def f : Nat → Nat
  | 0 => 1
  | n + 1 => f n + 2

theorem target : f 1 = 3 := by rw [f, f]
