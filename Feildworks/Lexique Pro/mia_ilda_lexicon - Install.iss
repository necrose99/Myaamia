
; Script for Installing Lexique Pro.
; 
; This is compiled into a setup exe using Inno Setup.
; Inno Setup is available as freeware from www.jrsoftware.org.

[Setup]
AppName=Lexique Pro - Miami
AppVerName=Lexique Pro 3.6
AppVersion=3
AppCopyright=Copyright (c) 2004-2010, SIL International
VersionInfoVersion=3.6
AppPublisher=SIL International
DefaultDirName={pf}\SIL\Lexique Pro 3.6
DefaultGroupName=Lexique Pro
OutputBaseFilename=Miami - Lexique Pro Setup
OutputDir=C:\Users\black\GitHub\Myaamia\Feildworks\
DisableProgramGroupPage=yes
DisableDirPage=yes
SolidCompression=no
Compression=lzma
WizardImageFile=C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizLexProImage.bmp
WizardSmallImageFile=C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizLexProSmallImage.bmp

; If the executable is more than 2GB, set DiskSpanning=Yes
DiskSpanning=No
SlicesPerDisk=3
DiskSliceSize=1566000000

[Languages]
; The language files can be downloaded from the Inno Setup web site (www.jrsoftware.org)
Name: en; MessagesFile: compiler:Default.isl
Name: fr; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\French.isl
Name: es; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Spanish.isl
Name: pt; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\PortugueseStd.isl
Name: de; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\German.isl
Name: id; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Indonesian.isl
Name: ar; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Arabic.isl
Name: bg; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Bulgarian.isl
Name: ru; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Russian.isl
Name: nl; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Dutch.isl
Name: zhCHT; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\ChineseTrad.isl
Name: zhCHS; MessagesFile: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\ChineseSimp.isl

[Messages]
en.BeveledLabel=English
fr.BeveledLabel=Français
es.BeveledLabel=Español
pt.BeveledLabel=Português

