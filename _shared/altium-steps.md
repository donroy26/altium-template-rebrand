# Altium steps - the template swap, evidence and fallback

The facts behind the swap. The script path comes first; the click-by-click procedure is the fallback that stage 02 copies into each run sheet. Items marked unconfirmed have not been tried; settle them on the pilot project and record the answer here.

## Scripting the swap

The script is [RebrandTemplates.pas](../_tools/altium/RebrandTemplates.pas). It has never been run on a real Altium install. Claude Code on your machine is where it gets fixed.

Confirmed by Altium docs:
- Process `Sch:ChangeCurrentTemplate`. Documented parameters: `TemplateSource=Project|General|Configuration` and `Action=ChooseTemplatesFolder`. With no parameters it is "Choose Another Template File". `Sch:UpdateCurrentTemplate` and `Sch:RemoveTemplate` take none.
- `ISch_Document`: `TemplateFileName` (read/write), `ShowTemplateGraphics`, `TitleBlockOn`, `UpdateDocumentProperties`. `ISch_Template` has `FileName`. Object id `eTemplate`. `RemoveSchObject`.
- Plumbing: `ResetParameters; AddStringParameter('ObjectKind','Project'); AddStringParameter('FileName', path); RunProcess('WorkspaceManager:OpenObject')`, and `ObjectKind=All` with `WorkspaceManager:CloseObject`. Also `Client.OpenDocument('SCH', path)`, `Client.ShowDocument(doc)`, `serverDoc.DoFileSave(...)`, `SchServer.GetSchDocumentByPath(path)`.

Unconfirmed, from one third-party claim ("measured on AD 25.8.1", never shown running): `AddStringParameter('TemplateSource','Local'); AddStringParameter('FileName', TplFile); AddStringParameter('Silent','True'); RunProcess('Sch:ChangeCurrentTemplate')` applies a template file with no dialog. This is method 1 in the script. `Local` is not among the documented `TemplateSource` values.

What method 1 leaves unknown: which parameter action and which scope the silent path uses. Stage 04 catches a wrong outcome either way.

What the script's syntax rests on: constructs seen in third-party scripts (Salitronic eda-agent `Generic.pas`, Apache-2.0, patterns only; the Altium CI article; `IterateSchSheets.pas`; Altium-Designer-addons `SheetParameters.pas`). Not seen in any of them: `Const` declarations, `TStringList.LoadFromFile` and `SaveToFile`, `TStringList.Strings[i]` and `Count`, `While` loops, `Length`, `ISch_Document.TemplateFileName` as a read (the sources read it with `GetState_TemplateFileName`), writing `TitleBlockOn`, `SetModified(False)`.

Saving: `serverDoc.SetModified(True); serverDoc.DoFileSave('')` appears in eda-agent on a sheet made with `Client.OpenNewDocument('SCH', ...)`, with success judged by the file existing. No `DoFileSave` example on an existing SchDoc was found in the three Altium-Designer-addons files that were read, or in the CI article.

What the probe found on your version: FILL (Altium version, which method worked, the read-back values). Copy them from `stages/03_swap/output/swap-log.txt` after the pilot.

If method 1 fails and per-sheet dialogs are too slow, the next step is a script that builds the template object through the Schematic API. Not built.

## Manual procedure (fallback if the script cannot be used)

Confirmed from Altium docs:
- Menu: Design > Sheet Templates. Commands: Local > Load From File (`*.SchDot`), Local > Manage Templates, Set Template from server (Workspace-managed templates), Update Current Template, Remove Current Template.
- The Properties panel can also set it: Document Options, Page Options > Formatting and Size > Template.
- The Update Template dialog offers a scope: "Just this document", "All schematic documents in the current project", "All open schematic documents".
- It also offers a parameter action: "Do not update any parameters", "Add new parameters that exist in the template only", "Replace all matching parameters".

Steps:
1. Commit or copy the project first. Work on the copy.
2. Single-size project: open any sheet, load the template, scope "All schematic documents in the current project".
3. Mixed-size project: one pass per size. Open only that size's sheets, load that size's template, scope "All open schematic documents", close them, repeat.
4. Parameter action: "Add new parameters that exist in the template only". Do not use "Replace all matching parameters", because it overwrites sheet values with the template's.
5. File > Save All.

## Old projects

- Saving an old project in a current Altium version may rewrite the files in the newer format. Unconfirmed. Work on copies or in version control, so the change can be seen and undone.
- A released or archived project's documents change when re-templated. You decide per project whether that needs a new revision.
- A sheet with no template record has its old title block either built in or drawn straight on the sheet. A new template lands on top of it. The script switches the built-in one off; a drawn one has to be deleted by hand.

## Unconfirmed: settle on the pilot project and record the answer here

- Whether a whole-project pass on mixed sizes forces one template onto every size.
- What happens when the sheet size and the template size differ.
- Whether existing title-block text survives in every case.
- Whether Update Current Template does nothing when the referenced file is missing.
