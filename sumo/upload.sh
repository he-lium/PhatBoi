scp $1 robot@ev3dev.local:~
filename="${1##*/}"
ssh robot@ev3dev.local 'python $filename'
