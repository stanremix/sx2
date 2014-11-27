# Create your views here.
# -*- coding: utf8 -*-
from upyun import UpYun,md5,md5file
from people.models import Profile
from django.contrib.auth.models import User
from django.http import HttpResponse
import os
import sys
import pdb
DOMAIN_NAME = "http://newavatar.b0.upaiyun.com"
def upload_img(request):
    #u = UpYun('空间名称','操作员用户名','操作员密码')
    u = UpYun('newavatar','12345','qwer!@#$')
    #查看版本信息
    #print u.version()

    #设定api所调用的域名
    #u.setApiDomain('v0.api.upyun.com')

    #创建目录
    #a = u.mkDir('/testa')
    #print a
    #a = u.mkDir('/a/b/c', True) 可自动创建父级目录（最多10级）

    #显示目录下的文件
    #a = u.readDir('/test/')
    #for i in a:
    #    print i.filename
    
    #开启调试
    #u.debug = True
    #get user
    pdb.set_trace()
    user = User.objects.get(username="User1")
    user_id = user.id
    pro = user.get_profile()
    #get user avatar url
    url_avatar = pro.avatar.url
    dir_path = url_avatar.split("/")
    del dir_path[-1]
    #get upload file path
    file_path = "/".join(dir_path)
    #create dir
    a = u.mkDir('%s'%file_path,True)
    #get current dir path
    op=os.path.abspath(os.path.curdir).split()
    #get current img path
    userp = url_avatar.split()
    op.extend(userp)
    img_path = ''.join(op)
    #open img
    data = open('%s'%img_path,'rb')
    #设置待上传文件的 Content-MD5 值
    #如又拍云服务端收到的文件MD5值与用户设置的不一致，将回报 406 Not Acceptable 错误
    u.setContentMD5(md5file(data))

    #置待上传文件的 访问密钥（注意：仅支持图片空！，设置密钥后，无法根据原文件URL直接访问，需带 URL 后面加上 （缩略图间隔标志符+密钥） 进行访问）
    #如缩略图间隔标志符为 ! ，密钥为 bac，上传文件路径为 /folder/test.jpg ，那么该图片的对外访问地址为： http://空间域名/folder/test.jpg!bac
    #u.setFileSecret('bbbb')
    
    #开始上传文件
    pdb.set_trace()
    #get upload img path
    file_path = file_path.split()
    img_format = url_avatar.rsplit(".")[-1]
    user_img_jpg = '%s.%s'%(user_id,img_format)
    file_path.append(user_img_jpg)
    upload_path = '/'.join(file_path)
    #upload img
    a = u.writeFile('%s'%upload_path,data)
    print a
    #a = u.writeFile('/a/b/c/d/e/f/g/logo.jpg',data, True) 可自动创建父级目录（最多10级）
    #spice upyun current img url
    domin_url = DOMAIN_NAME.split()
    domin_url.append(upload_path)
    upyun_img_url = ''.join(domin_url)
    #
    if a:
    	pro.avatar = upyun_img_url
    	pro.save()
    #获取上传后的图片信息（仅图片空间有返回数据）
    print(u.getWritedFileInfo('x-upyun-width')) # 图片宽度
    print(u.getWritedFileInfo('x-upyun-height')) # 图片高度
    print(u.getWritedFileInfo('x-upyun-frames')) # 图片帧数
    print(u.getWritedFileInfo('x-upyun-file-type')) # 图片类型

    #获取文件信息
    print u.getFileInfo('/logo.jpg')

    #a = u.writeFile('/testd.jpg','sdfsdf')
    #print a
    #a = u.deleteFile('/testd.jpg')
    #print a
    a = u.readDir('/')
    if a:
        for i in a:
            print i.filename
    else : 
        print a

    return HttpResponse("success")

def splice_url():
	pass

def test(request):
	from util import upload_pic
	pdb.set_trace()
	pro = Profile.objects.get(user__id=14380)
	upload_pic(pro.avatar, 14380, 'ava')
	
	return HttpResponse("success")


