; BCacheTranslation 安装脚本

[Setup]
AppName=BCacheTranslation
AppVersion=2.0.0
AppPublisher=clehj
DefaultDirName={autopf}\BCacheTranslation
DefaultGroupName=BCacheTranslation
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=BCacheTranslation_Setup_2.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
; 移除语言设置，使用默认英文

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\BCacheTranslation_v2.0.0\BCacheTranslation_v2.0.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BCacheTranslation_v2.0.0\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "style_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BCacheTranslation"; Filename: "{app}\BCacheTranslation.exe"
Name: "{group}\Uninstall BCacheTranslation"; Filename: "{uninstallexe}"
Name: "{autodesktop}\BCacheTranslation"; Filename: "{app}\BCacheTranslation.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BCacheTranslation.exe"; Description: "Launch BCacheTranslation"; Flags: postinstall nowait skipifsilent