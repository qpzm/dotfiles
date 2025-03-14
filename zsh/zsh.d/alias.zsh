# Custom Alias commands for ZSH

# Basic
alias c='command'

alias cp='nocorrect cp -iv'
alias mv='nocorrect mv -iv'
alias rm='nocorrect rm -iv'

# sudo, but inherits $PATH from the current shell
alias sudoenv='sudo env PATH=$PATH'

if (( $+commands[htop] )); then
    alias top='htop'
    alias topc='htop -s PERCENT_CPU'
    alias topm='htop -s PERCENT_MEM'
fi

# list
if command -v exa 2>&1 >/dev/null; then
    # exa is our friend :)
    alias ls='exa'
    alias l='exa --long --group --git'
else
    # fallback to normal ls
    alias l='ls'
fi

# Screen
alias scr='screen -rD'

# vim: Defaults to Neovim if exists
if command -v nvim 2>&1 >/dev/null; then
    alias vim='nvim'
fi
alias vi='vim'
alias v='vim'

# Just open ~/.vimrc, ~/.zshrc, etc.
alias vimrc='vim +cd\ ~/.vim -O ~/.vim/vimrc ~/.vim/plugins.vim'
alias zshrc='vim +cd\ ~/.zsh -O ~/.zsh/zshrc ~/.zpreztorc'

# Tmux ========================================= {{{

# create a new session with name
alias tmuxnew='tmux new -s'
# list sessions
alias tmuxl='tmux list-sessions'
# tmuxa <session> : attach to <session> (force 256color and detach others)
alias tmuxa='tmux -2 attach-session -d -t'
# tmux kill-session -t
alias tmuxkill='tmux kill-session -t'

# I am lazy, yeah
alias t='tmuxa'
alias T='TMUX= tmuxa'

# tmuxp
function tmuxp {
    tmuxpfile="$1"
    if [ -z "$tmuxpfile" ] && [[ -s ".tmuxp.yaml" ]]; then
        tmuxpfile=".tmuxp.yaml"
    fi

    if [[ -s "$tmuxpfile" ]]; then
        # (load) e.g. $ tmuxp [.tmuxp.yaml]
        command tmuxp load $tmuxpfile
    else
        # (normal commands)
        command tmuxp $@;
    fi
}

alias set-pane-title='set-window-title'
alias tmux-pane-title='set-window-title'

# }}}
# SSH ========================================= {{{

if [[ "$(uname)" == "Darwin" ]] && (( $+commands[iterm-tab-color] )); then
  ssh() {
    command ssh $@
    iterm-tab-color reset 2>/dev/null
  }
fi

function ssh-tmuxa {
    host="$1"
    if [[ -z "$2" ]]; then
       ssh $host -t tmux attach -d
    else;
       ssh $host -t tmux attach -d -t "$2"
    fi
}
alias sshta='ssh-tmuxa'
alias ssh-ta='ssh-tmuxa'
compdef '_hosts' ssh-tmuxa
# }}}

# More Git aliases ============================= {{{
# (overrides prezto's default git/alias.zsh)

alias gh='git history'
alias gha='gh --all'
alias gd='git diff --no-prefix'
alias gdc='gd --cached --no-prefix'
alias gds='gd --staged --no-prefix'
alias gs='git status'
alias gsu='gs -u'

# using the vim plugin 'GV'!
function _vim_gv {
    vim -c ":GV $1"
}
alias gv='_vim_gv'
alias gva='gv --all'

# }}}


# Python ======================================= {{{

# anaconda
alias sa='source activate'

# virtualenv
alias wo='workon'

# ipython
alias ipy='ipython'
alias ipypdb='ipy -c "%pdb" -i'   # with auto pdb calling turned ON

alias ipynb='jupyter notebook'
alias ipynb0='ipynb --ip=0.0.0.0'
alias jupyter-lab='jupyter-lab --no-browser'

