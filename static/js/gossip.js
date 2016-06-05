$(document).ready(function() {
    function initMore() {
        $('#more').removeAttr('disabled').text('加载更多').attr('data-page', 1).show();
    }

    $('#gossip').click(function(evt) {
        var url=$(this).attr('href');
        $('main').load(url);
        $('.active').removeClass('active');
        $(this).parent('li').addClass('active');
        initMore();
        evt.preventDefault();
    }); //end click
    $('#gossip').click();

    $('#rank').click(function(evt) {
        var url=$(this).attr('href');
        $('main').load(url);
        $('.active').removeClass('active');
        $(this).parent('li').addClass('active');
        $('#more').hide();
        evt.preventDefault();
    }); //end click

    $('#info').click(function(evt) {
        var url=$(this).attr('href');
        $('main').load(url);
        $('.active').removeClass('active');
        $(this).parent('li').addClass('active');
        initMore();
        evt.preventDefault();
    }); //end click

    $('main').delegate('#fish', 'click', function(evt){
        var url=$(this).attr('href');
        $('#present').load(url);
        evt.preventDefault();
    }); //end delegate

    $('#request').click(function(evt) {
        var url=$(this).attr('href');
        $('main').load(url);
        $('.active').removeClass('active');
        $(this).parent('li').addClass('active');
        $('#more').hide();
        evt.preventDefault();
    }); //end click

    $('main').delegate('#seek', 'click', function(evt) {
        var url = $(this).attr('href');
        var username = $('#username').val();
        $.get(url, {username: username}, function(data) {
            if (data == 'success')
                alert('好友请求已发送');
            else if (data == 'fail')
                alert('请求出错');
            else if (data == 'hasbeen')
                alert('已经是好友了');
            else if (data == 'nobody')
                alert('无此用户');
            else
                alert('您已发出过请求');
        }); //end get
        
        evt.preventDefault();
    }); //end delegate

    $('main').delegate('.reply', 'click', function(evt) {
        var url = $(this).attr('href');
        var reply = $(this).attr('data-reply');
        var inviterId = $(this).parents('tr').attr('data-id');
        $.get(url, {reply: reply, inviterId: inviterId}, function(data) {
            if (data == 'success'){
                alert('处理成功');
                $('#request').click();
            }
            else
                alert('处理失败');
        }); //end get
        evt.preventDefault();
    }); //end delegate

    $('main').delegate('#push', 'click', function(evt) {
        var url = $(this).attr('href');
        gossipData = $('#newGossip').serialize();
        $.post(url, gossipData, function(data) {
            alert('发表成功');
            $('#gossip').click();
        }); //end post
        evt.preventDefault();
    }); //end delegate

    $('main').delegate('.glance', 'click', function(evt) {
        var url = $(this).attr('href');
        var glance = $(this);
        $.get(url, {}, function(data) {
            if (data == 'noenough') {
                alert('你的金币不足');
            }
            else
                glance.replaceWith('<p>' + data + '</p');
        }); //end get
        evt.preventDefault();
    }); //end delegate

    $('#more').click(function() {
        var url = $('.active > a').attr('href');
        var page = $('#more').attr('data-page');
        $('#more').attr('data-page', parseInt(page) + 1);
        $.get(url, {page: page}, function(data) {
            if (data != 'nomore')
                $('main').append(data);
            else 
                $('#more').text('没有更多内容了').attr('disabled', 'disabled');
        }); //end get
    }); //end click
}); //end ready