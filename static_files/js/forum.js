var page = {
    isAuthor : false,
    add_comment_url: '',
    del_comment_url: '',
    comments_div: null,
    editor: null
}

function onCommentSubmit(){
    var author = $('input[name=author_name]').val();
    var msg = $('textarea[name=msg]').val();
    var csrf = $('input[name=csrfmiddlewaretoken]').val();
    if(author.length == 0 || msg.length == 0){
        return;
    }
    $.post(page.add_comment_url, {'author_name' : author, 'msg' : msg, 'csrfmiddlewaretoken' : csrf}, function(response){
        var data = $.parseJSON(response);
        if(data.code == 200){
            var tpl = _.template($('#comment-template').html());
            var comment = $(tpl({'author_name' : author, 'msg' : msg, 'cid' : data.cid, 'date': data.date})).prependTo(page.comments_div);
            if(page.isAuthor){
                comment.find('a.comment-delete-link').bind('click', onDeleteCommentClick);
            }
            page.comments_div.fadeIn(300);
            try{
                page.editor.clear();
            }
            catch(e) {
                app.error(e.message)
            }
        }
        else {
                app.error('Failed to add comment. code: ' + data.code + ';' + data.message);
            }
        }
    );
}
function onDeleteCommentClick(e){
    e.preventDefault();
    var csrf = $('input[name=csrfmiddlewaretoken]').val();
    var container = $(this).parents('div.comment');
    $.post(page.del_comment_url, {'cid' : container.attr('data-cid'),  'csrfmiddlewaretoken' : csrf}, function(response){
        var data = $.parseJSON(response);
        if(data.code == 200){
            container.fadeOut(300, function(){
                container.remove();
                if(page.comments_div.find('div.comment').length == 0) page.comments_div.fadeOut(300);
            });
        } else {
            app.error('Failed to delete comment. code: ' + data.code + '; ' + data.message);
        }
    });
}
function onGetCommentsComplete(data){
    if(data.code == 200){
        var tpl = _.template($('#comment-template').html());
        for(var i=0;i<data.comments.length;i++){
            var obj = $.parseJSON(data.comments[i])
            var comment = $(tpl({'author_name':obj.author_name, 'msg':obj.msg, 'cid':obj.cid, 'date':obj.date}));
            comment.prependTo(page.comments_div);
            if(page.isAuthor){
                comment.find('a.comment-delete-link').bind('click', onDeleteCommentClick);
            }
        }
        if(data.comments.length > 0) page.comments_div.fadeIn(200);
    }
    else{
        app.log('get_comments failed. code: ' + data.code + '; message: ' + data.message);
    }
}