#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('''
   @wookayin's              ███████╗██╗██╗     ███████╗███████╗
   ██████╗  █████╗ ████████╗██╔════╝██║██║     ██╔════╝██╔════╝
   ██╔══██╗██╔══██╗╚══██╔══╝█████╗  ██║██║     █████╗  ███████╗
   ██║  ██║██║  ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
   ██████╔╝╚█████╔╝   ██║   ██║     ██║███████╗███████╗███████║
   ╚═════╝  ╚════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝

   https://dotfiles.wook.kr/
''')

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-f', '--force', action="store_true", default=False,
                    help='If set, it will override existing symbolic links')
parser.add_argument('--skip-vimplug', action='store_true',
                    help='If set, do not update vim plugins.')
parser.add_argument('--skip-zgen', '--skip-zplug', action='store_true',
                    help='If set, skip zgen updates.')
parser.add_argument('--enable-coc', action='store_true',
                    help='Install coc.nvim (highly experimental)')

args = parser.parse_args()

################# BEGIN OF FIXME #################

# Task Definition
# (path of target symlink) : (location of source file in the repository)
tasks = {
    # SHELLS
    '~/.bashrc' : 'bashrc',
    '~/.screenrc' : 'screenrc',

    # VIM
    '~/.vimrc' : 'vim/vimrc',
    '~/.vim' : 'vim',
    '~/.vim/autoload/plug.vim' : 'vim/bundle/vim-plug/plug.vim',

    # NeoVIM
    '~/.config/nvim' : 'nvim',

    # GIT
    '~/.gitconfig' : 'git/gitconfig',
    '~/.gitignore' : 'git/gitignore',

    # ZSH
    '~/.zgen'     : 'zsh/zgen',
    '~/.zsh'      : 'zsh',
    '~/.zlogin'   : 'zsh/zlogin',
    '~/.zlogout'  : 'zsh/zlogout',
    '~/.zpreztorc': 'zsh/zpreztorc',
    '~/.zprofile' : 'zsh/zprofile',
    '~/.zshenv'   : 'zsh/zshenv',
    '~/.zshrc'    : 'zsh/zshrc',

    # Bins
    '~/.local/bin/dotfiles' : 'bin/dotfiles',
    '~/.local/bin/fasd' : 'zsh/fasd/fasd',
    '~/.local/bin/is_mosh' : 'zsh/is_mosh/is_mosh',
    '~/.local/bin/fzf' : '~/.fzf/bin/fzf', # fzf is at $HOME/.fzf

    # X
    '~/.Xmodmap' : 'Xmodmap',

    # GTK
    '~/.gtkrc-2.0' : 'gtkrc-2.0',

    # tmux
    '~/.tmux'     : 'tmux',
    '~/.tmux.conf' : 'tmux/tmux.conf',

    # .config (XDG-style)
    '~/.config/terminator' : 'config/terminator',
    '~/.config/pudb/pudb.cfg' : 'config/pudb/pudb.cfg',
    '~/.config/fsh/wook.ini' : 'config/fsh/wook.ini',
    '~/.config/direnv/direnvrc' : 'config/direnv/direnvrc',

    # pip and python
    #'~/.pip/pip.conf' : 'pip/pip.conf',
    '~/.pythonrc.py' : 'python/pythonrc.py',
    '~/.pylintrc' : 'python/pylintrc',
    '~/.condarc' : 'python/condarc',
    '~/.config/pycodestyle' : 'python/pycodestyle',
    '~/.ptpython/config.py' : 'python/ptpython.config.py',
}


from distutils.spawn import find_executable


post_actions = [
    '''#!/bin/bash
    # Check whether ~/.vim and ~/.zsh are well-configured
    for f in ~/.vim ~/.zsh ~/.vimrc ~/.zshrc; do
        if ! readlink $f >/dev/null; then
            echo -e "\033[0;31m\
WARNING: $f is not a symbolic link to ~/.dotfiles.
You may want to remove your local folder (~/.vim) and try again?\033[0m"
            exit 1;
        else
            echo "$f --> $(readlink $f)"
        fi
    done
    ''',

    '''#!/bin/bash
    # Update zgen modules and cache (the init file)
    zsh -c "
        source ${HOME}/.zshrc                   # source zplug and list plugins
        if ! which zgen > /dev/null; then
            echo -e '\033[0;31m\
ERROR: zgen not found. Double check the submodule exists, and you have a valid ~/.zshrc!\033[0m'
            ls -alh ~/.zsh/zgen/
            ls -alh ~/.zshrc
            exit 1;
        fi
        zgen reset
        zgen update
    "
    ''' if not args.skip_zgen else '',

    '''#!/bin/bash
    # validate neovim package installation on python2/3 and automatically install if missing
    source "etc/install-neovim-py.sh"
    ''',

    # Run vim-plug installation
    {'install' : '{vim} +PlugInstall +qall'.format(vim='nvim' if find_executable('nvim') else 'vim'),
     'update'  : '{vim} +PlugUpdate  +qall'.format(vim='nvim' if find_executable('nvim') else 'vim'),
     'none'    : ''}['update' if not args.skip_vimplug else 'none'],

    # Install tmux plugins via tpm
    '~/.tmux/plugins/tpm/bin/install_plugins',

    r'''#!/bin/bash
    # Check tmux version >= 2.3 (or use `dotfiles install tmux`)
    _version_check() {    # target_ver current_ver
        [ "$1" = "$(echo -e "$1\n$2" | sort -s -t- -k 2,2n | sort -t. -s -k 1,1n -k 2,2n | head -n1)" ]
    }
    if ! _version_check "2.3" "$(tmux -V | cut -d' ' -f2)"; then
        echo -en "\033[0;33m"
        echo -e "$(tmux -V) is too old. Contact system administrator, or:"
        echo -e "  $ dotfiles install tmux  \033[0m (installs to ~/.local/, if you don't have sudo)"
        exit 1;
    else
        echo "$(which tmux): $(tmux -V)"
    fi
    ''',

    r'''#!/bin/bash
    # create directory ~/.config/coc if not exists
    coc_dir="$HOME/.config/coc/"
    if [ ! -d "$coc_dir" ]; then
        mkdir -p "$coc_dir" || exit 1;
        echo "Created: $coc_dir"
    fi
    ''' if args.enable_coc else ''

    r'''#!/bin/bash
    # Change default shell to zsh
    /bin/zsh --version >/dev/null || (echo -e "Error: /bin/zsh not found. Please install zsh"; exit 1)
    if [[ ! "$SHELL" = *zsh ]]; then
        echo -e '\033[0;33mPlease type your password if you wish to change the default shell to ZSH\e[m'
        chsh -s /bin/zsh && echo -e 'Successfully changed the default shell, please re-login'
    else
        echo -e "\033[0;32m\$SHELL is already zsh.\033[0m $(zsh --version)"
    fi
    ''',

    r'''#!/bin/bash
    # Create ~/.gitconfig.secret file and check user configuration
    if [ ! -f ~/.gitconfig.secret ]; then
        cat > ~/.gitconfig.secret <<EOL
# vim: set ft=gitconfig:
EOL
    fi
    if ! git config --file ~/.gitconfig.secret user.name 2>&1 > /dev/null || \
       ! git config --file ~/.gitconfig.secret user.email 2>&1 > /dev/null; then echo -ne '
    \033[1;33m[!!!] Please configure git user name and email:
        git config --file ~/.gitconfig.secret user.name "(YOUR NAME)"
        git config --file ~/.gitconfig.secret user.email "(YOUR EMAIL)"
\033[0m'
        echo -en '\n'
        echo -en "(git config user.name) \033[0;33m Please input your name  : \033[0m"; read git_username
        echo -en "(git config user.email)\033[0;33m Please input your email : \033[0m"; read git_useremail
        if [[ -n "$git_username" ]] && [[ -n "$git_useremail" ]]; then
            git config --file ~/.gitconfig.secret user.name "$git_username"
            git config --file ~/.gitconfig.secret user.email "$git_useremail"
        else
            exit 1;   # error
        fi
    fi

    # get the current config
    echo -en '\033[0;32m';
    echo -en 'user.name  : '; git config --file ~/.gitconfig.secret user.name
    echo -en 'user.email : '; git config --file ~/.gitconfig.secret user.email
    echo -en '\033[0m';
    ''',
]

################# END OF FIXME #################

def _wrap_colors(ansicode):
    return (lambda msg: ansicode + str(msg) + '\033[0m')
GRAY   = _wrap_colors("\033[0;37m")
WHITE  = _wrap_colors("\033[1;37m")
RED    = _wrap_colors("\033[0;31m")
GREEN  = _wrap_colors("\033[0;32m")
YELLOW = _wrap_colors("\033[0;33m")
CYAN   = _wrap_colors("\033[0;36m")
BLUE   = _wrap_colors("\033[0;34m")


import os
import sys
import subprocess

if sys.version_info[0] >= 3:  # python3
    from builtins import input
    unicode = lambda s, _: str(s)
else:
    input = raw_input         # python2

from signal import signal, SIGPIPE, SIG_DFL
from optparse import OptionParser
from sys import stderr

def log(msg, cr=True):
    stderr.write(msg)
    if cr:
        stderr.write('\n')

def log_boxed(msg, color_fn=WHITE, use_bold=False, len_adjust=0):
    import unicodedata
    pad_msg = (" " + msg + "  ")
    l = sum(not unicodedata.combining(ch) for ch in unicode(pad_msg, 'utf-8')) + len_adjust
    if use_bold:
        log(color_fn("┏" + ("━" * l) + "┓\n" +
                     "┃" + pad_msg   + "┃\n" +
                     "┗" + ("━" * l) + "┛\n"), cr=False)
    else:
        log(color_fn("┌" + ("─" * l) + "┐\n" +
                     "│" + pad_msg   + "│\n" +
                     "└" + ("─" * l) + "┘\n"), cr=False)


# get current directory (absolute path)
current_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(current_dir)

# check if git submodules are loaded properly
stat = subprocess.check_output("git submodule status --recursive",
                               shell=True, universal_newlines=True)
submodule_issues = [(l.split()[1], l[0]) for l in stat.split('\n') if len(l) and l[0] != ' ']

if submodule_issues:
    stat_messages = {'+': 'needs update', '-': 'not initialized', 'U': 'conflict!'}
    for (submodule_name, submodule_stat) in submodule_issues:
        log(RED("git submodule {name} : {status}".format(
            name=submodule_name,
            status=stat_messages.get(submodule_stat, '(Unknown)'))))
    log(RED(" you may run: $ git submodule update --init --recursive"))

    log("")
    log(YELLOW("Do you want to update submodules? (y/n) "), cr=False)
    shall_we = (input().lower() == 'y')
    if shall_we:
        git_submodule_update_cmd = 'git submodule update --init --recursive'
        # git 2.8+ supports parallel submodule fetching
        try:
            git_version = str(subprocess.check_output("""git --version | awk '{print $3}'""", shell=True))
            if git_version >= '2.8': git_submodule_update_cmd += ' --jobs 8'
        except Exception as e:
            pass
        log("Running: %s" % BLUE(git_submodule_update_cmd))
        subprocess.call(git_submodule_update_cmd, shell=True)
    else:
        log(RED("Aborted."))
        sys.exit(1)


log_boxed("Creating symbolic links", color_fn=CYAN)
for target, source in sorted(tasks.items()):
    # normalize paths
    source = os.path.join(current_dir, os.path.expanduser(source))
    target = os.path.expanduser(target)

    # bad entry if source does not exists...
    if not os.path.lexists(source):
        log(RED("source %s : does not exist" % source))
        continue

    # if --force option is given, delete and override the previous symlink
    if os.path.lexists(target):
        is_broken_link = os.path.islink(target) and not os.path.exists(os.readlink(target))

        if args.force or is_broken_link:
            if os.path.islink(target):
                os.unlink(target)
            else:
                log("{:50s} : {}".format(
                    BLUE(target),
                    YELLOW("already exists but not a symbolic link; --force option ignored")
                ))
        else:
            log("{:50s} : {}".format(
                BLUE(target),
                GRAY("already exists, skipped") if os.path.islink(target) \
                    else YELLOW("exists, but not a symbolic link. Check by yourself!!")
            ))

    # make a symbolic link if available
    if not os.path.lexists(target):
        try:
            mkdir_target = os.path.split(target)[0]
            os.makedirs(mkdir_target)
            log(GREEN('Created directory : %s' % mkdir_target))
        except:
            pass
        os.symlink(source, target)
        log("{:50s} : {}".format(
            BLUE(target),
            GREEN("symlink created from '%s'" % source)
        ))

errors = []
for action in post_actions:
    if not action:
        continue

    action_title = action.strip().split('\n')[0].strip()
    if action_title == '#!/bin/bash': action_title = action.strip().split('\n')[1].strip()

    log("\n", cr=False)
    log_boxed("Executing: " + action_title, color_fn=CYAN)
    ret = subprocess.call(['bash', '-c', action],
                          preexec_fn=lambda: signal(SIGPIPE, SIG_DFL))

    if ret:
        errors.append(action_title)

log("\n")
if errors:
    log_boxed("You have %3d warnings or errors -- check the logs!" % len(errors),
              color_fn=YELLOW, use_bold=True)
    for e in errors:
        log("   " + YELLOW(e))
    log("\n")
else:
    log_boxed("✔︎  You are all set! ", len_adjust=-1,
              color_fn=GREEN, use_bold=True)

log("- Please restart shell (e.g. " + CYAN("`exec zsh`") + ") if necessary.")
log("- To install some packages locally (e.g. neovim, tmux), try " + CYAN("`dotfiles install <package>`"))
log("- If you want to update dotfiles (or have any errors), try " + CYAN("`dotfiles update`"))
log("\n\n", cr=False)