# ptpython
alias ptpy='ptipython'

# pip install nose, rednose
alias nt='NOSE_REDNOSE=1 nosetests -v'

# unit test: in verbose mode
alias pytest='pytest -vv'
alias green='green -vv'

# }}}


# Some useful aliases for CLI scripting (pipe, etc)
alias awk1="awk '{print \$1}'"
alias awk2="awk '{print \$2}'"
alias awk3="awk '{print \$3}'"
alias awk4="awk '{print \$4}'"
alias awk5="awk '{print \$5}'"
alias awk6="awk '{print \$6}'"
alias awk7="awk '{print \$7}'"
alias awk8="awk '{print \$8}'"
alias awk9="awk '{print \$9}'"
alias awklast="awk '{print \$\(NF\)}'"


# Codes ===================================== {{{

alias prettyxml='xmllint --format - | pygmentize -l xml'

if (( $+commands[cdiff] )); then
    # cdiff, side-by-side with full width
    alias sdiff="cdiff -s -w0"
fi

# }}}


# Etc ======================================= {{{

alias iterm-tab-color="noglob iterm-tab-color"

if (( $+commands[pydf] )); then
    # pip install --user pydf
    # pydf: a colorized df
    alias df="pydf"
fi

function site-packages() {
    # print the path to the site packages from current python environment,
    # e.g. ~/.anaconda3/envs/XXX/lib/python3.6/site-packages/

    python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
    # python -c "import site; print('\n'.join(site.getsitepackages()))"
}

function vimpy() {
    # Open a corresponding file of specified python module.
    # e.g. $ vimpy numpy.core    --> opens $(site-package)/numpy/core/__init__.py
    if [[ -z "$1" ]]; then; echo "Argument required"; return 1; fi

    module_path=$(python -c "import $1; print($1.__file__)")
    if [[ -n "$module_path" ]]; then
      echo $module_path
      vim "$module_path"
    fi
}

# open some macOS applications
if [[ "$(uname)" == "Darwin" ]]; then

    # typora
    function typora   { open -a Typora $@ }

    # skim
    function skim     { open -a Skim $@ }
    compdef '_files -g "*.pdf"' skim

    # terminal-notifier
    function notify   { terminal-notifier -message "$*" }

    # some commands that needs to work correctly in tmux
    if [ -n "$TMUX" ] && (( $+commands[reattach-to-user-namespace] )); then
        alias pngpaste='reattach-to-user-namespace pngpaste'
        alias pbcopy='reattach-to-user-namespace pbcopy'
        alias pbpaste='reattach-to-user-namespace pbpaste'
    fi
fi


# default watch options
alias watch='watch --color -n1'

# nvidia-smi/gpustat every 1 sec
#alias smi='watch -n1 nvidia-smi'
alias watchgpu='watch --color -n0.2 "gpustat --color || gpustat"'
alias smi='watchgpu'

function watchgpucpu {
    watch --color -n0.2 "gpustat --color; echo -n 'CPU '; cpu-usage | ascii-bar;"
}

function usegpu {
    gpu_id="$1"
    if [[ "$1" == "none" ]]; then
        gpu_id=""
    elif [[ "$1" == "auto" ]] && (( $+commands[gpustat] )); then
        gpu_id=$(/usr/bin/python -c 'import gpustat, sys; \
            g = max(gpustat.new_query(), key=lambda g: g.memory_available); \
            g.print_to(sys.stderr); print(g.index)')
    fi
    export CUDA_DEVICE_ORDER=PCI_BUS_ID
    export CUDA_VISIBLE_DEVICES=$gpu_id
}

if (( ! $+commands[tb] )); then
    alias tb='python -m tbtools.tb'
fi

# }}}

# ip
alias ip="dig +short myip.opendns.com @resolver1.opendns.com"
alias localip="ipconfig getifaddr en0"

# foundry
alias ft='forge test'
