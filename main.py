#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from hashlib import sha1
import lxml
from lxml import etree
import datetime, time
import cPickle as pickle
from sqlalchemy import *
import urllib, urllib2
import json
import random

def index(request):
    return HttpResponse('ok')

def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSingnature(request),content_type="text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request),content_type="application/xml")
        return response
    else:
        return None


def checkSingnature(request):
    '''
        验证微信api提供的signature和token等信息
    '''

    token = settings.TOKEN
    signature = request.GET.get('signature', None)
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)

    infostr = ''.join(sorted([token, timestamp, nonce]))
    if infostr:
        hashstr = sha1(infostr).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            return None
    else:
        return None

def responseMsg(request):
    config_cache.judge()
    config = game_config.ploy_system_simple
    str_xml = request.POST.keys()[0]
    xml = etree.fromstring(str_xml)
    fromUser = xml.find("FromUserName").text
    toUser = xml.find("ToUserName").text
    createTime = str(int(time.time()))
    msgType = xml.find("MsgType").text
    if msgType == 'event':
        #关注动作
        content = config['Msg']['welcome']
    elif msgType == 'text':
        #发送文字消息
        content = xml.find("Content").text
    elif msgType == 'image':
        #图片
        content = config['shard']['reply']
    else:
        content = config['Msg']['all']
    texttpl = '''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>''' % (fromUser, toUser, createTime, content)
    return HttpResponse(texttpl)
