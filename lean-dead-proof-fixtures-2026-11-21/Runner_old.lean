/-
Runner.lean: read a Lean file command by command, the way a source-level tool would, and print
  (1) after each command: the constants of this file that are new since the command before it;
  (2) at the end, for each name given after the file: whether it exists, the constants of this file that its type
      and value reach (transitively), and its axioms.
It changes nothing and writes no file. Use:  lean --run Runner.lean <file.lean> [name ...]
With ASYNC=0 in the environment the file is elaborated with Elab.async false.
-/
import Lean
open Lean Elab

def localNames (env : Environment) : NameSet :=
  env.constants.map₂.foldl (fun acc n _ => acc.insert n) {}

def usedBy (ci : ConstantInfo) : Array Name :=
  let fromVal := match ci with
    | .defnInfo v => v.value.getUsedConstants
    | .thmInfo v => v.value.getUsedConstants
    | .opaqueInfo v => v.value.getUsedConstants
    | _ => #[]
  ci.type.getUsedConstants ++ fromVal

/-- the constants of this file that `root` reaches through types and values -/
partial def reach (env : Environment) (root : Name) : NameSet :=
  go root {}
where
  go (c : Name) (seen : NameSet) : NameSet :=
    if seen.contains c then seen else
    if (env.getModuleIdxFor? c).isSome then seen else
    match env.find? c with
    | none => seen
    | some ci => (usedBy ci).foldl (fun s d => go d s) (seen.insert c)

/-- every axiom that `root` reaches, through this file and the imported ones -/
partial def axiomsOf (env : Environment) (root : Name) : Array Name :=
  let kenv := env
  let rec go (c : Name) (st : NameSet × NameSet) : NameSet × NameSet :=
    if st.1.contains c then st else
    let st := (st.1.insert c, st.2)
    match kenv.find? c with
    | none => st
    | some ci =>
      let st := match ci with
        | .axiomInfo _ => (st.1, st.2.insert c)
        | _ => st
      let extra := match ci with
        | .inductInfo v => v.ctors.toArray
        | _ => #[]
      ((usedBy ci) ++ extra).foldl (fun s d => go d s) st
  (go root ({}, {})).2.toArray.qsort (fun a b => a.toString < b.toString)

def kindOf (ci : ConstantInfo) : String :=
  match ci with
  | .axiomInfo _ => "axiom" | .defnInfo _ => "def" | .thmInfo _ => "theorem" | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quot" | .inductInfo _ => "inductive" | .ctorInfo _ => "constructor" | .recInfo _ => "recursor"

def firstLine (s : String) : String :=
  let l := (s.splitOn "\n").head!
  if l.length > 90 then l.take 90 ++ "..." else l

unsafe def main (args : List String) : IO Unit := do
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let fname := args.head!
  let roots := args.tail!.map String.toName
  let input ← IO.FS.readFile fname
  let inputCtx := Parser.mkInputContext input fname
  let (header, parserState, messages) ← Parser.parseHeader inputCtx
  let async := (← IO.getEnv "ASYNC") != some "0"
  let opts : Options := ({} : Options).setBool `Elab.async async
  let (env, messages) ← processHeader header opts messages inputCtx
  let cmdState := Command.mkState env messages opts
  let ctx : Frontend.Context := { inputCtx }
  let mut st : Frontend.State := { commandState := cmdState, parserState := parserState, cmdPos := parserState.pos }
  let mut seen : NameSet := localNames st.commandState.env
  let mut k := 0
  let mut nmsg := 0
  IO.println s!"file {fname} | Elab.async {async} | {Lean.versionString}"
  repeat
    let (done, st') ← (Frontend.processCommand ctx).run st
    st := st'
    -- wait for everything this command started, then look
    let env := st.commandState.env
    let now := localNames env
    let fresh := now.toList.filter (fun n => !seen.contains n)
    let src := (input.extract st.cmdPos st.parserState.pos).trim
    if !done || src != "" then
      k := k + 1
      IO.println s!"[{k}] {firstLine src}"
      for n in fresh.toArray.qsort (fun a b => a.toString < b.toString) do
        let kind := match env.find? n with | some ci => kindOf ci | none => "?"
        IO.println s!"      + {n} ({kind})"
    let msgs := st.commandState.messages.toList
    for m in msgs.drop nmsg do
      IO.println (s!"      ! {← m.toString}").trimRight
    nmsg := msgs.length
    seen := now
    if done then break
  let env := st.commandState.env
  let final := localNames env
  IO.println s!"constants of this file at the end: {final.size}"
  for r in roots do
    match env.find? r with
    | none => IO.println s!"ROOT {r}: not a constant (in the kernel map: {final.contains r})"
    | some ci =>
      let rs := (reach env r).toList.filter (· != r) |>.toArray.qsort (fun a b => a.toString < b.toString)
      IO.println s!"ROOT {r} ({kindOf ci}) reaches in this file: {rs.toList}"
      IO.println s!"ROOT {r} axioms: {(axiomsOf env r).toList}"
