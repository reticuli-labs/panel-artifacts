-- Fixture 2c: a proof inside a definition is taken out into an auxiliary theorem. Two definitions need the same small fact.
--DEAD
def deadD : Fin 5 := ⟨3, by decide⟩
--/DEAD

def liveD : Fin 5 := ⟨3, by decide⟩

theorem target : liveD.val = 3 := rfl