[CustomMessages]
en.CreateIcon=Create a desktop icon
en.CreateDesktopIcon=Create an icon
en.CreateDesktopIcon2=Create an icon:
en.LaunchLexiquePro=Launch Lexique Pro
en.ProgramFiles=Lexique Pro program files
en.DistWizProgFiles=Distribution Wizard program files
en.Lexicons=Lexicons
en.ICU=ICU International Components for Unicode
fr.CreateIcon=Créer une icône sur le Bureau
fr.CreateDesktopIcon=Créer une icône
fr.CreateDesktopIcon2=Créer une icône:
fr.LaunchLexiquePro=Lancer Lexique Pro
fr.ProgramFiles=Fichiers de programme de Lexique Pro
fr.DistWizProgFiles=Fichiers de programme de l'Assistant de Distribution
fr.Lexicons=Lexiques
fr.ICU=ICU International Components for Unicode
es.CreateIcon=Agregar un icono del escritorio
es.CreateDesktopIcon=Agregar un icono
es.CreateDesktopIcon2=Agregar un icono:
es.LaunchLexiquePro=Iniciar Lexique Pro 
es.ProgramFiles=Archivos de programa de Lexique Pro 
es.DistWizProgFiles=Archivos de programa del Asistente de Distribución 
es.Lexicons=Léxicos 
es.ICU=ICU International Components for Unicode
pt.CreateIcon=Criar um ícone no ambiente de trabalho:
pt.CreateDesktopIcon=Criar um ícone
pt.CreateDesktopIcon2=Criar um ícone:
pt.LaunchLexiquePro=Iniciar Lexique Pro
pt.ProgramFiles=Ficheiros do programa Lexique Pro
pt.DistWizProgFiles=Ficheiros do programa do Assistente de Distribuição
pt.Lexicons=Léxicos
pt.ICU=ICU International Components for Unicode
ru.CreateIcon=Create a desktop icon
ru.CreateDesktopIcon=Create an icon
ru.CreateDesktopIcon2=Create an icon:
ru.LaunchLexiquePro=Launch Lexique Pro
ru.ProgramFiles=Lexique Pro program files
ru.DistWizProgFiles=Distribution Wizard program files
ru.Lexicons=Lexicons
ru.ICU=ICU International Components for Unicode
ar.CreateIcon=Create a desktop icon
ar.CreateDesktopIcon=Create an icon
ar.CreateDesktopIcon2=Create an icon:
ar.LaunchLexiquePro=Launch Lexique Pro
ar.ProgramFiles=Lexique Pro program files
ar.DistWizProgFiles=Distribution Wizard program files
ar.Lexicons=Lexicons
ar.ICU=ICU International Components for Unicode
bg.CreateIcon=Създай икона върху работния плот
bg.CreateDesktopIcon=Създай икона
bg.CreateDesktopIcon2=Създай икона:
bg.LaunchLexiquePro=Стартирай Lexique Pro
bg.ProgramFiles=Програмните файлове на Lexique Pro
bg.DistWizProgFiles=Програмните файлове на помощника за разпространяване на речника
bg.Lexicons=Речници
bg.ICU=ICU - International Components for Unicode
id.CreateIcon=Buat ikon di desktop
id.CreateDesktopIcon=Buat ikon
id.CreateDesktopIcon2=Buat ikon:
id.LaunchLexiquePro=Buka Lexique Pro
id.ProgramFiles=Berkas program Lexique Pro
id.DistWizProgFiles=Berkas program Wizard Distribusi
id.Lexicons=Kosakata
id.ICU=.tiff
nl.CreateIcon=Create a desktop icon
nl.CreateDesktopIcon=Create an icon
nl.CreateDesktopIcon2=Create an icon:
nl.LaunchLexiquePro=Launch Lexique Pro
nl.ProgramFiles=Lexique Pro program files
nl.DistWizProgFiles=Distribution Wizard program files
nl.Lexicons=Lexicons
nl.ICU=ICU International Components for Unicode

[Tasks]
Name: desktopicon_0; Description: {cm:CreateDesktopIcon2}; GroupDescription: {cm:CreateIcon}; Components: not (Lexicons\Lexicon_0)
Name: desktopicon_1; Description: Miami; GroupDescription: {cm:CreateDesktopIcon}; Components: Lexicons\Lexicon_0

[Files]
; Lexique Pro Program Files
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\LexiquePro.exe; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion

Source: C:\Program Files (x86)\SIL\Lexique Pro\licence.txt; DestDir: {code:GetAppDir}; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Language Codes\iso-639-3.tab; DestDir: {code:GetAppDir}\Language Codes; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Language Codes\iso-639-3-macrolanguages.tab; DestDir: {code:GetAppDir}\Language Codes; Flags: ignoreversion

Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\homebanner1.jpg; DestDir: {code:GetAppDir}\Display; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\homebanner2.jpg; DestDir: {code:GetAppDir}\Display; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\Icons\mov-icon.png; DestDir: {code:GetAppDir}\Display\Icons; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\Icons\doc-icon.png; DestDir: {code:GetAppDir}\Display\Icons; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\Icons\pdf-icon.png; DestDir: {code:GetAppDir}\Display\Icons; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\Icons\sound-icon.png; DestDir: {code:GetAppDir}\Display\Icons; Flags: ignoreversion

; Help
Source: C:\Program Files (x86)\SIL\Lexique Pro\Help\LexiquePro.chm; DestDir: {code:GetAppDir}\Help; Flags: ignoreversion

; DLLs
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\TECkit_x86.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\bass.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\cc32.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\htmltortf_sautinsoft.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\multiscribe.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\bin\DelZip190.dll; DestDir: {code:GetAppDir}\bin; Flags: ignoreversion

