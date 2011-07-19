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
    # Add the vim repositories of the bundles you want to install
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
        "git://github.com/tomtom/tlib_vim.git",
        "git://github.com/MarcWeber/vim-addon-mw-utils.git",
        "git://github.com/spf13/snipmate.vim.git",
        "git://github.com/spf13/snipmate-snippets.git",
        "git://github.com/flazz/vim-colorschemes.git",
        ]

    #Bundle installation method
    vim_bundle_dir = env_settings_dir + "/vim/bundle/"
    with cd(env_settings_dir):
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

        # check and delete if vimrc exists
            if exists("%s/.vimrc" % user_home_dir):
                run("rm -f %s/.vimrc" % user_home_dir)
        # Let's lake a symbolic link of the vim_redirector
        run('ln -s %s/vim/vimrc_redirector %s/.vimrc' %
                            (env_settings_dir, user_home_dir))
    # Hack to make snipmate work
    run('ln -s %ssnipmate-snippets %s/vim/snippets' %
                            (vim_bundle_dir, env_settings_dir))
    #install the vim colorschemes
    if not exists("%s/vim/colors" % env_settings_dir):
        run("mkdir ~/.env_settings/vim/colors")
    with cd("%s/vim/bundle/vim-colorschemes" % env_settings_dir):
        run("cp -fa ./* %s/.env_settings/vim/colors" % user_home_dir)

    #install dfamorato vim colorscheme
    with cd("/tmp"):
        run("git clone git://gist.github.com/1093923.git dfamorato-vim")
        run("cp -f ./dfamorato-vim/dfamorato.vim %s/.env_settings/vim/colors" %
        user_home_dir)
        run("rm -rf /tmp/dfamorato-vim")

    #install Command-T with rake extension because we need to
    command_t_dir = vim_bundle_dir + "Command-T/"
    with cd(command_t_dir):
        sudo('rake make')

def _install_zsh_customizations(env_settings_dir, user_home_dir):
    '''Install "oh my zsh"'''
    with cd(env_settings_dir):
        run("git submodule add git://github.com/dfamorato/oh-my-zsh.git"
                " ./zsh/oh-my-zsh")

        #check and delete if zshrc exists
        if exists("%s/.zshrc" % user_home_dir):
            run("rm -f %s/.zsh*" % user_home_dir)
        run("ln -s %s/zsh/oh-my-zsh/templates/dfamorato-zshrc  %s/.zshrc" %
                (env_settings_dir,user_home_dir))
        run('export PATH=$PATH >> %s/.zshrc' % user_home_dir)
        sudo("chsh -s /bin/zsh")

def _install_virtualenv_customizations():
    '''Install virtualenv and virtualenv wrappers'''
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')

def _install_git_customizations(env_settings_dir, user_home_dir):
    """Links the gitconfig and gitignore file"""
    #check and delete if git config files exist
    if exists("%s/.gitconfig" % user_home_dir):
        run("rm -f %s/.gitconfig "% user_home_dir)
    if exists("%s/.gitignore_global" % user_home_dir):
        run("rm -f %s/.gitignore_global" % user_home_dir)

    #Link git config files from repo
    run("ln -s %s/git/gitconfig %s/.gitconfig" % (env_settings_dir,
        user_home_dir))
    run("ln -s %s/git/gitignore_global %s/.gitignore_global" %
            (env_settings_dir, user_home_dir))

def _install_mercurial_customizations(env_settings_dir, user_home_dir):
    ''' Install mercurial customizations and extensions'''
    with cd(env_settings_dir +"/mercurial" ):
        run("hg clone https://dfamorato@bitbucket.org/sjl/hg-prompt")
        if exists ("%s/.hgrc" % user_home_dir):
            run("rm -f %s/.hgrc" % user_home_dir)
        run("ln -s %s/mercurial/hgrc %s/.hgrc" % (env_settings_dir,
            user_home_dir))

def customize():
    target_os = prompt("What is the OS you are deploying to: mac or linux: ")
    if target_os in ("LINUX", "linux"):
        sudo("apt-get update")
        sudo("apt-get install -y rake ruby-dev vim-nox")
        sudo("apt-get install -y python-pip python-dev build-essential")
        sudo("apt-get install -y byobu zsh git-core mercurial")
    else:
        #TODO: what are the requirements to install on a mac ??
        pass

    # let's find out what is the users home directory
    user_home_dir = run('echo $HOME')

    #Create the $HOME/Development/Projects directory if non existant
    if not exists(user_home_dir + "/Development"):
        run("mkdir ~/Development")
    if not exists(user_home_dir + "/Development/Projects"):
        run("mkdir ~/Development/Projects")

    #delete .env_settings dir if exists
    if exists("%s/.env_settings" % user_home_dir):
        run("rm -rf %s/.env_settings" % user_home_dir)
    #TODO: Prompt user for his fork of the env_settings project
    #Clone base settings from github
    with cd(user_home_dir):
        run('git clone git://github.com/dfamorato/env_settings.git .env_settings')
    env_settings_dir = user_home_dir + "/.env_settings"

    #Add git upstream server for future updates on this project
    with cd(env_settings_dir):
        run("git remote add upstream git://github.com/dfamorato/env_settings.git")

    #start to install customizations
    _install_vim_customizations(env_settings_dir, user_home_dir)
    _install_zsh_customizations(env_settings_dir, user_home_dir)
    _install_git_customizations(env_settings_dir, user_home_dir)
    _install_mercurial_customizations(env_settings_dir, user_home_dir)
    _install_virtualenv_customizations()

def update():
    pass
