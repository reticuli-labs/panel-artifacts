-- Fixture 1: constants made at first use. f is defined by pattern matching; dead is the first to rewrite with it, target rewrites
-- with it as well.
def f : Nat → Nat
  | 0 => 1
  | n + 1 => f n + 2


theorem target : f 1 = 3 := by rw [f, f]
