let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd D:\python\qdocviewer\scripts
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +35 D:\python\qdocviewer\__main__.py
badd +36 D:\python\qdocviewer\mainwindow.py
badd +55 D:\python\qdocviewer\server.py
badd +1 D:\python\qdocviewer\index.py
badd +160 D:\python\qdocviewer\viewer.py
badd +73 D:\python\qdocviewer\utils.py
badd +7 D:\python\qdocviewer\format\zipped.py
badd +1 D:\python\qdocviewer\format\__init__.py
badd +1 D:\python\qdocviewer\format\directory.py
badd +1 D:\python\qdocviewer\format\base.py
badd +1 D:\python\qdocviewer\tree.py
badd +1 D:\python\qdocviewer\__init__.py
badd +1 D:\python\qdocviewer\format\mirror.py
badd +1 D:\python\qdocviewer\stack.py
badd +1 D:\python\qdocviewer\status.py
badd +1 D:\python\qdocviewer\docs\docs.yaml
badd +1 D:\python\qdocviewer\scripts\index.py
argglobal
%argdel
$argadd \python\qdocviewer\docs.yaml
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
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit D:\python\qdocviewer\docs\docs.yaml
argglobal
balt D:\python\qdocviewer\__main__.py
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
let s:l = 58 - ((57 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 58
normal! 03|
tabnext
edit D:\python\qdocviewer\__main__.py
argglobal
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
let s:l = 172 - ((57 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 172
normal! 013|
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
let s:l = 43 - ((37 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 43
normal! 068|
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
let s:l = 21 - ((20 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 21
normal! 019|
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
let s:l = 78 - ((29 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 78
normal! 045|
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
let s:l = 79 - ((18 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 79
normal! 087|
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
let s:l = 57 - ((45 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 57
normal! 016|
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
let s:l = 15 - ((14 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 15
normal! 014|
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
let s:l = 67 - ((38 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 67
normal! 021|
tabnext
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
let s:l = 18 - ((17 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 059|
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
let s:l = 21 - ((20 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 21
normal! 0
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
tabnext
edit D:\python\qdocviewer\scripts\index.py
argglobal
balt D:\python\qdocviewer\utils.py
setlocal fdm=marker
setlocal fde=PythonFold(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=99
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 110 - ((26 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 110
normal! 034|
tabnext 18
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
