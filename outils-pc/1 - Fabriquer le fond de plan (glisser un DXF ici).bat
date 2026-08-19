@echo off
rem Pas de "chcp 65001" ici : sous Windows, la page de code UTF-8 empeche
rem "set /p" de lire ce que l'on tape. Tous les messages sont donc sans accent.
setlocal enabledelayedexpansion
title SC Carto - fabrication du fond de plan
color 0B

if "%~1"=="" (
  echo.
  echo   ==========================================================
  echo    SC Carto - fabrication du fond de plan
  echo   ==========================================================
  echo.
  echo    Mode d'emploi : prenez le fichier DXF du client et
  echo    GLISSEZ-LE sur cette icone.
  echo.
  echo    Ne double-cliquez pas dessus : il ne saurait pas quoi faire.
  echo.
  pause
  exit /b
)

set "OUTILS=%~dp0"
set "DXF=%~1"
set "SORTIE=%~dpn1.svg"

echo.
echo   ==========================================================
echo    Plan a convertir : %~nx1
echo   ==========================================================
echo.
echo   Voici les calques que contient ce plan :
echo.

python "%OUTILS%dxf2fond.py" "%DXF%" --lister
if errorlevel 1 goto :fin

echo.
echo   Quels calques faut-il JETER ?
echo   Typiquement : les cotations, le mobilier, les axes, les hachures.
echo   Tapez leurs noms separes par des virgules, ou laissez vide
echo   pour tout garder, puis appuyez sur Entree.
echo.
set "EXCL="
set /p "EXCL=   A jeter : "
echo.
echo   ----------------------------------------------------------
echo.

if "!EXCL!"=="" (
  python "%OUTILS%dxf2fond.py" "%DXF%" -o "%SORTIE%"
) else (
  python "%OUTILS%dxf2fond.py" "%DXF%" -o "%SORTIE%" --exclure "!EXCL!"
)

if errorlevel 1 (
  echo.
  echo   La conversion a echoue. Relisez le message ci-dessus.
  goto :fin
)

echo.
echo   ==========================================================
echo    C'est fait. Deux fichiers ont ete crees a cote du DXF :
echo.
echo      - le fichier .svg     ^: a copier sur le telephone
echo      - le fichier .calage  ^: A GARDER ICI, il servira au retour
echo   ==========================================================
echo.
echo   Le resultat ne vous plait pas ? Relancez en jetant
echo   d'autres calques, cela ne coute rien.
echo.

:fin
pause
