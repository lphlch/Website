from flask.helpers import flash, url_for
from flask.templating import render_template
from flask_login.utils import login_required
from flask_migrate import current
from flask_login import current_user
from flask import request
from werkzeug.urls import url_decode
from werkzeug.utils import redirect
from app.main.forms import CommentForm, EditProfileForm, RedirectToEditForm
from app.test import createModule
from . import main
import flask
# from ..models import User
# from ..models import Video
from ..models import *

# @main.route('/<int:page>/')
# def index(page=None):
#     if page is None:
#         page = 1
#     #tags = Tag.query.all()
#     page_data = Video.query
#     # 编号
#     id = request.args.get('id', 0)  # 获取id，获取不到返回0
#     if int(id) != 0:
#         page_data = page_data.filter_by(id=int(id))
#     # 点赞数
#     likenum = request.args.get('likenum', 0)
#     playnum = 1
#     if int(likenum) != 0:
#         if int(playnum) == 1:
#             page_data = page_data.order_by(
#                 Video.likenum.desc()
#             )
#         else:
#             page_data = page_data.order_by(
#                 Video.likenum.asc()
#             )
#     # 视频发布时间
#     uploadtime = request.args.get('uploadtime', 0)
#     if int(uploadtime) != 0:
#         if int(uploadtime) == 1:
#             page_data = page_data.order_by(
#                 Video.uploadtime.desc()
#             )
#         else:
#             page_data = page_data.order_by(
#                 Video.uploadtime.asc()
#             )
#     # 播放量
#     playnum = request.args.get('playnum', 0)
#     if int(playnum) != 0:
#         if int(playnum) == 1:
#             page_data = page_data.order_by(
#                 Video.playnum.desc()
#             )
#         else:
#             page_data = page_data.order_by(
#                 Video.playnum.asc()
#             )
#     # 评论量
#     commentnum = request.args.get('commentnum', 0)
#     if int(commentnum) != 0:
#         if int(commentnum) == 1:
#             page_data = page_data.order_by(
#                 Video.commentnum.desc()
#             )
#         else:
#             page_data = page_data.order_by(
#                 Video.commentnum.asc()
#             )

#     page = request.args.get("page", 1)
#     page_data = page_data.paginate(page=int(page), per_page=10)

#     p = dict(
#         id=id,
#         likenum=likenum,
#         uploadtime=uploadtime,
#         playnum=playnum,
#         commentnum=commentnum
#     )
#     return render_template("index.html", p=p, page_data=page_data)

@main.route('/')
def index():
    data = Video.query.all()
    return render_template('animation.html', data=data)

# 轮播图
@main.route('/animation/')
def animation():
    data = Video.query.all()
    return render_template('animation.html', data=data)


@main.route('/space')
def spaceDefault():
    #if user is not logged in, redirect to login page
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    #if user is logged in, render the space page
    return flask.render_template('UserSpace.html', user=current_user)

# Default space
@main.route('/space/')
def spaceDefaultAddition():
    #the same as above
    #if user is not logged in, redirect to login page
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    #if user is logged in, render the space page
    return flask.render_template('UserSpace.html', user=current_user)

# Redirect to user space
@main.route('/space/<username>')
@login_required
def spaceUser(username):
    #get the user from the database
    user1=User(username)

    #if click the edit button, redirect to edit page
    form=RedirectToEditForm()
    if form.validate_on_submit():
        return flask.redirect(flask.url_for('editProfile'))
    return flask.render_template('UserSpace.html',user=user1)

@main.route('/video/<videoname>')
def playvideo(videoname):
    # video1=Video(videoname)
    video = Video.query.filter_by(title=videoname).first()
    # 这里依据名字从查找video，后期可以改为依据id查找

    form = CommentForm()
    buttonforms = createModule() #button forms 4 in 1 
    # like,coin,star,share
    
    if form.validate_on_submit():
        comment = Comment(content=form.body,author=current_user._get_current_object())
        # _get_current_object() returns somethign in the session, and even if author is not declared, this stil works
        # very mysterious and don't konw why
        db.session.add(comment)
        return redirect(url_for('.playvideo'),videoname=videoname)
    if buttonforms[0].validate_on_submit():
        # like
        exist_videolike = Videolike.query.filter_by(user_id=current_user.get_id(),video_id=video.id).first()
        if exist_videolike == None:
            video.likenum += 1 
            videolike = Videolike(video_id=video.id,user_id=current_user.get_id())
            db.session.add(videolike)
        else:
            video.likenum -= 1
            db.session.delete(exist_videolike)
        db.session.commit()

    if(buttonforms[1].validate_on_submit()):
        # coin
        exist_videocoin = Videocoin.query.filter_by(user_id=current_user.get_id(),video_id=video.id).first()
        if exist_videocoin == None:
            video.coinnum += 1
            videocoin = Videocoin(video_id=video.id,user_id=current_user.get_id())
            db.session.add(videocoin)    
            db.session.commit()
        else:
            flash('You have throwed the coin')            

    if(buttonforms[2].validate_on_submit()):
        # star 
        exist_videocol = Videocol.query.filter_by(user_id=current_user.get_id(),video_id=video.id).first()
        if exist_videocol == None:
            video.videocols += 1
            videocol = Videocol(video.id,current_user.get_id())
            db.session.add(videocol)
        else:
            db.session.delete(exist_videocol)
        db.session.commit()

    if(buttonforms[3].validate_on_submit()):
        # share
        pass
        
    
    comments = Comment.query.order_by(Comment.addtime.desc()).all
    
    # return flask.render_template('extend.html',video=video1)
    return render_template('video.html',video=video,comments=comments, \
    buttonforms=buttonforms)

# 用户资料编辑
@main.route("/editProfile",methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.nickName = form.nickName.data
        current_user.password = form.password.data
        current_user.about_me = form.introduction.data

        db.session.add(current_user)
        flash("You have updated your profile")
        return redirect(url_for(".spaceUser",username=current_user.name))
    form.nickName.data = current_user.nickName
    form.password.data = current_user.password
    form.introduction.data = current_user.introduction
    return render_template('EditProfile.html',form=form)

# 隐私政策
@main.route('/privacy')
def privacy():
    return flask.render_template('privacy.html')

#用户协议
@main.route('/term_of_use')
def licence():
    return flask.render_template('termOfUse.html')

# 管理员资料编辑器