; Info Pages
Source: C:\Program Files (x86)\SIL\Lexique Pro\info\index.htm; DestDir: {code:GetAppDir}\Info\; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\info\index-es.htm; DestDir: {code:GetAppDir}\Info\; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\info\SIL-Logo-English.png; DestDir: {code:GetAppDir}\Info\; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\info\SIL-Logo-Spanish.png; DestDir: {code:GetAppDir}\Info\; Flags: ignoreversion

; Semantic Domains - Dictionary Development Program
Source: C:\Program Files (x86)\SIL\Lexique Pro\Semantic Domains\xxdict2.db; DestDir: {code:GetAppDir}\Semantic Domains; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Semantic Domains\xxdict3.db; DestDir: {code:GetAppDir}\Semantic Domains; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Semantic Domains\xxdict4.db; DestDir: {code:GetAppDir}\Semantic Domains; Flags: ignoreversion

; Lexicon Files
Source: C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon.sfm; DestDir: {code:GetDataDir}\Miami; Flags: ignoreversion; Components: Lexicons\Lexicon_0
Source: C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon.lpConfig.tmp; DestName: mia_ilda_lexicon.lpConfig; DestDir: {code:GetDataDir}\Miami; Flags: ignoreversion; Components: Lexicons\Lexicon_0
Source: C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon - From End.idx; DestDir: {code:GetDataDir}\Miami; Flags: ignoreversion; Components: Lexicons\Lexicon_0
Source: C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon - English.idx; DestDir: {code:GetDataDir}\Miami; Flags: ignoreversion; Components: Lexicons\Lexicon_0
Source: C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon - French.idx; DestDir: {code:GetDataDir}\Miami; Flags: ignoreversion; Components: Lexicons\Lexicon_0

; About Language Pages

; Home Page
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\homebanner1.jpg; DestDir: {code:GetDataDir}\Miami\Display\; Flags: ignoreversion; Components: Lexicons\Lexicon_0
Source: C:\Program Files (x86)\SIL\Lexique Pro\Display\homebanner2.jpg; DestDir: {code:GetDataDir}\Miami\Display\; Flags: ignoreversion; Components: Lexicons\Lexicon_0

; Inno Setup Files - for Distribution Wizard
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Compil32.exe; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\license.txt; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\ISCmplr.dll; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\islzma.dll; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\isscint.dll; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Setup.e32; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\SetupLdr.e32; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup

Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizModernImage.bmp; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizModernSmallImage.bmp; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizLexProImage.bmp; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\WizLexProSmallImage.bmp; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup

; Inno Setup Files - Message files
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Default.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\French.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Spanish.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\PortugueseStd.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\German.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Dutch.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Russian.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Bulgarian.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Indonesian.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\Arabic.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\ChineseSimp.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup
Source: C:\Program Files (x86)\SIL\Lexique Pro\Inno Setup\ChineseTrad.isl; DestDir: {code:GetAppDir}\Inno Setup; Flags: ignoreversion; Components: Inno_Setup

