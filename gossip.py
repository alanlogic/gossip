import random

from sqlalchemy.sql.expression import func, or_
from flask import (Flask, request, redirect, url_for, abort,
                   render_template, session, flash)

from database import db_session
from form import LoginForm, RegisterForm
from model import Gossip, Friend, User, Player, Invite

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '''B\x8f\xcb"\x84{\xb7g\xb2\'\xb4v\xc3\x92\
                              xc9\xf0\xcd\xc5\xfd\xc8\xfc\xdf\xa5\xb9'''


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def main_index():
    return render_template('index.html')


@app.route('/<int:user_id>')
def user_index(user_id):
    user = User.query.filter(User.user_id == user_id).one_or_none()
    if user is None:
        abort(404)
    return render_template('user_page.html')


@app.route('/my-gossip')
def my_gossip():
    page = int(request.args.get('page', 0))
    gossips = (Gossip.query.
               filter(Gossip.user_id == session['user_id']).
               order_by(Gossip.datetime.desc()).limit(10)
               .offset(page * 10).all())
    if len(gossips) == 0 and page != 0:
        return 'nomore'
    return render_template('my_gossip.html', gossips=gossips, page=page)


def get_friends(user_id):
    friends = (db_session.query(Friend.user1).
               filter(Friend.user2 == user_id).
               union
               (db_session.query(Friend.user2).
                filter(Friend.user1 == user_id))
               .all())
    return list(map(lambda friend: friend.user1, friends))


# have another choice
@app.route('/infocenter')
def infocenter():
    page = int(request.args.get('page', 0))
    friends_id = get_friends(session['user_id'])
    if len(friends_id) == 0:
        return render_template('infocenter.html', r_gossips=[], page=page)
    r_gossips = (db_session.query(Gossip, Player.nickname).
                 join(Player, Gossip.user_id == Player.user_id).
                 filter(Gossip.user_id.in_(friends_id)).
                 order_by(Gossip.datetime.desc()).
                 limit(10).offset(page * 10).all())
    if len(r_gossips) == 0 and page != 0:
        return 'nomore'
    return render_template('infocenter.html', r_gossips=r_gossips, page=page)


@app.route('/glance/<int:g_id>')
def glance(g_id):
    gossip = Gossip.query.filter(Gossip.gossip_id == g_id).one_or_none()
    if gossip is None:
        return 'none'
    player = Player.query.filter(Player.user_id == session['user_id']).one()
    if player.gold < gossip.price:
        return 'noenough'
    player.gold -= gossip.price
    db_session.commit()
    return gossip.content


@app.route('/rank')
def rank():
    page = int(request.args.get('page', 0))
    friends_id = get_friends(session['user_id'])
    if len(friends_id) == 0:
        return render_template('rank.html', ranked=[], page=page)
    # validate if you have friends or it will be a warning
    ranked = (Player.query.filter(Player.user_id.in_(friends_id)).
              order_by(Player.gold).offset(page * 10).limit(10).all())
    return render_template('rank.html', ranked=ranked, page=page)


@app.route('/fish')
def fish():
    max_id = db_session.query(func.max(Gossip.gossip_id)).scalar()
    target_id = max_id * random.random()
    f_gossip = (db_session.query(Gossip, User.username, Player.nickname).
                join(User, Gossip.user_id == User.user_id).
                join(Player, Gossip.user_id == Player.user_id).
                filter(Gossip.gossip_id >= target_id)
                .first())
    return render_template('fish.html', f_gossip=f_gossip)


# problem: only user look up the messagebox,otherwise won't get the Invite
@app.route('/message-box')
def message_box():
    # a confusing query
    requests = (db_session.query(Invite.user2, User.username).
                join(User, Invite.user2 == User.user_id).
                filter(Invite.user1 == session['user_id']).all())
    return render_template('message_box.html', requests=requests)


@app.route('/reply')
def reply():
    inviter_id = request.args.get('inviterId', None)
    if inviter_id is None:
        return 'fail'
    invitation = Invite.query.filter(Invite.user1 == session['user_id'],
                                     Invite.user2 == inviter_id).first()
    if invitation is None:
        return 'norecord'
    if request.args.get('reply', 'refuse') == 'accept':
        db_session.add(Friend(user1=session['user_id'], user2=inviter_id))
    db_session.delete(invitation)
    db_session.commit()
    return 'success'


@app.route('/add-gossip', methods=['Post'])
def add_gossip():
    db_session.add(Gossip(request.form, session['user_id']))
    db_session.commit()
    return 'success'


@app.route('/add-friend')
def add_friend():
    username = request.args.get('username', None)
    if username is None:
        return 'fail'
    user = User.query.filter(User.username == username).one_or_none()
    if user is None:
        return 'nobody'
    has_been = (Friend.query.filter(or_(Friend.user1 == session['user_id'],
                                        Friend.user2 == user.user_id),
                                    (Friend.user2 == session['user_id'],
                                     Friend.user1 == user.user_id)).
                one_or_none())
    if has_been is not None:
        return 'hasbeen'
    invited = (Invite.query.filter(Invite.user1 == user.user_id,
                                   Invite.user2 == session['user_id']).
               one_or_none())
    if invited is not None:
        return 'invited'
    db_session.add(Invite(user1=user.user_id, user2=session['user_id']))
    db_session.commit()
    return 'success'


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = form.get_user().user_id
        session['user_id'] = user_id
        return redirect(url_for('user_index', user_id=user_id))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('main_index'))


# need debug
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.add_user()
        session['user_id'] = user.user_id
        return redirect(url_for('user_index', user_id=user.user_id))
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run()
