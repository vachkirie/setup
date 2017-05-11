" special c syntax file modifier:
" add C function highlight

" old version with macro
"syntax match cFunction display "\<\h\w*\>\s*("me=e-1
syntax match cFunction display "\<\h\w*("me=e-1
syntax match cFunction display "*\*\h\w*("me=e-1,ms=s+1
hi cFunction  term=underline cterm=bold ctermfg=11 guifg=Orange
"highlight def link cFunction Function
