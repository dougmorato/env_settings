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

def _install_vim_customizations(env_settings_dir, user_home_dir):
    "Setup and install vim customizations."
    # Add the vim repositories below
    vim_repositories = [
        "git://github.com/alfredodeza/pytest.vim.git",
        "git://github.com/altercation/vim-colors-solarized.git",
        "git://github.com/fs111/pydoc.vim.git",
        "git://github.com/kevinw/pyflakes-vim.git",
        "git://github.com/mileszs/ack.vim.git",
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
        "git://github.com/spf13/PIV.git",
        "git://github.com/ervandew/supertab.git",
        "git://github.com/Raimondi/delimitMate.git",
        "git://github.com/vim-scripts/matchit.zip.git",
        "git://github.com/tomtom/checksyntax_vim.git",
        "git://github.com/spf13/vim-easytags.git",
        "git://github.com/tomtom/tlib_vim.git",
        "git://github.com/MarcWeber/vim-addon-mw-utils.git",
        "git://github.com/spf13/snipmate.vim.git",
        "git://github.com/spf13/snipmate-snippets.git"
        ]

    vim_bundle_dir = env_settings_dir + "/vim/bundle/"
    with cd(env_settings_dir):
        run("git init .")
        for repository in vim_repositories:
            repository_list = repository.split('/')
            repository_guess = repository_list[4]
            if 'git' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.git')
                repository_bundle_dir = vim_bundle_dir + repository_dir
                run('git submodule add %s %s' %
                            (repository, repository_bundle_dir))
            elif 'hg' in repository_list[0]:
                repository_dir = repository_guess.rstrip('.hg')
                repository_bundle_dir = vim_bundle_dir + repository_dir
                run('hg clone %s %s' % (repository, repository_bundle_dir))
        #FUCKING HACK TO MAKE FUCKING PYFLAKES WORK
        run("git submodule add git://github.com/kevinw/pyflakes.git"
                " %s/vim/ftplugin/python/pyflakes" % env_settings_dir)
        with cd("%s/vim/ftplugin/python/pyflakes" % env_settings_dir):
            run("python setup.py install")
        run('ln -s %s/vim/vimrc_redirector %s/.vimrc' %
                            (env_settings_dir, user_home_dir))
    run('ln -s %ssnipmate-snippets %s/vim/snippets' %
                            (vim_bundle_dir, env_settings_dir))

    #install Command-T with rake extension because we need to
    command_t_dir = vim_bundle_dir + "Command-T/"
    with cd(command_t_dir):
        run('rake make')

def _install_zsh_customizations():
    pass

def _install_bash_customizations():
    pass

def _install_virtualenv_customizations():
    pass

def _install_git_customizations():
    pass

def _install_mercurial_customizations():
    pass

def _install_vcprompt():
    pass

def customize():
    target_os = prompt("What is the OS you are deploying to: mac or linux: ")
    if "LINUX" or "linux" in target_os:
        run("aptitude update")
        run("aptitude install -y rake ruby-dev")
        run("aptitude install -y python-pip python-dev build-essential")
        run("aptitude install -y git-core mercurial exuberant-ctags")
        run("pip install ipython")

    else:
        sudo("brew install exuberant-ctags")
        run("pip install ipython")

    #clone base settings from github
    with cd("/tmp"):
        run('git clone git://github.com/dfamorato/env_settings.git')

    #Setup basic necessary variables
    user_home_dir = run('echo $HOME')
    env_settings_dir = user_home_dir + "/.env_settings"
    if not exists(env_settings_dir):
            run('mkdir %s'  % env_settings_dir)
    #move data from cloned git repo to permanent directory
    run('mv -f /tmp/env_settings/* %s/' % env_settings_dir)
    run('rm -rf /tmp/env_settings')

    #start to install customizations
    _install_vim_customizations(env_settings_dir, user_home_dir)

def update():
    pass

