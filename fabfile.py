#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" Fabric Recipes for installing, updating and maintaining OSX/Linux
enviroment customizations such as Vim, Bash, Zsh, Git and Mercurial.

:by Douglas Morato on May 2011.
:copyright: 2011 by Craft.IO @ Miami, Florida, USA.
:license: WTFPL . Check http://en.wikipedia.org/wiki/WTFPL for details.

"""
from fabric.api import run, cd, env
from fabric.contrib.files import exists

def install_vim_customizations():
    "Setup and install vim customizations."
    #Setup basic necessary variables
    user_home_dir = run('echo $HOME')
    with cd(user_home_dir):
        env_settings_dir = str(user_home_dir) + "/.env_settings"
    if not exists(env_settings_dir):
        run('mkdir %s'  % env_settings_dir)

    # Add the vim repositories below
    vim_repositories = [
        "git://github.com/alfredodeza/pytest.vim.git",
        "git://github.com/altercation/vim-colors-solarized.git",
        "git://github.com/fs111/pydoc.vim.git",
        "git://github.com/kevinw/pyflakes-vim.git",
        "git://github.com/mileszs/ack.vim.git",
        "git://github.com/msanders/snipmate.vim.git",
        "git://github.com/scrooloose/nerdcommenter.git",
        "git://github.com/scrooloose/nerdtree.git",
        "git://github.com/sjl/gundo.vim.git",
        "git://github.com/sukima/xmledit",
        "git://github.com/timcharper/textile.vim.git",
        "git://github.com/tomtom/tcomment_vim.git",
        "git://github.com/tpope/vim-cucumber.git",
        "git://github.com/tpope/vim-fugitive.git",
        "git://github.com/tpope/vim-haml.git",
        "git://github.com/tpope/vim-markdown.git",
        "git://github.com/tpope/vim-pastie.git",
        "git://github.com/tpope/vim-rails.git",
        "git://github.com/tpope/vim-repeat.git",
        "git://github.com/tpope/vim-surround.git",
        "git://github.com/tsaleh/vim-align.git",
        "git://github.com/tsaleh/vim-matchit.git",
        "git://github.com/tsaleh/vim-shoulda.git",
        "git://github.com/vim-ruby/vim-ruby.git",
        "git://github.com/vim-scripts/applescript.vim",
        "git://github.com/nvie/vim-pep8.git",
        "git://github.com/vim-scripts/TaskList.vim.git",
        "git://github.com/wincent/Command-T.git",
    ]
    vim_bundle_dir = str(env_settings_dir) + "/vim/bundle/"
    with cd(env_settings_dir):
        run("git init .")
        for repository in vim_repositories:
            repository_list = repository.split('/')
            repository_guess = repository_list[4]
            if 'git' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.git')
                repository_bundle_dir = vim_bundle_dir + repository_dir
                run('git submodule add %s %s' % (repository, repository_bundle_dir))
            elif 'hg' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.hg')
                repository_bundle_dir = str(vim_bundle_dir) + str(repository_dir)
                run('hg clone %s %s' % (repository, repository_bundle_dir))
    run('ln -s %s/vim/vimrc %s/.vimrc' % (env_settings_dir, user_home_dir))

def install_zsh_customizations():
    pass

def install_bash_customizations():
    pass

def install_virtualenv_customizations():
    pass

def install_git_customizations():
    pass

def install_mercurial_customizations():
    pass

def install_vcprompt():
    pass

def customize():
    pass

def update():
    pass

