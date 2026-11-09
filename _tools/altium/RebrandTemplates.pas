// RebrandTemplates.pas - swap the sheet template on many schematic sheets from a job list.
//
// READ FIRST: the authors never ran this on a real Altium install. Method 1 rests on one
// third-party claim (measured on Altium Designer 25.8.1, never shown running). Run RunProbe on a
// scratch COPY of one project before anything else. If Altium reports a script error, fix it with
// Claude Code on your machine; the evidence and the unconfirmed list are in _shared\altium-steps.md.
//
// Setup: set WorkspaceRoot below (the folder holding AGENTS.md, ending in a backslash) and Method.
//   Method 1: Sch:ChangeCurrentTemplate with TemplateSource=Local, FileName and Silent (unconfirmed claim)
//   Method 2: the same without Silent (a dialog may appear; confirm it)
//   Method 3: the process with no parameters (you pick the template file in the dialog)
// Run: File > Run Script, browse to this file, then run RunProbe (first job only, never saves)
//   or RunBatch (every job, saves a sheet only when the read-back matches).
// Reads  stages\03_swap\output\jobs.txt: project .PrjPcb path|sheet path|template path|titleblock_off
//   (absolute paths, grouped by project, project path may be empty, titleblock_off is 0 or 1).
// Writes stages\03_swap\output\swap-log.txt, saved after every sheet so a crash leaves evidence.

Const
    WorkspaceRoot = 'C:\FILL\altium-template-rebrand\';
    Method        = 1;

Var
    SwapLog : TStringList;

Procedure Say(Msg : String);
Begin
    SwapLog.Add(Msg);
    SwapLog.SaveToFile(WorkspaceRoot + 'stages\03_swap\output\swap-log.txt');
End;

// N-th (1-based) field of a |-separated line
Function Field(Line : String; N : Integer) : String;
Var
    I, P : Integer;
Begin
    Result := '';
    For I := 1 To N Do
    Begin
        P := Pos('|', Line);
        If P = 0 Then P := Length(Line) + 1;
        If I = N Then Result := Copy(Line, 1, P - 1)
        Else Line := Copy(Line, P + 1, Length(Line));
    End;
End;

Function AltiumVersion : String;
Begin
    Result := '';
    Try Result := Client.GetProductVersion; Except Result := ''; End;
    If Result = '' Then Result := '(not available)';
End;

Procedure OpenProject(Prj : String);
Begin
    ResetParameters;
    AddStringParameter('ObjectKind', 'Project');
    AddStringParameter('FileName', Prj);
    RunProcess('WorkspaceManager:OpenObject');
    ResetParameters;
End;

Procedure CloseAll;
Begin
    ResetParameters;
    AddStringParameter('ObjectKind', 'All');
    RunProcess('WorkspaceManager:CloseObject');
    ResetParameters;
End;

Function OpenSheet(Path : String) : IServerDocument;
Begin
    Result := Client.OpenDocument('SCH', Path);
    If Result <> Nil Then Client.ShowDocument(Result);
End;

Function SheetDoc(Path : String) : ISch_Document;
Begin
    Result := Nil;
    Try Result := SchServer.GetSchDocumentByPath(Path); Except End;
End;

Function TemplateNameOf(Path : String) : String;
Var
    SchDoc : ISch_Document;
Begin
    Result := '';
    SchDoc := SheetDoc(Path);
    If SchDoc <> Nil Then
        Try Result := SchDoc.TemplateFileName; Except Result := '(unreadable)'; End;
End;

Function CountTemplates(Path : String) : Integer;
Var
    SchDoc : ISch_Document;
    Iter   : ISch_Iterator;
    Obj    : ISch_GraphicalObject;
Begin
    Result := 0;
    SchDoc := SheetDoc(Path);
    If SchDoc = Nil Then Exit;
    Iter := SchDoc.SchIterator_Create;
    Try
        Iter.SetState_IterationDepth(eIterateFirstLevel);
        Iter.AddFilter_ObjectSet(MkSet(eTemplate));
        Obj := Iter.FirstSchObject;
        While Obj <> Nil Do
        Begin
            Inc(Result);
            Obj := Iter.NextSchObject;
        End;
    Finally
        SchDoc.SchIterator_Destroy(Iter);
    End;
