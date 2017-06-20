let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
map! <S-Insert> <MiddleMouse>
noremap <silent>  :nohl
nmap d :cs find d =expand("<cword>")	
nmap i :cs find i ^=expand("<cfile>")$
nmap f :cs find f =expand("<cfile>")	
nmap e :cs find e =expand("<cword>")	
nmap t :cs find t =expand("<cword>")	
nmap c :cs find c =expand("<cword>")	
nmap g :cs find g =expand("<cword>")	
nmap s :cs find s =expand("<cword>")	
nmap ,ic :call InsertComment()
nmap ,sp :call SavePosition()                                                                                                                                                                                   
nmap <silent> \vv <Plug>VCSVimDiff
nmap <silent> \vu <Plug>VCSUpdate
nmap <silent> \vU <Plug>VCSUnlock
nmap <silent> \vs <Plug>VCSStatus
nmap <silent> \vr <Plug>VCSReview
nmap <silent> \vq <Plug>VCSRevert
nmap <silent> \vn <Plug>VCSAnnotate
nmap <silent> \vl <Plug>VCSLog
nmap <silent> \vL <Plug>VCSLock
nmap <silent> \vi <Plug>VCSInfo
nmap <silent> \vg <Plug>VCSGotoOriginal
nmap <silent> \vG <Plug>VCSClearAndGotoOriginal
nmap <silent> \vd <Plug>VCSDiff
nmap <silent> \vD <Plug>VCSDelete
nmap <silent> \vc <Plug>VCSCommit
nmap <silent> \va <Plug>VCSAdd
map <silent> \cc <Plug>CRV_CRefVimInvoke
map <silent> \cw <Plug>CRV_CRefVimAsk
nmap <silent> \cr <Plug>CRV_CRefVimNormal
vmap <silent> \cr <Plug>CRV_CRefVimVisual
map \rwp <Plug>RestoreWinPosn
map \swp <Plug>SaveWinPosn
nmap \ihn :IHN
nmap \is :IHS:A
nmap \ih :IHS
vmap <silent> \x <Plug>VisualTraditional
vmap <silent> \c <Plug>VisualTraditionalj
nmap <silent> \x <Plug>Traditional
nmap <silent> \c <Plug>Traditionalj
map \tt <Plug>AM_tt
map \tsq <Plug>AM_tsq
map \tsp <Plug>AM_tsp
map \tml <Plug>AM_tml
map \tab <Plug>AM_tab
map \m= <Plug>AM_m=
map \t@ <Plug>AM_t@
map \t~ <Plug>AM_t~
map \t? <Plug>AM_t?
map \w= <Plug>AM_w=
map \ts= <Plug>AM_ts=
map \ts< <Plug>AM_ts<
map \ts; <Plug>AM_ts;
map \ts: <Plug>AM_ts:
map \ts, <Plug>AM_ts,
map \t= <Plug>AM_t=
map \t< <Plug>AM_t<
map \t; <Plug>AM_t;
map \t: <Plug>AM_t:
map \t, <Plug>AM_t,
map \t# <Plug>AM_t#
map \t| <Plug>AM_t|
map \T~ <Plug>AM_T~
map \Tsp <Plug>AM_Tsp
map \Tab <Plug>AM_Tab
map \T@ <Plug>AM_T@
map \T? <Plug>AM_T?
map \T= <Plug>AM_T=
map \T< <Plug>AM_T<
map \T; <Plug>AM_T;
map \T: <Plug>AM_T:
map \Ts, <Plug>AM_Ts,
map \T, <Plug>AM_T,o
map \T# <Plug>AM_T#
map \T| <Plug>AM_T|
map \Htd <Plug>AM_Htd
map \anum <Plug>AM_aunum
map \aunum <Plug>AM_aenum
map \afnc <Plug>AM_afnc
map \adef <Plug>AM_adef
map \adec <Plug>AM_adec
map \ascom <Plug>AM_ascom
map \aocom <Plug>AM_aocom
map \adcom <Plug>AM_adcom
map \acom <Plug>AM_acom
map \abox <Plug>AM_abox
map \a( <Plug>AM_a(
map \a= <Plug>AM_a=
map \a< <Plug>AM_a<
map \a, <Plug>AM_a,
map \a? <Plug>AM_a?
nmap gx <Plug>NetrwBrowseX
map <S-Insert> <MiddleMouse>
nnoremap <silent> <Plug>VCSVimDiff :VCSVimDiff
nnoremap <silent> <Plug>VCSUpdate :VCSUpdate
nnoremap <silent> <Plug>VCSUnlock :VCSUnlock
nnoremap <silent> <Plug>VCSStatus :VCSStatus
nnoremap <silent> <Plug>VCSReview :VCSReview
nnoremap <silent> <Plug>VCSRevert :VCSRevert
nnoremap <silent> <Plug>VCSLog :VCSLog
nnoremap <silent> <Plug>VCSLock :VCSLock
nnoremap <silent> <Plug>VCSInfo :VCSInfo
nnoremap <silent> <Plug>VCSClearAndGotoOriginal :VCSGotoOriginal!
nnoremap <silent> <Plug>VCSGotoOriginal :VCSGotoOriginal
nnoremap <silent> <Plug>VCSDiff :VCSDiff
nnoremap <silent> <Plug>VCSDelete :VCSDelete
nnoremap <silent> <Plug>VCSCommit :VCSCommit
nnoremap <silent> <Plug>VCSAnnotate :VCSAnnotate
nnoremap <silent> <Plug>VCSAdd :VCSAdd
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetrwBrowseX(expand("<cWORD>"),0)
nmap <Nul><Nul>d :vert scs find d =expand("<cword>")
nmap <Nul><Nul>i :vert scs find i ^=expand("<cfile>")$	
nmap <Nul><Nul>f :vert scs find f =expand("<cfile>")	
nmap <Nul><Nul>e :vert scs find e =expand("<cword>")
nmap <Nul><Nul>t :vert scs find t =expand("<cword>")
nmap <Nul><Nul>c :vert scs find c =expand("<cword>")
nmap <Nul><Nul>g :vert scs find g =expand("<cword>")
nmap <Nul><Nul>s :vert scs find s =expand("<cword>")
nmap <Nul>d :scs find d =expand("<cword>")	
nmap <Nul>i :scs find i ^=expand("<cfile>")$	
nmap <Nul>f :scs find f =expand("<cfile>")	
nmap <Nul>e :scs find e =expand("<cword>")	
nmap <Nul>t :scs find t =expand("<cword>")	
nmap <Nul>c :scs find c =expand("<cword>")	
nmap <Nul>g :scs find g =expand("<cword>")	
nmap <Nul>s :scs find s =expand("<cword>")	
nmap <silent> <Plug>RestoreWinPosn :call RestoreWinPosn()
nmap <silent> <Plug>SaveWinPosn :call SaveWinPosn()
noremap <Plug>VisualFirstLine :call EnhancedCommentify('', 'first',   line("'<"), line("'>"))
noremap <Plug>VisualTraditional :call EnhancedCommentify('', 'guess',   line("'<"), line("'>"))
noremap <Plug>VisualDeComment :call EnhancedCommentify('', 'decomment',   line("'<"), line("'>"))
noremap <Plug>VisualComment :call EnhancedCommentify('', 'comment',   line("'<"), line("'>"))
noremap <Plug>FirstLine :call EnhancedCommentify('', 'first')
noremap <Plug>Traditional :call EnhancedCommentify('', 'guess')
noremap <Plug>DeComment :call EnhancedCommentify('', 'decomment')
noremap <Plug>Comment :call EnhancedCommentify('', 'comment')
nmap <SNR>14_WE <Plug>AlignMapsWrapperEnd
map <SNR>14_WS <Plug>AlignMapsWrapperStart
nnoremap <silent> <F10> :let @*=expand("%:t").":".line(".")
map <F11> :BufExplorer
nnoremap <silent> <F8> :TlistToggle
nnoremap <silent> <F9> :NERDTreeToggle
map <F6> :next 
map <F5> :previous 
map <F3> 
map <F2> 
map <silent> <F1> :!cscope -R -b && ctags -R *.c *.h
imap \ihn :IHN
imap \is :IHS:A
imap \ih :IHS
imap <silent> \x <Plug>Traditional
imap <silent> \c <Plug>Traditionalji
let &cpo=s:cpo_save
unlet s:cpo_save
set autowrite
set background=dark
set backspace=2
set cinoptions=:0
set cscopetag
set cscopeverbose
set fileencodings=ucs-bom,utf-8,default,latin1
set guioptions=aegimrLt
set helplang=en
set hidden
set history=100
set hlsearch
set ignorecase
set incsearch
set laststatus=2
set mouse=a
set printoptions=paper:a4
set ruler
set runtimepath=~/.vim,/var/lib/vim/addons,/usr/share/vim/vimfiles,/usr/share/vim/vim74,/usr/share/vim/vimfiles/after,/var/lib/vim/addons/after,~/.vim/after
set showcmd
set showmatch
set smartcase
set smartindent
set spellsuggest=best,10
set suffixes=.bak,~,.swp,.o,.info,.aux,.log,.dvi,.bbl,.blg,.brf,.cb,.ind,.idx,.ilg,.inx,.out,.toc
set termencoding=utf-8
set wildignore=*.pyc
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/getienne-host-tools/py-script
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +71 GitHeaderPrefix.py
argglobal
silent! argdel *
argadd GitHeaderPrefix.py
edit GitHeaderPrefix.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal backupcopy=
setlocal balloonexpr=
setlocal nobinary
setlocal nobreakindent
setlocal breakindentopt=
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),:,!^F,o,O,e
setlocal cinoptions=:0
setlocal cinwords=if,else,while,do,for,switch
setlocal colorcolumn=
setlocal comments=b:#,fb:-
setlocal commentstring=#\ %s
setlocal complete=.,w,b,u,t,i
setlocal concealcursor=
setlocal conceallevel=0
setlocal completefunc=
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal expandtab
if &filetype != 'python'
setlocal filetype=python
endif
setlocal fixendofline
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
set foldmethod=marker
setlocal foldmethod=marker
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatoptions=tcq
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=2
setlocal imsearch=2
setlocal include=^\\s*\\(from\\|import\\)
setlocal includeexpr=substitute(v:fname,'\\.','/','g')
setlocal indentexpr=GetPythonIndent(v:lnum)
setlocal indentkeys=0{,0},:,!^F,o,O,e,<:>,=elif,=except
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255,*,/
setlocal keywordprg=pydoc
setlocal nolinebreak
setlocal nolisp
setlocal lispwords=
setlocal nolist
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal modeline
setlocal modifiable
setlocal nrformats=bin,octal,hex
setlocal nonumber
setlocal numberwidth=4
setlocal omnifunc=pythoncomplete#Complete
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norelativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=4
setlocal noshortname
setlocal smartindent
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=
setlocal suffixesadd=.py
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'python'
setlocal syntax=python
endif
setlocal tabstop=8
setlocal tagcase=
setlocal tags=
setlocal textwidth=0
setlocal thesaurus=
setlocal noundofile
setlocal undolevels=-123456
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
let s:l = 6 - ((5 * winheight(0) + 35) / 71)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
6
normal! 014|
lcd ~/getienne-host-tools/py-script
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
