; Non-commercial use only
; Inno Setup 7.0.1 - x64 installer

#define MyAppName "Aura Qa"
#define MyAppVersion "(Debugging) 0.1 - BUILD 202711131542"
#define MyAppExeName "Aura Qa.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".qalg"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{F539A767-C6EB-4719-9341-E59BB5E21ECB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

SetupArchitecture=x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

ChangesAssociations=yes
DisableProgramGroupPage=yes

OutputDir=C:\Users\ADMIN\Desktop\fiixxing\inno\stable
OutputBaseFilename=Aura_Qa_v(Debuggin)0.1_internal_dist002b_007c
SetupIconFile=C:\Users\ADMIN\Desktop\fiixxing\src launcher\icon.ico

SolidCompression=yes
WizardStyle=classic dynamic

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application
Source: "C:\Users\ADMIN\Desktop\fiixxing\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; MinGW runtime libraries
Source: "C:\Users\ADMIN\Desktop\fiixxing\libstdc++-6.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\libgcc_s_seh-1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\libwinpthread-1.dll"; DestDir: "{app}"; Flags: ignoreversion

; Application directories
Source: "C:\Users\ADMIN\Desktop\fiixxing\Customlib\*"; DestDir: "{app}\Customlib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\ADMIN\Desktop\fiixxing\Java\*"; DestDir: "{app}\Java"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\ADMIN\Desktop\fiixxing\Tools\*"; DestDir: "{app}\Tools"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\ADMIN\Desktop\fiixxing\UI\*"; DestDir: "{app}\UI"; Flags: ignoreversion recursesubdirs createallsubdirs

; Additional application files
Source: "C:\Users\ADMIN\Desktop\fiixxing\GUI"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\plk.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\Python.rar"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\Rar.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\run_pipeline.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\ADMIN\Desktop\fiixxing\setup.bat"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Code]

type
  { Windows x64 MSG layout: 48 bytes. }
  TAppMessage = record
    hwnd: Int64;
    message: LongWord;
    Padding1: LongWord;
    wParam: Int64;
    lParam: Int64;
    time: LongWord;
    ptX: LongInt;
    ptY: LongInt;
    lPrivate: LongWord;
  end;

function AppPeekMessage(
  var Msg: TAppMessage;
  WindowHandle: Int64;
  FilterMin: LongWord;
  FilterMax: LongWord;
  RemoveMessage: LongWord): Integer;
  external 'PeekMessageW@user32.dll stdcall';

function AppTranslateMessage(var Msg: TAppMessage): Integer;
  external 'TranslateMessage@user32.dll stdcall';

function AppDispatchMessage(var Msg: TAppMessage): Int64;
  external 'DispatchMessageW@user32.dll stdcall';

function AppGetTickCount64: Int64;
  external 'GetTickCount64@kernel32.dll stdcall';

const
  APP_PM_REMOVE = 1;
  APP_PBM_SETMARQUEE = $040A;
  APP_WM_SETREDRAW = $000B;

var
  LogMemo: TNewMemo;
  LinesShown: Integer;
  LogPath: String;
  SetupRunning: Boolean;
  SetupSucceeded: Boolean;

procedure InitializeWizard;
begin
  SetupRunning := False;
  SetupSucceeded := False;
  LinesShown := 0;

  LogMemo := TNewMemo.Create(WizardForm);
  LogMemo.Parent := WizardForm.InstallingPage;
  LogMemo.Left := WizardForm.ProgressGauge.Left;
  LogMemo.Top :=
    WizardForm.ProgressGauge.Top +
    WizardForm.ProgressGauge.Height + ScaleY(12);
  LogMemo.Width := WizardForm.ProgressGauge.Width;
  LogMemo.Height :=
    WizardForm.InstallingPage.ClientHeight -
    LogMemo.Top - ScaleY(4);

  LogMemo.ReadOnly := True;
  LogMemo.ScrollBars := ssVertical;
  LogMemo.WordWrap := False;
  LogMemo.Font.Name := 'Consolas';
  LogMemo.Font.Size := 8;
  LogMemo.Color := clBlack;
  LogMemo.Font.Color := clWhite;
  LogMemo.Visible := False;
