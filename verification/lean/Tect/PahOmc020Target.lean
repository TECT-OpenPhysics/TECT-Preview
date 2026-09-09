import Std

def formRoute (common liminf recovery target transfer : Bool) : Bool :=
  common && liminf && recovery && target && transfer

def pathRoute (space tight generator unique transfer : Bool) : Bool :=
  space && tight && generator && unique && transfer

def targetRoute (form path : Bool) : Bool := form || path

theorem form_route_needs_common (liminf recovery target transfer : Bool) :
    formRoute false liminf recovery target transfer = false := by
  simp [formRoute]

theorem form_route_needs_liminf (common recovery target transfer : Bool) :
    formRoute common false recovery target transfer = false := by
  simp [formRoute]

theorem form_route_needs_recovery (common liminf target transfer : Bool) :
    formRoute common liminf false target transfer = false := by
  simp [formRoute]

theorem form_route_needs_transfer (common liminf recovery target : Bool) :
    formRoute common liminf recovery target false = false := by
  simp [formRoute]

theorem path_route_needs_space (tight generator unique transfer : Bool) :
    pathRoute false tight generator unique transfer = false := by
  simp [pathRoute]

theorem path_route_needs_unique (space tight generator transfer : Bool) :
    pathRoute space tight generator false transfer = false := by
  simp [pathRoute]

theorem named_target_is_not_route :
    targetRoute false false = false := by
  simp [targetRoute]

theorem target_route_requires_one_complete (form path : Bool) :
    targetRoute form path = true -> form = true ∨ path = true := by
  intro h
  simp [targetRoute] at h
  exact h
