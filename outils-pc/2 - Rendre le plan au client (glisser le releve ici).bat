@echo off
rem Pas de "chcp 65001" ici : sous Windows, la page de code UTF-8 empeche
rem "set /p" de lire ce que l'on tape. Tous les messages sont donc sans accent.
setlocal enabledelayedexpansion
title SC Carto - plan enrichi pour le client
color 0E

if "%~1"=="" (
  echo.
  echo   ==========================================================
  echo    SC Carto - rendre le plan enrichi au client
  echo   ==========================================================
  echo.
  echo    Mode d'emploi : prenez le fichier ZIP exporte par
  echo    l'application et GLISSEZ-LE sur cette icone.
  echo.
  echo    Ne double-cliquez pas dessus : il ne saurait pas quoi faire.
  echo.
  pause
  exit /b
)

set "OUTILS=%~dp0"
set "JSON=%~1"

echo.
echo   ==========================================================
echo    Releve : %~nx1
echo   ==========================================================
echo.
echo   Il me faut encore deux fichiers. Pour chacun :
echo   glissez-le DANS CETTE FENETRE, puis appuyez sur Entree.
echo.
echo   1 sur 2 - le DXF d'origine du client
set "DXF="
set /p "DXF=       ici : "
if not defined DXF goto :manque
set DXF=%DXF:"=%

echo.
echo   2 sur 2 - le fichier .calage.json
echo             (cree en meme temps que le fond de plan)
set "CAL="
set /p "CAL=       ici : "
if not defined CAL goto :manque
set CAL=%CAL:"=%

echo.
echo   ----------------------------------------------------------
echo.

python "%OUTILS%points2dxf.py" --json "%JSON%" --dxf "%DXF%" --calage "%CAL%" --couleurs-statut --remplacer

if errorlevel 1 (
  echo.
  echo   L'operation a echoue. Relisez le message ci-dessus.
  goto :fin
)

echo.
echo   ==========================================================
echo    C'est fait. Le fichier _boites.dxf est a cote du DXF
echo    d'origine. Le plan du client n'a pas ete modifie :
echo    c'est une copie, avec un calque en plus.
echo   ==========================================================
echo.
goto :fin

:manque
echo.
echo   Fichier manquant, rien n'a ete fait. Relancez.
echo.

:fin
pause