End;

Procedure SetTitleBlockOff(Path : String);
Var
    SchDoc : ISch_Document;
Begin
    SchDoc := SheetDoc(Path);
    If SchDoc <> Nil Then
    Begin
        SchDoc.TitleBlockOn := False;
        SchDoc.UpdateDocumentProperties;
    End;
End;

// Documented parameters of Sch:ChangeCurrentTemplate are TemplateSource=Project|General|Configuration
// and Action=ChooseTemplatesFolder. TemplateSource=Local, FileName and Silent are the unconfirmed claim.
Procedure ApplyTemplate(Tpl : String; M : Integer);
Begin
    ResetParameters;
    If M < 3 Then
    Begin
        AddStringParameter('TemplateSource', 'Local');
        AddStringParameter('FileName', Tpl);
        If M = 1 Then AddStringParameter('Silent', 'True');
    End;
    RunProcess('Sch:ChangeCurrentTemplate');
    ResetParameters;
End;

// Apply with method M, read back, log it. True when the template file name matches (names only, any case).
Function TryMethod(Path, Tpl : String; M : Integer) : Boolean;
Var
    Got, Verdict : String;
Begin
    Try ApplyTemplate(Tpl, M); Except Say('  method ' + IntToStr(M) + ' raised an exception'); End;
    Got := TemplateNameOf(Path);
    Result := SameText(ExtractFileName(Got), ExtractFileName(Tpl));
    If Result Then Verdict := 'match' Else Verdict := 'no match';
    Say('  method ' + IntToStr(M) + ': TemplateFileName=' + Got + ', eTemplate objects='
        + IntToStr(CountTemplates(Path)) + ', ' + Verdict);
End;

// index of the next usable job line at or after From, or -1
Function NextJob(Jobs : TStringList; From : Integer) : Integer;
Var
    I : Integer;
    S : String;
Begin
    Result := -1;
    I := From;
    While (I < Jobs.Count) And (Result < 0) Do
    Begin
        S := Trim(Jobs.Strings[I]);
        If (S <> '') And (Copy(S, 1, 1) <> '#') Then Result := I;
        Inc(I);
    End;
End;

Procedure RunProbe;
Var
    Jobs      : TStringList;
    Line, Prj, Sheet, Tpl : String;
    M, Worked : Integer;
    ServerDoc : IServerDocument;
Begin
    SwapLog := TStringList.Create;
    Jobs := TStringList.Create;
    Try
        Jobs.LoadFromFile(WorkspaceRoot + 'stages\03_swap\output\jobs.txt');
        If NextJob(Jobs, 0) < 0 Then
        Begin
            Say('PROBE no jobs in jobs.txt');
            Exit;
        End;
        Line := Trim(Jobs.Strings[NextJob(Jobs, 0)]);
        Prj := Field(Line, 1);
        Sheet := Field(Line, 2);
        Tpl := Field(Line, 3);
        Say('PROBE Altium ' + AltiumVersion + ', sheet ' + Sheet + ', template ' + Tpl);
        If Prj <> '' Then OpenProject(Prj);
        ServerDoc := OpenSheet(Sheet);
        If ServerDoc = Nil Then
        Begin
            Say('PROBE could not open the sheet');
            Exit;
        End;
        Say('  before: TemplateFileName=' + TemplateNameOf(Sheet) + ', eTemplate objects=' + IntToStr(CountTemplates(Sheet)));
        If SameText(ExtractFileName(TemplateNameOf(Sheet)), ExtractFileName(Tpl)) Then
        Begin
            Say('PROBE cannot tell: the sheet already names this template');
            ServerDoc.SetModified(False);
            CloseAll;
            Exit;
        End;
        Worked := 0;
        M := 1;
        While (M <= 3) And (Worked = 0) Do
        Begin
            If M = 3 Then Say('  method 3 needs you: pick the template file in the dialog');
            If TryMethod(Sheet, Tpl, M) Then Worked := M;
            Inc(M);
        End;
        If Worked > 0 Then Say('PROBE method ' + IntToStr(Worked) + ' worked. Set Method = ' + IntToStr(Worked))
        Else Say('PROBE no method worked');
        ServerDoc.SetModified(False);    // the probe never saves
        CloseAll;
    Finally
        Jobs.Free;
        SwapLog.Free;
    End;
