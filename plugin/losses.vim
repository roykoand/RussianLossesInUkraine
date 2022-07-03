let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')
let $PYTHONPATH = expand('~/RussianLossesInUkraine/plugin/env/lib/python3.7/site-packages')

set laststatus=2

python3 << EOF
import sys
import os
import vim

sys.path.insert(0, vim.eval('s:script_dir'))

import parse_losses

vim.command('set statusline=[RUSSIAN\ \LOSSES]\ ')
separator = "\\ \\"
vim.command(f'set statusline+={parse_losses.RussianLosses().parse().replace(" ", separator)}')
EOF
