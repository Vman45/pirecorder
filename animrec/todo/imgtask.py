# !/usr/bin/python

# import packages
from time import strftime
import crontab
import datetime
import os

# define plan function
def plan(imgwait=5.0,
         imgnr=100,
         imgtime=600,
         taskname="molly",
         taskcode="0 7 * * *",
         taskset="True",
         taskshow="False"):

    """
    Run automated image recording with the rpi camera

    Storage location
    ----------
    The folder where the images will be stored is automatically
    set to the folder on the server that reflects the rpi name,
    and within that a folder of the date, for example
    /home/pi/SERVER/pi41/171204.

    Parameters
    ----------
    imgwait : float, default = 5.0
        The delay between subsequent images in seconds. When a
        delay is provided that is less than shutterspeed +
        processingtime, "delay" will be automatically set to 0
        and images thus taken one after the other.
    imgnr : integer, default = 100
        The number of images that will be taken. When this number
        is reached, the script will automatically terminate. The
        minimum of imgnr and nr of images based on imgwait and
        imgtime will be selected.
    imgtime : integer, default = 600
        The time in seconds during which images should be taken.
        The minimum of imgnr and nr of images based on imgwait
        and imgtime will be selected.
    taskname : str, default = "molly"
        The name for the timing task. This parameter only really
        needs to be set when wanting to run multiple different
        tasks.
    taskcode : string, default = "0 7 * * *"
        The taskcode representing the schedule for the image script
        to be executed, based on CRON scheduling. The parts it
        should contain are as follows:
        * * * * *
        - - - - -
        | | | | |
        | | | | +----- day of week (0 - 7) (Sunday=0 or 7)
        | | | +---------- month (1 - 12)
        | | +--------------- day of month (1 - 31)
        | +-------------------- hour (0 - 23)
        +------------------------- min (0 - 59)
        Each of the parts supports wildcards (*), ranges (2-5),
        and lists (2,5,6,11). For example, if you want to run the
        img recording script at 22:00 on every day of the week
        from Monday through Friday: 0 7 (2,5) * *
    taskset : str, default = "True"
        If the timing task should be enabled ("True") or disabled
        ("False")
    taskshow : str, default = "False"
        If the different timed tasks should be shown ("True") or
        not ("False")

    Output
    -------
    A scheduled task to run automated SESSIONS during which a
    series of controlled JPEG images are recorded for a certain
    duration and delay. Images are automatically named based on
    the rpi number, date, and time, following a standard naming
    convention, e.g. pi11_172511_im00010_153012.jpg

    """

    # create access to the system crontab of pi
    cron = crontab.CronTab(user='pi')

    # set-up storing of logfiles
    logfolder = "/home/pi/SERVER/imglogs/"
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)

    # define crontab job command
    exe = "/usr/local/bin/runp"
    scriptloc = " /home/pi/AnimRec/imgrec.py"
    fcode = " record:imgwait="+str(imgwait)+",imgnr="+str(imgnr)+",imgtime="+str(imgtime)
    write = " >> /home/pi/SERVER/imglogs/`date +\%y\%m\%d`_$HOSTNAME.log 2>&1"
    taskcommand = exe+scriptloc+fcode+write

    # create job functions
    def enablejob(job):
        if taskset == "True":
            job.enable()
        elif taskset == "False":
            job.enable(False)
        else:
            print "Please provide 'True' or 'False' for parameter enable"

    def createjob():
        job = cron.new(command=taskcommand,comment=taskname)
        job.setall(taskcode)
        enablejob(job)
        cron.write()
        print "\n"+taskname+ " recording job created succesfully"

    def modifyjob():
        if taskset == "True":
            if job.command != taskcommand:
                job.command = taskcommand
            job.setall(taskcode)
        enablejob(job)
        cron.write()
        print "\n"+taskname+" recording job modified successfully"

    # check if already jobs exist; if not create job
    if len(cron) == 0:
        createjob()

    # there are jobs so check if specific job exists
    else:
        for i, job in enumerate(cron):

            # a job with specific name exists, so modify
            if job.comment == taskname:
                modifyjob()
                break

            # the specific job does not exist so create it
            if len(cron) == (i+1):
                createjob()

    # print crontab schedule
    if taskshow == "True":
        print "\nCurrent task schedule:"

        # get length of maximum crontab name
        maxlen = 8
        for job in cron:
            maxlen = len(job) if (len(job)>maxlen and len(job)<30) else maxlen

        # now show last and next job
        for job in cron:
            sch = job.schedule(date_from=datetime.datetime.now())
            next = sch.get_next()
            jobname = job.comment
            jobname = jobname+" "*(maxlen-len(jobname))
            if job.is_enabled():
                print jobname+" next job: "+str(next)
            else:
                print jobname+" disabled"