End;

Procedure RunBatch;
Var
    Jobs      : TStringList;
    Line, Prj, LastPrj, Sheet, Tpl, Got : String;
    I, Nok, Nfail : Integer;
    Started, Stop, First, Ok : Boolean;
    ServerDoc : IServerDocument;
    SchDoc    : ISch_Document;
Begin
    SwapLog := TStringList.Create;
    Jobs := TStringList.Create;
    Nok := 0;
    Nfail := 0;
    Started := False;
    Stop := False;
    First := True;
    LastPrj := '';
    Try
        Jobs.LoadFromFile(WorkspaceRoot + 'stages\03_swap\output\jobs.txt');
        Say('BATCH Altium ' + AltiumVersion + ', Method ' + IntToStr(Method));
        I := NextJob(Jobs, 0);
        While (I >= 0) And (Not Stop) Do
        Begin
            Line := Trim(Jobs.Strings[I]);
            Prj := Field(Line, 1);
            Sheet := Field(Line, 2);
            Tpl := Field(Line, 3);
            If (Not Started) Or (Prj <> LastPrj) Then
            Begin
                If Started Then CloseAll;
                If Prj <> '' Then OpenProject(Prj);
                LastPrj := Prj;
                Started := True;
            End;
            Ok := False;
            Got := '';
            Try
                ServerDoc := OpenSheet(Sheet);
                If ServerDoc = Nil Then Got := '(could not open)'
                Else
                Begin
                    If Field(Line, 4) = '1' Then SetTitleBlockOff(Sheet);
                    ApplyTemplate(Tpl, Method);
                    Got := TemplateNameOf(Sheet);
                    Ok := SameText(ExtractFileName(Got), ExtractFileName(Tpl));
                    SchDoc := SheetDoc(Sheet);
                    If (Field(Line, 4) = '1') And (SchDoc <> Nil) Then
                        If SchDoc.TitleBlockOn Then Say('NOTE|' + Sheet + '|TitleBlockOn is still on');
                    If Ok Then
                    Begin
                        // DoFileSave('') on a schematic: seen once, in the third-party eda-agent Generic.pas
                        // (Apache-2.0), on a sheet made by Client.OpenNewDocument('SCH', ...). No example
                        // on an existing SchDoc was found in the Altium-Designer-addons files that were read.
                        // Stage 04_verify reads the files on disk, so a silent save failure shows up there.
                        ServerDoc.SetModified(True);
                        ServerDoc.DoFileSave('');
                    End
                    Else ServerDoc.SetModified(False);    // discard, so closing does not ask to save
                End;
            Except
                Got := '(exception)';
                Ok := False;
            End;
            If Ok Then
            Begin
                Inc(Nok);
                Say('OK|' + Sheet + '|' + ExtractFileName(Got));
            End
            Else
            Begin
                Inc(Nfail);
                Say('FAIL|' + Sheet + '|' + ExtractFileName(Tpl) + '|' + ExtractFileName(Got));
                If First Then Stop := True;
            End;
            First := False;
            I := NextJob(Jobs, I + 1);
        End;
        If Started Then CloseAll;
        If Stop Then Say('STOP the first sheet of the batch failed');
        Say('DONE ' + IntToStr(Nok) + ' ok, ' + IntToStr(Nfail) + ' failed');
    Finally
        Jobs.Free;
        SwapLog.Free;
    End;
End;
