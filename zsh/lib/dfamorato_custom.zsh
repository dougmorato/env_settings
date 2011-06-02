#Say how long a commoand took, if it took more than 30 seconds
export REPORTIME=30


# Prompts for confirmation after 'rm *' etc
# Helps avoid mistakes like 'rm * o' when 'rm *.o' was intended
setopt RM_STAR_WAIT

# Background processes aren't killed on exit of shell
setopt AUTO_CONTINUE

# Don’t write over existing files with >, use >! instead
setopt NOCLOBBER

# Don’t nice background processes
setopt NO_BG_NICE

# Watch other user login/out
watch=notme
export LOGCHECK=60

#ssh to my hosts
alias conpika="ssh dfamorato@pika.globalcorphq.com"
alias conpg1="ssh root@pg1.globalcorphq.com"
alias conpg2="ssh root@pg2.globalcorphq.com"
alias conmg1="ssh root@mg1.globalcorphq.com"
alias conmg2="ssh root@mg2.globalcorphq.com"
alias conweb1="ssh root@web1.globalcorphq.com"
alias conweb2="ssh root@web2.globalcorphq.com"
alias concache1="ssh root@cache1.globalcorphq.com"
alias conslave1="ssh root@slave1.globalcorphq.com"
alias conmq1="ssh root@mq1.globalcorphq.com"
alias concorp="ssh root@corp.globalcorphq.com"

#Navigating
alias site="cd ~/Sites"
alias home="cd ~"
alias root="cd /"
alias trunks="cd ~/Development/Trunks"
alias dev="cd ~/Development"
alias apps="cd /Applications/"
alias projects="cd ~/Development/Projects"