; Fonts
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\KhmerOSsys.ttf; DestDir: "{fonts}"; FontInstall: "Khmer OS System"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\KhmerOSsys.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILB.ttf; DestDir: "{fonts}"; FontInstall: "Charis SIL Bold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILB.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILBI.ttf; DestDir: "{fonts}"; FontInstall: "Charis SIL Bold Italic"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILBI.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILI.ttf; DestDir: "{fonts}"; FontInstall: "Charis SIL Italic"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILI.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILR.ttf; DestDir: "{fonts}"; FontInstall: "Charis SIL"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Program Files (x86)\SIL\Lexique Pro\Fonts\CharisSILR.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion

Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Bold.ttf; DestDir: "{fonts}"; FontInstall: "BJCree Bold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Bold.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Medium.ttf; DestDir: "{fonts}"; FontInstall: "BJCree Medium"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Medium.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Regular.ttf; DestDir: "{fonts}"; FontInstall: "BJCree"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-Regular.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-SemiBold.ttf; DestDir: "{fonts}"; FontInstall: "BJCree SemiBold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\BJCree-SemiBold.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\CatrinityFlags.otf.ttf; DestDir: "{fonts}"; FontInstall: "Catrinity Flags"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\CatrinityFlags.otf.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Black.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Black"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Black.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Bold.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Bold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Bold.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-ExtraBold.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee ExtraBold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-ExtraBold.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-ExtraLight.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee ExtraLight"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-ExtraLight.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Light.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Light"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Light.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Medium.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Medium"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Medium.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Regular.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Regular"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Regular.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-SemiBold.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee SemiBold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-SemiBold.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Thin.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Thin"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-Thin.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-VariableFont_wght.ttf; DestDir: "{fonts}"; FontInstall: "Noto Sans Cherokee Regular"; Flags: onlyifdoesntexist uninsneveruninstall
Source: C:\Users\black\GitHub\Myaamia\Etamology-Flask\static\NotoSansCherokee-VariableFont_wght.ttf; DestDir: {code:GetAppDir}\Fonts; Flags: ignoreversion


[Code]
var
  DirPage: TInputDirWizardPage;

function GetDefaultAppDir : String;
  begin
  Result := ExpandConstant('{param:APPDIR|{pf}\SIL\Lexique Pro}');
  end;

function GetDefaultDataDir : String;
  begin
  Result := ExpandConstant('{param:DATADIR|{userdocs}\Lexique Pro Data}');
  end;

procedure CreateTheWizardPages;
  var
    Msg1, Msg2 : string;
  begin
  // Create the page
  Msg1 := SetupMessage(msgSelectDirDesc);
  StringChangeEx( Msg1, '[name]', 'Lexique Pro', True);

  Msg2 := SetupMessage(msgSelectDirLabel3);
  StringChangeEx( Msg2, '[name]', 'Lexique Pro', True);

  DirPage := CreateInputDirPage(wpSelectDir,
    SetupMessage(msgWizardSelectDir),
    Msg1,
    Msg2 + #13#10#13#10 +
    SetupMessage(msgSelectDirBrowseLabel),
    False, SetupMessage(msgNewFolderName));

  // Add items
  DirPage.Add(CustomMessage('ProgramFiles') + ':');
  DirPage.Add('Lexicon data files:');

  // Set initial values
  DirPage.Values[0] := GetDefaultAppDir;
  DirPage.Values[1] := GetDefaultDataDir;
  end;

function GetAppDir(Param : String) : String;
  begin
  Result := DirPage.Values[0];
  if Result = '' then
     Result := GetDefaultAppDir;
  end;

function GetDataDir(Param : String) : String;
  begin
  Result := DirPage.Values[1];
   if Result = '' then
     Result := GetDefaultDataDir;
  end;

procedure InitializeWizard();
  begin
  CreateTheWizardPages;
  end;

[Icons]
Name: {group}\Lexique Pro - Miami; Filename: {code:GetAppDir}\bin\LexiquePro.exe; Parameters: "/f ""{code:GetDataDir}\Miami\mia_ilda_lexicon.sfm"""; IconIndex: 0; Components: Lexicons\Lexicon_0
Name: {userdesktop}\Lexique Pro - Miami; Filename: {code:GetAppDir}\bin\LexiquePro.exe; Tasks: desktopicon_1; Parameters: "/f ""{code:GetDataDir}\Miami\mia_ilda_lexicon.sfm"""; IconIndex: 0; Components: Lexicons\Lexicon_0

; Icons if database is not chosen
Name: {group}\Lexique Pro; Filename: {code:GetAppDir}\bin\LexiquePro.exe; IconIndex: 0; Components: not (Lexicons\Lexicon_0)
Name: {userdesktop}\Lexique Pro; Filename: {code:GetAppDir}\bin\LexiquePro.exe; Tasks: desktopicon_0; IconIndex: 0; Components: not (Lexicons\Lexicon_0)

