"
" VIM configuration file of Frederic Chanal
"

" Use Vim settings, rather then Vi settings (much better!).
" This must be first, because it changes other options as a side effect.
set nocompatible

" Basics settings
set laststatus=2
set hlsearch
set showcmd			" Show (partial) command in status line.
set showmatch		" Show matching brackets.
set ignorecase		" Do case insensitive matching
set smartcase		" Do smart case matching
set incsearch		" Incremental search
set autowrite		" Automatically save before commands like :next and :make
set hidden  		" Hide buffers when they are abandoned
set mouse=a			" Enable mouse usage (all modes) in terminals
set tabstop=8		" Tab length
set shiftwidth=8	" Indenting length
set smartindent		" Indenting method
set backspace=2		" Enable backspace in insert mode
set ruler			" Display the column and line in the status line
set history=100		" History remember 100 command
set foldmethod=marker	" Use marker for folding
set spellsuggest+=10	" Max number of suggestions
let c_space_errors=1

"highlight OverLength ctermbg=red ctermfg=white guibg=#592929
"match OverLength /\%81v.\+/
"set hls 


" Enable syntax
syntax on

" Specific C syntax option
set cinoptions+=:0

" Set graphic option
set background=dark

" Graphic enhancement (must be after set 'bg') 
" -> for gvim it must be set in MYGVIMRC file


" Mapping
" =======
"map <silent> <F1> :!find . -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name 'Kconfig' -o -name 'Makefile' >> tag.filelist && cscope -i tag.filelist && ctags -L tag.filelist<CR>
map <silent> <F1> :!cscope -R -b && ctags -R *.c *.h<CR>
map <F2> <C-]>
map <F3> <C-t>
"nmap <F2> :cs find g <C-R>=expand("<cword>")<CR><CR>
"nmap <F3> :cs find c <C-R>=expand("<cword>")<CR><CR>
"nmap <F4> :cs find d <C-R>=expand("<cword>")<CR><CR>
map <F5> :previous <cr>
map <F6> :next <cr>
nnoremap <silent> <F9> :NERDTreeToggle<CR>
nnoremap <silent> <F8> :TlistToggle<CR>
map <F11> :BufExplorer<CR>
noremap <silent> <C-H> :nohl<CR>
nnoremap <silent> <F10> :let @*=expand("%:t").":".line(".")<CR>

" Plugin modifier
" ===============
let VCSCommandMapPrefix="<leader>v" " Mapping modifier for VCSCommand plugin
" set statusline=%<%f\ %([%{Tlist_Get_Tagname_By_Line()}]%)%h%m%r%=%-14.(%l,%c%V%)\ %P
let NERDTreeHijackNetrw=0

" User defined functions
" ======================



function! SaveAndQuit()
	if (getcwd() =~ "^".$HOME)
		if (g:loaded_nerd_tree)
			NERDTreeClose
		end
		mksession!
	endif
endfunction

" Autocommands
" ============
autocmd! VimLeave * call SaveAndQuit()

" Command
"========
" Convenient command to see the difference between the current buffer and the
" file it was loaded from, thus the changes you made.
command! DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis
	 	\ | wincmd p | diffthis

" Load specific plugin
" ====================
runtime! ftplugin/man.vim

" Only do this part when compiled with support for autocommands.
if has("autocmd")

  " Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
  filetype plugin indent on

  " Put these in an autocmd group, so that we can delete them easily.
  augroup vimrcEx
  au!

  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78

  " When editing a file, always jump to the last known cursor position.
  " Don't do it when the position is invalid or when inside an event handler
  " (happens when dropping a file on gvim).
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal! g`\"" |
    \ endif


  autocmd BufWritePre * :%s/\s\+$//e

  augroup END

else

  set autoindent		" always set autoindenting on

endif " has("autocmd")


"code review                                                                                                                                                                                                        
function SavePosition()                                                                                                                                                                                             
  let g:file_name=expand("%")                                                                                                                                                                                       
  let g:line_number=line(".")                                                                                                                                                                                       
  let g:reviewer_initials="GE" " Your initials                                                                                                                                                                      
endfunction                                                                                                                                                                                                         
                                                                                                                                                                                                                    
function InsertComment()                                                                                                                                                                                            
  execute "normal i". g:file_name . ":" . g:line_number . ": " . g:reviewer_initials . " - "                                                                                                                        
  startinsert                                                                                                                                                                                                       
endfunction                                                                                                                                                                                                         
nmap ,sp :call SavePosition()<CR>                                                                                                                                                                                   
nmap ,ic :call InsertComment()<CR>


"if has("cscope")
"	set csprg=/usr/bin/cscope
"	set csto=0
"	set cst
"	set nocsverb
	" Ajouter la base du rÃ©pertoire courant.
"	if filereadable("cscope.out")
"	    cscope add cscope.out
	" Sinon ajouter la base dÃ©signÃ©e par l'environnement.
"	elseif $CSCOPE_DB != ""
"	    cscope add $CSCOPE_DB
"	endif
"	set csverb
"endif " has("cscope")