def test_a(request):
	from checkpub.models import CheckPub
	pdb.set_trace()

	conn = UpYun('cpp19', 'one9', 'one9in1234')

	cp = CheckPub.objects.get(id=273344)
	cp_id = cp.id
	#user_id = cp.user.id

	op=os.path.abspath(os.path.curdir).split()
    #get current img path
	userp = cp.photo.url.split()
	op.extend(userp)
	img_path = ''.join(op)
    #open img
	data = open('%s'%img_path,'rb')
    #设置待上传文件的 Content-MD5 值
    #如又拍云服务端收到的文件MD5值与用户设置的不一致，将回报 406 Not Acceptable 错误
	conn.setContentMD5(md5file(data))

	#img_format = cp.photo.url.rsplit(".")[-1]
	#user_img_jpg = '%d.%s'%(user_id,img_format)
	#user_img_jpg = '%d'%(user_id)
	
	result = conn.writeFile('%d' % cp_id ,data)
	print result

	return HttpResponse("success")

def test_dd(request):
    u = UpYun('newavatar','one9','one9in1234')
    #查看版本信息
    #print u.version()

    #设定api所调用的域名
    #u.setApiDomain('v0.api.upyun.com')

    #创建目录
    #a = u.mkDir('/testa')
    #print a
    #a = u.mkDir('/a/b/c', True) 可自动创建父级目录（最多10级）

    #显示目录下的文件
    #a = u.readDir('/test/')
    #for i in a:
    #    print i.filename
    
    #开启调试
    #u.debug = True
    #get user
    pdb.set_trace()
    
    user = User.objects.get(id=301)
    user_id = user.id
    pro = user.get_profile()
    #get user avatar url
    url_avatar = pro.avatar.url
    dir_path = url_avatar.split("/")
    del dir_path[-1]
    #get upload file path
    file_path = "/".join(dir_path)
    #create dir
    a = u.mkDir('%s'%file_path,True)
    #get current dir path
    op=os.path.abspath(os.path.curdir).split()
    #get current img path
    userp = url_avatar.split()
    op.extend(userp)
    img_path = ''.join(op)
    #open img
    data = open('%s'%img_path,'rb')
    #设置待上传文件的 Content-MD5 值
    #如又拍云服务端收到的文件MD5值与用户设置的不一致，将回报 406 Not Acceptable 错误
    u.setContentMD5(md5file(data))

    #置待上传文件的 访问密钥（注意：仅支持图片空！，设置密钥后，无法根据原文件URL直接访问，需带 URL 后面加上 （缩略图间隔标志符+密钥） 进行访问）
    #如缩略图间隔标志符为 ! ，密钥为 bac，上传文件路径为 /folder/test.jpg ，那么该图片的对外访问地址为： http://空间域名/folder/test.jpg!bac
    #u.setFileSecret('bbbb')
    
    #开始上传文件
    pdb.set_trace()
    #get upload img path
    file_path = file_path.split()
    img_format = url_avatar.rsplit(".")[-1]
    user_img_jpg = '%s.%s'%(user_id,img_format)
    file_path.append(user_img_jpg)
    upload_path = '/'.join(file_path)
    #upload img
    a = u.writeFile('%s'%upload_path,data)
    print a
    #a = u.writeFile('/a/b/c/d/e/f/g/logo.jpg',data, True) 可自动创建父级目录（最多10级）
    #spice upyun current img url
    domin_url = DOMAIN_NAME.split()
    domin_url.append(upload_path)
    upyun_img_url = ''.join(domin_url)
    #
    if a:
    	pro.avatar = upyun_img_url
    	pro.save()
    #获取上传后的图片信息（仅图片空间有返回数据）
    print(u.getWritedFileInfo('x-upyun-width')) # 图片宽度
    print(u.getWritedFileInfo('x-upyun-height')) # 图片高度
    print(u.getWritedFileInfo('x-upyun-frames')) # 图片帧数
    print(u.getWritedFileInfo('x-upyun-file-type')) # 图片类型

    #获取文件信息
    print u.getFileInfo('/logo.jpg')

    #a = u.writeFile('/testd.jpg','sdfsdf')
    #print a
    #a = u.deleteFile('/testd.jpg')
    #print a
    a = u.readDir('/')
    if a:
        for i in a:
            print i.filename
    else : 
        print a


