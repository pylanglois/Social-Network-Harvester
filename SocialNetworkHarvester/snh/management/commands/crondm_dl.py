# coding=UTF-8

import os
import subprocess
from tendo import singleton

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from snh.models.dailymotionmodel import *
from settings import MEDIA_ROOT

import snhlogger
logger = snhlogger.init_logger(__name__, "dailymotion_downloader.log")

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    #help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        me = singleton.SingleInstance(flavor_id="crondm_dl")

        try:
            logger.info("Will run the dailymotion video downloader.")

            videos = DMVideo.objects.all()
            for vid in videos:
                logger.info("Video: %s" % vid.url)
                logger.info("User: %s" % vid.user)
                userfid = vid.user.fid
                if vid.video_file_path is None:
                    try:
                        logger.info("will extract: %s" % vid.url)
                        filename = subprocess.check_output(["youtube-dl","-odailymotion_%s_%s" % (userfid, "%(id)s.%(ext)s"), "--get-filename", "%s" % vid.url])
                        filepath = os.path.join(MEDIA_ROOT,filename.strip("\n"))
                        output = subprocess.check_output(["youtube-dl","-o%s" % filepath, "%s" % vid.url])
                        vid.video_file_path = filepath
                        vid.save()
                    except TypeError:
                        logger.exception("TypeError! %s" % vid if vid else "None")
                    except subprocess.CalledProcessError:
                        logger.exception(u"cannot download video %s for user %s" % (vid.fid, vid.user))

        except:
            msg = u"Highest exception for the dailymotion video downloader cron. Not good."
            logger.exception(msg)

        logger.info("The harvest has end for the dailymotion video downloader.")



        
