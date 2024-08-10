let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd D:\python\qdocviewer
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +68 D:\python\qdocviewer\docs.yaml
badd +25 D:\python\qdocviewer\__main__.py
badd +36 D:\python\qdocviewer\mainwindow.py
badd +55 D:\python\qdocviewer\server.py
badd +1 D:\python\qdocviewer\index.py
badd +1 D:\python\qdocviewer\viewer.py
badd +1 D:\python\qdocviewer\utils.py
badd +7 D:\python\qdocviewer\format\zipped.py
badd +1 D:\python\qdocviewer\format\__init__.py
badd +1 D:\python\qdocviewer\format\directory.py
badd +1 D:\python\qdocviewer\format\base.py
badd +1 D:\python\qdocviewer\tree.py
badd +1 D:\python\qdocviewer\__init__.py
badd +1 D:\python\qdocviewer\format\mirror.py
badd +1 D:\python\qdocviewer\stack.py
badd +1 D:\python\qdocviewer\status.py
argglobal
%argdel
$argadd docs.yaml
set lines=61 columns=226
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit D:\python\qdocviewer\docs.yaml
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 113 - ((46 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 113
normal! 05|
tabnext
edit D:\python\qdocviewer\__main__.py
argglobal
balt D:\python\qdocviewer\docs.yaml
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 35 - ((34 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 35
normal! 02|
tabnext
edit D:\python\qdocviewer\__init__.py
argglobal
balt D:\python\qdocviewer\__main__.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 1 - ((0 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
tabnext
edit D:\python\qdocviewer\mainwindow.py
argglobal
balt D:\python\qdocviewer\__main__.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 64 - ((40 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 64
normal! 058|
tabnext
edit D:\python\qdocviewer\status.py
argglobal
balt D:\python\qdocviewer\mainwindow.py
setlocal fdm=manual
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 60 - ((35 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 60
normal! 099|
tabnext
edit D:\python\qdocviewer\stack.py
argglobal
balt D:\python\qdocviewer\mainwindow.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 9 - ((8 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 9
normal! 033|
tabnext
edit D:\python\qdocviewer\index.py
argglobal
balt D:\python\qdocviewer\mainwindow.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 118 - ((38 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 118
normal! 014|
tabnext
edit D:\python\qdocviewer\tree.py
argglobal
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 61 - ((36 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 61
normal! 0
tabnext
edit D:\python\qdocviewer\viewer.py
argglobal
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 129 - ((26 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 129
normal! 048|
tabnext
edit D:\python\qdocviewer\server.py
argglobal
balt D:\python\qdocviewer\mainwindow.py
setlocal fdm=manual
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 47 - ((46 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 47
normal! 037|
tabnext
edit D:\python\qdocviewer\format\zipped.py
argglobal
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 27 - ((26 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 27
normal! 029|
tabnext
edit D:\python\qdocviewer\format\mirror.py
argglobal
balt D:\python\qdocviewer\format\zipped.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 110 - ((32 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 110
normal! 034|
tabnext
edit D:\python\qdocviewer\format\base.py
argglobal
balt D:\python\qdocviewer\format\zipped.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 22 - ((2 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 22
normal! 014|
tabnext
tabnext
edit D:\python\qdocviewer\format\directory.py
argglobal
balt D:\python\qdocviewer\format\zipped.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 17 - ((16 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 17
normal! 029|
tabnext
edit D:\python\qdocviewer\format\__init__.py
argglobal
balt D:\python\qdocviewer\format\zipped.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 22 - ((21 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 22
normal! 031|
tabnext
edit D:\python\qdocviewer\utils.py
argglobal
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 73 - ((0 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 73
normal! 0
tabnext 17
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
