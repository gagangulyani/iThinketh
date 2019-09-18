$(document).ready(function() {
    setTimeout(function() {
        $(".alert-light").addClass('animated');
        $(".alert-light").addClass('fadeOutUp');
        setTimeout(function() {
            $(".alert-light").remove();
        }, 500);
    }, 2000);
    colorizer();
});

function loading(t = 200) {
    setTimeout(function() {
        $('#myOverlay').show();
        $('#loadingGIF').show();
    }, t);
}

// $('a').click(function(){
//     loading(0);
// });

function ClickToGoTo(link, ele) {
    loading()
    $(ele).addClass('tada');
    $(ele).addClass('animated');
    $('body').addClass('stop-scrolling')
    window.open(link, '_self');
}

function Edit(param) {
    //    console.log(param);
    if (param.ele) {
        ele = param.ele;
    }

    if (window.active) {
        Discard(ele);
        window.active = false;
        return;
    } else {
        window.active = true;
    }

    if (param.isQuote) {
        isQuote = true;
        var tag = 'textarea'
    } 
    else {
        isQuote = false;
        var tag = 'input';
        if ($(ele).hasClass('d-none')) {
            Discard(ele);
            return;
        }
        $(ele).toggleClass('d-none');
    }

    var form_edit = `
    <div class="form-group" id='form-in'>
        <${tag} class="form-control" type = "${param.type|| 'text'}" id="form-in-main" name="quote" placeholder="${param.placeholder || 'Write Image quote'}">
        </${tag}>
        <div class="d-flex justify-content-end mt-1">
            <a class="btn btn-outline-dark" 
            href="javascript:Discard('${ele}', ${isQuote})" 
            style='font-size: 0.8em!important;'>
            Discard Changes
            </a>
            <a class="btn btn-dark ml-1" 
            href='javascript:Save({data_ : "${QuoteID || username}",
ele: "${ele}", isQuote : ${isQuote}, fieldType: "${param.fieldType || null}"})'
             style='font-size: 0.8em!important;'>Save Changes</a>
        </div>
    </div>`;
    //    console.log(form_edit);
    var element_value = $(ele).text();
    $(form_edit).insertAfter(ele);
    //    // console.log('worked!');
    $('#form-in-main').val(element_value);
}

function Save(param) {
    //    // console.log('param : \n');
    //    // console.log(param);
    if (param.data_) {
        var data_ = param.data_;
    } else {
        //        console.log('data not provided for saving data');
    }

    if (param.ele) {
        var ele = param.ele;
    } else {
        //        console.log('element not provided for fetching the data');
    }

    var content = $('#form-in-main').val();
    //    console.log(content);

    //    // console.log('isQuote: '+ isQuote);
    if (param.isQuote) {
        //        console.log('request to image update');
        var url_ = '/api/quote';
        var obj = { 'quote': content, 'quoteID': data_ };
    } else {
        //        console.log('request to api');
        var url_ = '/api';
        var obj = {
            'username': data_,
            'fieldType': param.fieldType,
            'data': content
        }
    }

    //    console.log(obj);
    $.ajax({
        url: url_,
        type: 'PUT',
        data: JSON.stringify(obj),
        contentType: 'application/json',
        dataType: 'json',
        success: function(data) {
            // $('html, body').animate({ scrollTop: 0 }, 'fast');
            reloader();
            Discard(ele, isQuote);
        }
    })
}

function reloader(){
    var unique = $.now();
    $('.img-quote').attr('src',$('.img-quote').attr('src') + "?" + unique);
}

function Discard(ele, isQuote=false) {
    $('#form-in').remove();
    if (!(isQuote))
        $(ele).removeClass('d-none');
    window.active = false;
}

function Delete(param){
    if (param.isQuote){
        var obj = {
            'quoteID': QuoteID
        }
        $.ajax({
            url: '/api/quote',
            data: JSON.stringify(obj),
            contentType: 'application/json',
            dataType: 'json',
            type: 'DELETE'
        })
        .done(function() {
            window.open(profileLink, '_self');
        })
        .fail(function() {
            window.location.reload(true);
        })
        
    }
}

function colorizer() {
    ele = document.getElementsByClassName('colorize');
    var end = 120;
    var beg = 50;
    for (let i = 0; i < ele.length; i++) {
        text = ele[i].innerText;
        var newText = "";
        for (let j = 0; j < text.length; j++) {
            color1 = Math.floor(Math.random() * end) + beg;
            color3 = Math.floor(Math.random() * end) + beg;
            color2 = Math.floor(Math.random() * end) + beg;
            new_color = "" + color1 + ',' + color2 + ',' + color3;
            newText += "<span style='color: rgb(" + new_color + ")'>" + text[j] + "</span>";
        }
        ele[i].innerHTML = newText;
    };
}