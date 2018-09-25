TO ADD SUBTITLES TO MANY FILES  

rem FOR %A IN (*.mkv) DO mkvmerge -o "remux-%~nA.mkv" "%~A" "%~dpnA.srt"  


FOR REMOVING AUDIO "-a !<mkvinfo track number to remove>"  

FOR /F "delims=*" %%A IN ('dir /b *.MKV') DO "mkvmerge.exe" -o "fixed_%%A" -a !1 --compression -1:none "%%A"  


FOR REMOVING Many AUDIO  

FOR /F "delims=*" %%A IN ('dir /b *.MKV') DO "mkvmerge.exe" -o "E:\DBZ\%%A" -a !2,3 --compression -1:none "%%A"  


FOR EXTRACTING SUBS  

FOR /F "delims=*" %%A IN ('dir /b *.MKV') DO "mkvextract" tracks "%%A" 4:"E:\DBZSUBS\%%A.sup"  

EXTRACTING AND MERGING  

@ECHO OFF  
SETLOCAL  
SET "destdir=F:\Animes\Naruto (2002) Complete Series\All"  
dir "%destdir%"  
echo  
echo  
FOR /f "tokens=1*delims=:" %%A IN (  
 'dir /b /a-d "*.mkv"^|findstr /n /r "." '  
 ) DO (  
 FOR /f "tokens=1*delims=:" %%D IN (  
  'dir /b /a-d "%destdir%\*.mkv"^|findstr /n /r "." '  
  ) DO IF %%A==%%D mkvextract tracks "%%B" 1:"%destdir%\%%~nE.ogg" && mkvmerge -o "D:\remux-%%~nE.mkv" "%destdir%\%%E" "%destdir%\%%~nE.ogg"  
)
GOTO :EOF  
