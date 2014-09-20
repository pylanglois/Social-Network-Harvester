# coding=UTF-8

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django import template
from django.template.defaultfilters import stringfilter

from fandjango.decorators import facebook_authorization_required
from fandjango.models import User as FanUser

import gviz_api
import datetime as dt
from django.http import HttpResponse

from snh.models.twittermodel import *
from snh.models.facebookmodel import *
from snh.models.youtubemodel import *
from snh.models.dailymotionmodel import *

from snh.utils import get_datatables_records

from settings import PROJECT_PATH

import snhlogger
logger = snhlogger.init_logger(__name__, "view.log")

#
# DAILYMOTION
#
@login_required(login_url=u'/login/')
def dm(request, harvester_id):
    dailymotion_harvesters = DailyMotionHarvester.objects.all()
    return  render_to_response(u'snh/dailymotion.html',{
                                                    u'dm_selected':True,
                                                    u'all_harvesters':dailymotion_harvesters,
                                                    u'harvester_id':harvester_id,
                                                  })

@login_required(login_url=u'/login/')
def dm_user_detail(request, harvester_id, userfid):
    dailymotion_harvesters = DailyMotionHarvester.objects.all()
    user = get_list_or_404(DMUser, fid=userfid)[0]
    return  render_to_response(u'snh/dailymotion_detail.html',{
                                                    u'dm_selected':True,
                                                    u'all_harvesters':dailymotion_harvesters,
                                                    u'harvester_id':harvester_id,
                                                    u'user':user,
                                                  })
@login_required(login_url=u'/login/')
def dm_video_detail(request, harvester_id, videoid):
    dailymotion_harvesters = DailyMotionHarvester.objects.all()
    video = get_object_or_404(DMVideo, fid=videoid)
    video_url = ""
    if video.video_file_path:
        path_split = video.video_file_path.split(PROJECT_PATH)
        if len(path_split) > 1:
            video_url = path_split[1]

    return  render_to_response(u'snh/dailymotion_video.html',{
                                                    u'dm_selected':True,
                                                    u'all_harvesters':dailymotion_harvesters,
                                                    u'harvester_id':harvester_id,
                                                    u'user':video.user,
                                                    u'video':video,
                                                    u'video_url':video_url,
                                                  })