end;

procedure PumpWindowMessages;
var
  Msg: TAppMessage;
begin
  while AppPeekMessage(Msg, 0, 0, 0, APP_PM_REMOVE) <> 0 do
  begin
    AppTranslateMessage(Msg);
    AppDispatchMessage(Msg);
  end;
end;

procedure StartBusyProgress;
begin
  WizardForm.ProgressGauge.Style := npbstMarquee;

  SendMessage(
    WizardForm.ProgressGauge.Handle,
    APP_PBM_SETMARQUEE,
    1,
    15
  );

  WizardForm.ProgressGauge.Update;
end;

procedure StopBusyProgress;
begin
  SendMessage(
    WizardForm.ProgressGauge.Handle,
    APP_PBM_SETMARQUEE,
    0,
    0
  );

  WizardForm.ProgressGauge.Style := npbstNormal;

  if SetupSucceeded then
    WizardForm.ProgressGauge.Position :=
      WizardForm.ProgressGauge.Max
  else
    WizardForm.ProgressGauge.Position :=
      WizardForm.ProgressGauge.Min;

  WizardForm.ProgressGauge.Update;
end;

procedure AppendStatus(const S: String);
begin
  LogMemo.Lines.Add(S);
  SendMessage(LogMemo.Handle, $0115, 7, 0);
  LogMemo.Update;
  Log(S);
end;

procedure RefreshLog(Final: Boolean);
var
  Lines: TArrayOfString;
  Total, I: Integer;
begin
  if not FileExists(LogPath) then
    Exit;

  if not LoadStringsFromLockedFile(LogPath, Lines) then
    Exit;

  Total := GetArrayLength(Lines);

  if (not Final) and (Total > 0) then
    Total := Total - 1;

  if Total <= LinesShown then
    Exit;

  SendMessage(LogMemo.Handle, APP_WM_SETREDRAW, 0, 0);
  try
    for I := LinesShown to Total - 1 do
    begin
      LogMemo.Lines.Add(Lines[I]);

      if ((I - LinesShown + 1) mod 50) = 0 then
        PumpWindowMessages;
    end;

    LinesShown := Total;
  finally
    SendMessage(LogMemo.Handle, APP_WM_SETREDRAW, 1, 0);
  end;

  SendMessage(LogMemo.Handle, $0115, 7, 0);
  LogMemo.Invalidate;
  LogMemo.Update;
end;

procedure CancelButtonClick(
  CurPageID: Integer;
  var Cancel, Confirm: Boolean);
begin
  if SetupRunning then
  begin
    Cancel := False;
    Confirm := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchPath, WrapperPath, DonePath, WrapperText: String;
  ExitLines: TArrayOfString;
  ResultCode, ExitCode: Integer;
  PreviousCancelEnabled: Boolean;
  Msg: TAppMessage;
  LastLogRefresh, CurrentTick: Int64;
  ResultReady: Boolean;
