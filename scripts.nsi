; Installer Details
Outfile "FXSignalSpot_Binary_Trader.exe"
Name "FXSignalSpot Binary Trader Installer"
Icon "SetupClassicIcon.ico"

; Default installation directory
InstallDir "$PROGRAMFILES\Binary Trader"

; Pages
Page Components
Page Directory
Page InstFiles

; Components
Section "Main Application" SEC_MAIN
SetOutPath "$INSTDIR"
; Add your application files here
File "FXSignalSpot_Binary_Trader.exe"
File "login_details.json"
File "session_name.session"
File "brokerWidget.ui"
File "loaderWidget.ui"
File "loginWidget.ui"
File "mainWidget.ui"
File "signUpWidget.ui"
File "syntheticWidget.ui"
File "tradeWidget.ui"
File "WorkSans-Medium.ttf"
File "WorkSans-Regular.ttf"
File "resources.py"
File "TelegramCrawler.py"
File "TelegramUpdate.py"
SectionEnd

; Shortcuts
Section "Desktop Shortcut"
CreateDirectory "$DESKTOP"
CreateShortCut "$DESKTOP\FXSignalSpot_Binary_Trader.lnk" "$INSTDIR\FXSignalSpot_Binary_Trader.exe"
SectionEnd

; Start Menu Shortcut
Section "Start Menu Shortcut"
CreateDirectory "$SMPROGRAMS\Binary Trader"
CreateShortCut "$SMPROGRAMS\Binary Trader\FXSignalSpot_Binary_Trader.lnk" "$INSTDIR\FXSignalSpot_Binary_Trader.exe"
SectionEnd

; Uninstaller
Section "Uninstall"
Delete "$INSTDIR\FXSignalSpot_Binary_Trader.exe"
RMDir "$INSTDIR"
SectionEnd

; Uninstaller - Additional cleanup
Section "Uninstall - Additional Cleanup"
; Add any additional cleanup actions here
SectionEnd

; Uninstaller - Remove desktop shortcut
Section "Uninstall - Remove Desktop Shortcut"
Delete "$DESKTOP\FXSignalSpot_Binary_Trader.lnk"
SectionEnd

; Uninstaller - Remove Start Menu shortcut
Section "Uninstall - Remove Start Menu Shortcut"
Delete "$SMPROGRAMS\Binary Trader\FXSignalSpot_Binary_Trader.lnk"
RMDir "$SMPROGRAMS\Binary Trader"
SectionEnd
