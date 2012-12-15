#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" Fabric Recipes for installing, updating and maintaining OSX/Linux
enviroment customizations such as Vim, Bash, Zsh, Git and Mercurial.

:by Douglas Morato on May 2011.
:copyright: 2011 by Craft.IO @ Miami, Florida, USA.
:license: WTFPL . Check http://en.wikipedia.org/wiki/WTFPL for details.

"""
from fabric.api import run, cd, prompt, sudo
from fabric.contrib.files import exists

pip_packages = [
    "virtualenv",
    "virtualenvwrapper",
    "flake8",
]

vim_repositories = [
    "git://github.com/alfredodeza/pytest.vim.git",
    "git://github.com/ap/vim-css-color.git",
    "git://github.com/mileszs/ack.vim.git",
    "git://github.com/majutsushi/tagbar.git",
    "git://github.com/scrooloose/nerdtree.git",
    "git://github.com/scrooloose/syntastic.git",
    "git://github.com/sjl/gundo.vim.git",
    "git://github.com/sjl/threesome.vim.git",
    "git://github.com/tomtom/tcomment_vim.git",
    "git://github.com/tpope/vim-cucumber.git",
    "git://github.com/tpope/vim-fugitive.git",
    "git://github.com/tpope/vim-haml.git",
    "git://github.com/tpope/vim-markdown.git",
    "git://github.com/tpope/vim-pastie.git",
    "git://github.com/tpope/vim-rails.git",
    "git://github.com/tpope/vim-repeat.git",
    "git://github.com/tpope/vim-surround.git",
    "git://github.com/tpope/vim-git.git",
    "git://github.com/vim-ruby/vim-ruby.git",
    "git://github.com/nvie/vim-flake8.git",
    "git://github.com/spf13/PIV.git",
    "git://github.com/ervandew/supertab.git",
    "git://github.com/spf13/snipmate.vim.git",
    "git://github.com/Lokaltog/vim-powerline.git",
    "git://github.com/kien/rainbow_parentheses.vim.git",
    "git://github.com/pangloss/vim-javascript.git",
    "git://github.com/ajf/puppet-vim.git",
    "git://github.com/rosstimson/scala-vim-support.git",
    "git://github.com/kchmck/vim-coffee-script.git",
    "git://github.com/vim-scripts/csv.vim.git",
    "git://github.com/mmalecki/vim-node.js.git",
    "git://github.com/vim-scripts/Arduino-syntax-file.git",
    "git://github.com/vim-scripts/VimClojure.git",
    "git://github.com/groenewege/vim-less.git",
    "git://github.com/tpope/vim-endwise.git",
    "git://github.com/mattn/webapi-vim.git",
    "git://github.com/mattn/gist-vim.git",
    "git://github.com/kien/ctrlp.vim.git",
    "git://github.com/tomtom/tlib_vim.git",
    "git://github.com/MarcWeber/vim-addon-mw-utils.git",
    "git://github.com/garbas/vim-snipmate.git",
    "git://github.com/honza/snipmate-snippets.git",
]

dotfiles_list = [
    "ackrc",
    "bash_profile",
    "bashrc",
    "gemrc",
    "gitconfig",
    "gitignore_global",
    "hgignore_global",
    "hgrc",
    "irbrc",
    "tmux.conf",
    "vimrc",
    "zshrc",
]

brew_packages = [
    "autojump",
    "bash",
    "bash-completion",
    "macvim --override-system-vim",
    "reattach-to-user-namespace",
    "ack",
    "tmux",
    "tree",
    "rbenv",
    "ruby-build",
    "wget",
    "ctags"
]


def _install_vim_customizations(env_settings_dir, user_home_dir):
    "Setup and install vim customizations."
    # Add the vim repositories of the bundles you want to install

    #Bundle installation method
    vim_bundle_dir = env_settings_dir + "/vim/bundle/"
    with cd(env_settings_dir):
        for repository in vim_repositories:
            repository_list = repository.split('/')
            repository_guess = repository_list[4]
            if 'git' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.git')
                repository_bundle_dir = vim_bundle_dir + repository_dir
                run('git submodule add -f %s %s' %
                    (repository, repository_bundle_dir))
            elif 'hg' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.hg')
                repository_bundle_dir = vim_bundle_dir + repository_dir
                run('hg clone %s %s' % (repository, repository_bundle_dir))

        #install the vim colorschemes
        run("git submodule add -f "
            "git://github.com/dfamorato/vim-colorschemes.git"
            " %s/vim/bundle/colorscheme" % env_settings_dir)


def _install_zsh_customizations(env_settings_dir, user_home_dir):
    '''Install "oh my zsh"'''
    with cd(env_settings_dir):
        run("git submodule add -f git://github.com/robbyrussell/oh-my-zsh.git"
            " ./oh-my-zsh")
        run("ln -s ./dotfiles/dfamorato.zsh-theme"
            "./oh-my-zsh/themes/dfamorato.zsh-theme")


def _install_dotfiles_customizations(env_settings_dir, user_home_dir):
    ''' Install additional dotfiles customizations'''

    #Directory that contains the dotfiles
    dotfiles_conf_dir = env_settings_dir + "/dotfiles"

    #Check if dotfile exist, delete it and create new simlynks
    with cd(user_home_dir):
        for dotfile in dotfiles_list:
            if exists(".%s" % dotfile):
                run("rm -f %s*" % dotfile)
            run("ln -s %s/%s  .%s" % (dotfiles_conf_dir, dotfile, dotfile))


def _install_tmux_customization(env_settings_dir, user_home_dir):
    '''Install Tmux customization'''
    tmux_conf_dir = env_settings_dir + "/tmux/tmux-powerline"

    # Pull tmux configurations from github repo
    with cd(env_settings_dir):
        run("git submodule add -f "
            "git://github.com/dfamorato/tmux-powerline.git %s" % tmux_conf_dir)


def customize():
    target_os = prompt("What is the OS you are deploying to: mac, ubuntu or "
                       "fedora: ")
    if target_os in ("ubuntu", "UBUNTU"):
        sudo("apt-get update")
        sudo("apt-get install -y rake ruby-dev vim-nox")
        sudo("apt-get install -y python-pip python-dev build-essential")
        sudo("apt-get install -y tmux zsh git-core mercurial")

    elif target_os in ("mac", "MAC", "Mac"):
        #Install homebrew packages if it's  mac
        #for package in brew_packages:
        #    run("brew install %s" % package)
        pass

    #Install all pip packages necessary
    for package in pip_packages:
        sudo("pip install %s" % package)

    # let's find out what is the users home directory
    user_home_dir = run('echo $HOME')

    #delete .env_settings dir and ofther .files if they exist
    if exists("%s/.env_settings" % user_home_dir):
        sudo("rm -rf %s/.env_settings" % user_home_dir)
        with cd(user_home_dir):
            run("rm -rf .zsh* .zcom* .git* .hg* .vim* .profile* .bash* .tmux* \
                    .ackrc* .gemrc* .irbrc* .tmux*")

    #TODO: Prompt user for his fork of the env_settings project
    #Clone base settings from github
    with cd(user_home_dir):
        run("git clone git://github.com/dfamorato/env_settings.git "
            ".env_settings")
    env_settings_dir = user_home_dir + "/.env_settings"

    #Add git upstream server for future updates on this project
    with cd(env_settings_dir):
        run("git remote add upstream "
            "git://github.com/dfamorato/env_settings.git")

    #start to install customizations
    _install_vim_customizations(env_settings_dir, user_home_dir)
    _install_zsh_customizations(env_settings_dir, user_home_dir)
    _install_dotfiles_customizations(env_settings_dir, user_home_dir)
    _install_tmux_customization(env_settings_dir, user_home_dir)
