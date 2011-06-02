## Command history configuration
HISTFILE=$HOME/.zsh_history
HISTSIZE=10000 # Lines to save in memory
SAVEHIST=10000 # Lines to save on disk

# Ignore duplicates in history
setopt hist_ignore_dups # ignore duplication command history list

# share command history data
setopt share_history 

setopt hist_verify


# puts timestamps in the history
setopt extended_history

setopt hist_expire_dups_first

# Don't log commands beginning with a space.
setopt hist_ignore_space

# Append to history on-the-fly
setopt APPEND_HISTORY
setopt inc_append_history


# _all_ zsh sessions share the same history files
setopt SHARE_HISTORY
