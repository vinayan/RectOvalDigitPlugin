" this is mostly a matter of taste. but LaTeX looks good with just a bit
" of indentation.
set sw=2
" TIP: if you write your \label's as \label{fig:something}, then if you
" type in \ref{fig: and press <C-n> you will automatically cycle through
" all the figure labels. Very useful!
set iskeyword+=:

let g:tex_flavor='latex'
let g:Tex_DefaultTargetFormat='pdf'
let g:Tex_ViewRule_pdf='evince'

" Using imaps.vim

call IMAP("/e","é","tex")
call IMAP ("/em" , "\\emph{<++>} <++>" , "tex")


call IMAP ("/s3" , "\\subsubsection{ <++> }\<CR><++>" , "tex")
call IMAP ("/s2" , "\\subsection{ <++> }\<CR><++>" , "tex")
call IMAP ("/s1" , "\\section{ <++> }\<CR><++>" , "tex")

call IMAP ("/p" , "\\paragraph{ <++> }<++>" , "tex")
call IMAP ("/sp" , "\\subparagraph{ <++> } <++>" , "tex")

call IMAP ("/bit", "\\begin{itemize}\<cr>\\item <++>\<cr>\\end{itemize}\<cr><++>", "tex")

call IMAP("/footnote", "\\footnote{ <++> } <++>", "tex")

call IMAP("\item", "\\item <++>", "tex")

call IMAP("/fig", "\\begin{figure}\<cr>\\centering\\includegraphics[<++>]{<++>}\<cr>\\caption{<++>}\<cr>\\label{<++>}\<cr>\\end{figure}", "tex")

" Fix the é bug
imap <buffer> <leader>it <Plug>Tex_InsertItemOnThisLine
