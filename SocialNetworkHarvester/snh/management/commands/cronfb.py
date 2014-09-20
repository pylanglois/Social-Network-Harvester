# coding=UTF-8

from tendo import singleton

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from snh.management.commands.cronharvester import facebookch

import snhlogger
logger = snhlogger.init_logger(__name__, "facebook.log")

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    #help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        me = singleton.SingleInstance(flavor_id="cronfb")

        try:
            logger.info("Will run the Facebook harvesters.")
            facebookch.run_facebook_harvester()
        except:
            msg = u"Highest exception for the facebook cron. Not good."
            logger.exception(msg)

        logger.info("The harvest has end for the Facebook harvesters.")



        