#
# DailyMotion AJAX
#
@login_required(login_url=u'/login/')
def get_dm_list(request, call_type, harvester_id):
    querySet = None

    if harvester_id == "0":
        querySet = DMUser.objects.all()
    else:
        harvester = DailyMotionHarvester.objects.get(pmk_id__exact=harvester_id)
        querySet = harvester.dmusers_to_harvest.all()

    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {
                            0 : u'fid',
                            1 : u'username',
                            2 : u'screenname',
                            3 : u'gender',
                            4 : u'description',
                            5 : u'language',
                            6 : u'status',
                            7 : u'ftype',
                            8 : u'url__original_url',
                            9 : u'views_total',
                            10 : u'videos_total',


                            }
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dm_video_list(request, call_type, userfid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior

    columnIndexNameMap = {
                            0 : u'created_time',
                            1 : u'fid',
                            2 : u'title',
                            3 : u'description',
                            4 : u'language',
                            5 : u'country',
                            6 : u'duration',
                            7 : u'allow_comments',
                            8 : u'rating',
                            9 : u'ratings_total',
                            10: u'views_total',
                            11: u'comments_total',
                            12: u'bookmarks_total',
                            }
    try:
        user = get_list_or_404(DMUser, fid=userfid)[0]
        querySet = DMVideo.objects.filter(user=user)
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dm_comment_list(request, call_type, userfid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {
                            0 : u'created_time',
                            1 : u'user__screenname',
                            2 : u'video__user__screenname',
                            3 : u'video__fid',
                            4 : u'message',
                            5 : u'language',
                            6: u'user__fid',
                            7: u'video__user__fid',
                            }
    try:
        user = get_list_or_404(DMUser, fid=userfid)[0]
        querySet = DMComment.objects.filter(user=user)
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dm_videocomment_list(request, call_type, videofid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {
                            0 : u'created_time',
                            1 : u'user__screenname',
                            2 : u'video__user__screenname',
                            3 : u'video__fid',
                            4 : u'message',
                            5 : u'language',
                            6: u'user__fid',
                            7: u'video__user__fid',
                            }
    try:
        video = get_list_or_404(DMVideo, fid=videofid)[0]
        querySet = DMComment.objects.filter(video=video)
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)


@login_required(login_url=u'/login/')
def get_dm_fans_list(request, call_type, userfid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior

    columnIndexNameMap = {
                            0 : u'fid',
                            1 : u'username',
                            2 : u'screenname',
                            3 : u'gender',
                            4 : u'description',
                            5 : u'language',
                            6 : u'status',
                            7 : u'ftype',
                            8 : u'url__original_url',
                            9 : u'views_total',
                            10 : u'videos_total',
                            }
    try:
        user = get_list_or_404(DMUser, fid=userfid)[0]
        querySet = user.fans.all()
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dm_friends_list(request, call_type, userfid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior

    columnIndexNameMap = {
                            0 : u'fid',
                            1 : u'username',
                            2 : u'screenname',
                            3 : u'gender',
                            4 : u'description',
                            5 : u'language',
                            6 : u'status',
                            7 : u'ftype',
                            8 : u'url__original_url',
                            9 : u'views_total',
                            10 : u'videos_total',
                            }
    try:
        user = get_list_or_404(DMUser, fid=userfid)[0]
        querySet = user.friends.all()
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dm_following_list(request, call_type, userfid):
    querySet = None
    #columnIndexNameMap is required for correct sorting behavior

    columnIndexNameMap = {
                            0 : u'fid',
                            1 : u'username',
                            2 : u'screenname',
                            3 : u'gender',
                            4 : u'description',
                            5 : u'language',
                            6 : u'status',
                            7 : u'ftype',
                            8 : u'url__original_url',
                            9 : u'views_total',
                            10 : u'videos_total',
                            }
    try:
        user = get_list_or_404(DMUser, fid=userfid)[0]
        querySet = user.following.all()
    except ObjectDoesNotExist:
        pass
    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, call_type)

@login_required(login_url=u'/login/')
def get_dmvideo_chart(request, harvester_id, userfid):

    user = get_list_or_404(DMUser, fid=userfid)[0]
    count = DMVideo.objects.filter(user=user).count()

    fromto = DMVideo.objects.filter(user=user).order_by(u"created_time")
    base = fromto[0].created_time if count != 0 else dt.datetime.now()
    to = fromto[count-1].created_time if count != 0 else dt.datetime.now()

    days = (to - base).days + 1
    dateList = [ base + dt.timedelta(days=x) for x in range(0,days) ]
    description = {"date_val": ("date", "Date"),
                   "post_count": ("number", "Post count"),
                  }
    data = []
    for date in dateList:
        c = DMVideo.objects.filter(user=user).filter(created_time__year=date.year,created_time__month=date.month,created_time__day=date.day).count()
        data.append({"date_val":date, "post_count":c})

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    logger.debug(data_table.ToJSon())

    response =  HttpResponse(data_table.ToJSon(), mimetype='application/javascript')
    return response

@login_required(login_url=u'/login/')
def get_dmcomment_chart(request, harvester_id, userfid):

    user = get_list_or_404(DMUser, fid=userfid)[0]
    count = DMComment.objects.filter(user=user).count()

    fromto = DMComment.objects.filter(user=user).order_by(u"created_time")
    base = fromto[0].created_time if count != 0 else dt.datetime.now()
    to = fromto[count-1].created_time if count != 0 else dt.datetime.now()

    days = (to - base).days + 1
    dateList = [ base + dt.timedelta(days=x) for x in range(0,days) ]
    description = {"date_val": ("date", "Date"),
                   "post_count": ("number", "Post count"),
                  }
    data = []
    for date in dateList:
        c = DMComment.objects.filter(user=user).filter(created_time__year=date.year,created_time__month=date.month,created_time__day=date.day).count()
        data.append({"date_val":date, "post_count":c})

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    logger.debug(data_table.ToJSon())

    response =  HttpResponse(data_table.ToJSon(), mimetype='application/javascript')
    return response

@login_required(login_url=u'/login/')
def get_dmvideocomment_chart(request, harvester_id, videofid):

    logger.debug(videofid)
    video = get_list_or_404(DMVideo, fid=videofid)[0]
    count = DMComment.objects.filter(video=video).count()

    fromto = DMComment.objects.filter(video=video).order_by(u"created_time")
    base = fromto[0].created_time if count != 0 else dt.datetime.now()
    to = fromto[count-1].created_time if count != 0 else dt.datetime.now()

    days = (to - base).days + 1
    dateList = [ base + dt.timedelta(days=x) for x in range(0,days) ]
    description = {"date_val": ("date", "Date"),
                   "post_count": ("number", "Post count"),
                  }
    data = []
    for date in dateList:
        c = DMComment.objects.filter(video=video).filter(created_time__year=date.year,created_time__month=date.month,created_time__day=date.day).count()
        data.append({"date_val":date, "post_count":c})

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    logger.debug(data_table.ToJSon())

    response =  HttpResponse(data_table.ToJSon(), mimetype='application/javascript')
    return response

