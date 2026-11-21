def liveD : Fin 5 := ⟨3, by decide⟩

theorem target : liveD.val = 3 := rfl
