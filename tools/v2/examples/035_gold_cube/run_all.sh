#!/bin/bash
# resumable: gold3d skips frames that already exist (sequences); stills are re-rendered only if missing
cd /home/claude/work/035/b3d
B=/home/claude/bpyenv/bin/python; O=final; PR='{"gate_at":8.53,"slab_at":6.15,"res_at":4.45}'; C="--fps 15 --pct 67 --samples 12"
still() { f=$(python3 -c "print(f'{round($3*15):04d}')"); [ -f $O/$1/$f.png ] || $B gold3d.py $1 $2 $O $C --still $3 --params "$PR"; }
$B gold3d.py hook 7.02 $O $C --range 0,2.6 --params "$PR"
still size 11.33 3; still size 11.33 9; still pitch 4.72 2
still 1950 5.76 0.1; still 1950 5.76 3
still grow 10.27 3; still grow 10.27 9.5
$B gold3d.py grow 10.27 $O $C --range 6.15,7.15 --params "$PR"
still reserve 7.48 2
$B gold3d.py reserve 7.48 $O $C --range 4.45,5.85 --params "$PR"
still end 9.53 3
echo ALLDONE
