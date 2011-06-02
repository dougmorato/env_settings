# Push and pop directories on directory stack
alias pu='pushd'
alias po='popd'

# Super user
alias _='sudo'

#alias g='grep -in'

# Show history
alias history='fc -l 1'

alias afind='ack-grep -il'

alias x=extract

#terminal
alias lc="ls -laGph"
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Play safe!
alias 'rm=rm -i'
alias 'mv=mv -i'
alias 'cp=cp -i'

# Typing errors...
alias 'cd..=cd ..'

# Quick find
f() {
    echo "find . -iname \"*$1*\""
    find . -iname "*$1*"
}