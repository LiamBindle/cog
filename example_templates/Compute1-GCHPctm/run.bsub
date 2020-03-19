#!/usr/bin/bash
#BSUB -q {{ job['queue'] }}
#BSUB -n {{ job['num_cores'] }}
#BSUB -W 72:00
#BSUB -R "rusage[mem=300000] span[ptile={{ job['cores_per_node'] }}] select[mem < 2000000]"
#BSUB -a 'docker(registry.gsc.wustl.edu/sleong/base-engineering-gcc)'
#BSUB -J "SGV run"
#BSUB -g /$USER/c180e_runs
#BSUB -N
#BSUB -u liam.bindle@wustl.edu
#BSUB -o lsf-run-%J-output.txt

# Source bashrc
. /etc/bashrc

# Set up runtime environment
set -x                           # Print executed commands
set -e                           # Exit immediately if a command fails
ulimit -c 0                      # coredumpsize
ulimit -l unlimited              # memorylocked
ulimit -u 50000                  # maxproc
ulimit -v unlimited              # vmemoryuse
ulimit -s unlimited              # stacksize

# Execute simulation
cd {{ paths['run_directory'] }}
rm -f cap_restart gcchem*
./runConfig.sh
export TMPDIR="$__LSF_JOB_TMPDIR__"
mpirun -x LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH -np {{ job['num_cores'] }} ./geos