begin
  if CurStep <> ssPostInstall then
    Exit;

  SetupSucceeded := False;

  if SizeOf(Msg) <> 48 then
  begin
    MsgBox(
      'Invalid Windows message structure. An x64 installer is required.',
      mbCriticalError, MB_OK);
    Exit;
  end;

  BatchPath := ExpandConstant('{app}\setup.bat');
  LogPath := ExpandConstant('{app}\setup.log');
  WrapperPath := ExpandConstant('{tmp}\aura_setup_runner.cmd');
  DonePath := ExpandConstant('{tmp}\aura_setup_result.txt');

  if not FileExists(BatchPath) then
  begin
    MsgBox(
      'setup.bat was not found in the installation folder.',
      mbCriticalError, MB_OK);
    Exit;
  end;

  if FileExists(LogPath) then
  begin
    if not DeleteFile(LogPath) then
    begin
      MsgBox(
        'Unable to replace setup.log. Close any program using this file.',
        mbCriticalError, MB_OK);
      Exit;
    end;
  end;

  if FileExists(DonePath) then
  begin
    if not DeleteFile(DonePath) then
    begin
      MsgBox(
        'Unable to clear the temporary configuration result.',
        mbCriticalError, MB_OK);
      Exit;
    end;
  end;

  WrapperText :=
    '@echo off' + #13#10 +
    'setlocal EnableExtensions DisableDelayedExpansion' + #13#10 +
    'cd /d "' + ExpandConstant('{app}') + '"' + #13#10 +
    'echo Configuration runner started. > "' + LogPath + '"' + #13#10 +
    'call "' + BatchPath + '" /installer < nul >> "' +
      LogPath + '" 2>&1' + #13#10 +
    'set "AURA_SETUP_EXIT=%errorlevel%"' + #13#10 +
    '> "' + DonePath + '" echo %AURA_SETUP_EXIT%' + #13#10 +
    'exit /b %AURA_SETUP_EXIT%' + #13#10;

  if not SaveStringToFile(WrapperPath, WrapperText, False) then
  begin
    MsgBox(
      'Unable to create the temporary configuration runner.',
      mbCriticalError, MB_OK);
    Exit;
  end;

  LinesShown := 0;
  LogMemo.Lines.Clear;
  LogMemo.Visible := True;
  AppendStatus('Starting setup.bat /installer...');

  WizardForm.StatusLabel.Caption :=
    'Configuring Python and downloading models. Please wait...';
  WizardForm.Update;

  PreviousCancelEnabled := WizardForm.CancelButton.Enabled;
  SetupRunning := True;
  WizardForm.CancelButton.Enabled := False;
  StartBusyProgress;

  try
    if not Exec(
      ExpandConstant('{cmd}'),
      '/D /S /C ""' + WrapperPath + '""',
      ExpandConstant('{app}'),
      SW_HIDE,
      ewNoWait,
      ResultCode
    ) then
    begin
      AppendStatus(
        'ERROR: Unable to start configuration. ' +
        SysErrorMessage(ResultCode));

      MsgBox(
        'Unable to start configuration.' + #13#10 +
        SysErrorMessage(ResultCode),
        mbCriticalError, MB_OK);
      Exit;
    end;

    ExitCode := 0;
    ResultReady := False;
    LastLogRefresh := AppGetTickCount64 - 200;

    repeat
      PumpWindowMessages;

      CurrentTick := AppGetTickCount64;

      if CurrentTick - LastLogRefresh >= 200 then
      begin
        LastLogRefresh := CurrentTick;
        RefreshLog(False);

        if FileExists(DonePath) then
        begin
          if LoadStringsFromLockedFile(DonePath, ExitLines) then
          begin
            if GetArrayLength(ExitLines) > 0 then
            begin
              if Trim(ExitLines[0]) <> '' then
              begin
                ExitCode := StrToIntDef(Trim(ExitLines[0]), 1);
                ResultReady := True;
              end;
            end;
          end;
        end;
      end;

      if not ResultReady then
        Sleep(10);
    until ResultReady;

    RefreshLog(True);

    if ExitCode <> 0 then
    begin
      AppendStatus(
        'ERROR: setup.bat failed with exit code ' +
        IntToStr(ExitCode) + '.');

      MsgBox(
        'setup.bat failed with exit code ' +
        IntToStr(ExitCode) + '.' + #13#10 +
        'Check setup.log in the installation folder.',
        mbCriticalError, MB_OK);
      Exit;
    end;

    SetupSucceeded := True;

    WizardForm.StatusLabel.Caption :=
      'Environment configuration completed.';

    AppendStatus('Environment configuration completed successfully.');

  finally
    StopBusyProgress;
    SetupRunning := False;
    WizardForm.CancelButton.Enabled := PreviousCancelEnabled;
  end;
end;

function CanLaunchApplication: Boolean;
begin
  Result := SetupSucceeded;
end;

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; Check: CanLaunchApplication

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Python"
Type: filesandordirs; Name: "{app}\models"
Type: files; Name: "{app}\setup.log"