[Run]
Filename: {code:GetAppDir}\bin\LexiquePro.exe; Description: {cm:LaunchLexiquePro} - Miami; Flags: nowait postinstall skipifsilent; Parameters: "/f ""{code:GetDataDir}\Miami\mia_ilda_lexicon.sfm"""; Components: Lexicons\Lexicon_0
Filename: {code:GetAppDir}\bin\LexiquePro.exe; Description: {cm:LaunchLexiquePro}; Flags: nowait postinstall skipifsilent; Components: not (Lexicons\Lexicon_0)

[Registry]
Root: HKCR; Subkey: applications\LexiquePro.exe\shell\open\command; ValueType: string; ValueData: """{code:GetAppDir}\bin\LexiquePro.exe"" /f ""%1"""; Flags: deletevalue
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: en; Flags: deletevalue; Languages: en
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: fr; Flags: deletevalue; Languages: fr
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: es; Flags: deletevalue; Languages: es
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: pt; Flags: deletevalue; Languages: pt
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: bg; Flags: deletevalue; Languages: bg
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: zh-CHT; Flags: deletevalue; Languages: zhCHT
Root: HKCU; Subkey: Software\SIL\Lexique Pro\Interface; ValueType: string; ValueName: Language; ValueData: zh-CHS; Flags: deletevalue; Languages: zhCHS

Root: HKCR; Subkey: .lpConfig; ValueType: string; ValueData: LexiquePro.Config; Flags: deletevalue
Root: HKCR; Subkey: .lpConfig; ValueType: string; ValueName: Content Type; ValueData: text/xml; Flags: deletevalue
Root: HKCR; Subkey: .lpConfig; ValueType: string; ValueName: PerceivedType; ValueData: text; Flags: deletevalue
Root: HKCR; Subkey: .lpIndex;  ValueType: string; ValueData: LexiquePro.Index; Flags: deletevalue
Root: HKCR; Subkey: .lpIndex;  ValueType: string; ValueName: Content Type; ValueData: text/plain; Flags: deletevalue
Root: HKCR; Subkey: .lpIndex;  ValueType: string; ValueName: PerceivedType; ValueData: text; Flags: deletevalue
Root: HKCR; Subkey: LexiquePro.Config; ValueType: string; ValueData: Lexique Pro Config File; Flags: deletevalue
Root: HKCR; Subkey: LexiquePro.Index;  ValueType: string; ValueData: Lexique Pro Index File; Flags: deletevalue

[Components]
Name: LexiquePro_Program; Description: {cm:ProgramFiles}; Flags: fixed; Types: custom compact full
Name: Inno_Setup; Description: {cm:DistWizProgFiles}; Types: custom compact full
Name: ICU; Description: {cm:ICU}; Types: custom compact full
Name: Lexicons; Description: {cm:Lexicons}; Types: custom compact full
Name: Lexicons\Lexicon_0; Description: Miami; Types: custom compact full

[InstallDelete]
; Delete previous versions which installed in top-level folder
Type: files; Name: {code:GetAppDir}\LexiquePro.exe
Type: files; Name: {code:GetAppDir}\*.dll
Type: files; Name: {code:GetAppDir}\*.tab

[UninstallDelete]
Type: files; Name: "{code:GetDataDir}\Miami\*.idx"
Type: files; Name: "{code:GetDataDir}\Miami\*.bak"
Type: files; Name: "{code:GetDataDir}\Miami\*.tmp"
Type: files; Name: "{code:GetDataDir}\Miami\*.iss"
Type: files; Name: "{code:GetDataDir}\Miami\*.cc"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpLocked"
Type: files; Name: "{code:GetDataDir}\Miami\*.lck"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpEnc"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpLiftEnc"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpConfigEnc"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpIndex"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpCache-UnusedLetters"
Type: files; Name: "{code:GetDataDir}\Miami\*.lpCache-InitialLetters"
