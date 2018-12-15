# declare a name for this job to be sample_job
#PBS -N methyl_cpu
# Specify the gpuq queue
#PBS -q default
# Specify the number of gpus
#PBS -l nodes=1:ppn=10
# Specify the gpu feature
#PBS -l mem=40GB
# request 4 hours and 30 minutes of cpu time
#PBS -l walltime=04:00:00
# mail is sent to you when the job starts and when it terminates or aborts
#PBS -m bea
# specify your email address
#PBS -M joshua.j.levy.gr@dartmouth.edu
# Join error and standard output into one file
#PBS -j oe
# By default, PBS scripts execute in your home directory, not the
# directory from which they were submitted. The following line
# places you in the directory from which the job was submitted.
cd $PBS_O_WORKDIR
# run the program
module load python/3-Anaconda
source activate py36
python embedding.py perform_embedding -n 300 -hlt 500 -kl 15 -b 4. -s warm_restarts -lr 1e-4 -bce -e 140
exit 0