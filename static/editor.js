
$(document).ready(function() {
    // 다운로드 버튼 숨기기
    $('#download_ctrl').css('display','none');

    // 상태 select box 기본 선택
    $("select option[value="+$('#select_default').val()+"]").attr("selected","selected");



    var keyvalue = {}
    function get_keyword_dict(){
        $.ajax({
            type:"GET",
            url: "/pybo/upload/keyword/dict",
            success: function(data,status){ //status는 생략해도 됨
                //console.log(data);

                keyvalue = data
                //console.log(keyvalue);
                realtime_Check();
            },
            error: function(error){
                console.log(error.responseText);
            }
        });
    }
    get_keyword_dict();


    function realtime_Check(){
        if(document.location.href.indexOf("/pybo/editor") > 0){
        // ajax()에 {}객체 1개 전달
            var subject = $('#subject').val();
            var text = $('textarea#content').val();
            var qid = $('#qid').val();

            //text = encodeURIComponent(text);
            $.ajax({
                type:"POST",
                url: "/pybo/editor/convert",
                async : false,
                data: {
                        subject : subject,
                        content : text,
                        qid : qid
                    },
                success: function(data,status){ //status는 생략해도 됨
                    $('#subtitle').val(data);
                    $('#AddOption').html(''); // 테이블 초기화

                    var contents = '';

                    var res = data.split("\n");
                    var cnt = 1;
                    var subtitle_line = "";

                    for(var i in res) {
                        if(i == 0){}
                        else if(i % 2 == 0){
                            var _width = '1200';
                            var _height = '1000';
                            // 팝업을 가운데 위치시키기 위해 아래와 같이 값 구하기
                            var _left = ( window.screen.width/2) - (_width /2);
                            var _top = ( window.screen.height/2) - (_height /2);
                            //console.log(cnt + ":" + subtitle_line);
                            //console.log(keyvalue);
                            for(var key in keyvalue){
                                if(subtitle_line.indexOf(key) > -1){
                                    value = keyvalue[key];
                                    if(value == null || value == undefined) value = key;
                                    //console.log(key + ' : ' + value);
                                    var regEx = new RegExp(key, "gi");
                                    subtitle_line = subtitle_line.replace(regEx, "<a href='#none' style=\"font-weight: bold;\" onclick=\"window.open('/pybo/upload/search/keyword?page=1&kw="+key+"&num="+cnt+"', 'windowPop', 'width="+_width+", height="+_height+", left="+_left+", top="+_top+", resizable = yes, location = no ')\">"+key+"</a>");
                                }
                            }

                            contents += '<tr class=\"text-center subtitle_back\" id=\"tr_search_subtitle_'+ cnt +'\">';
                            contents +=     '<td class=\"subtitle_num\" style=\"width:50px\">'+ cnt + '</td>';
                            contents +=     '<td class=\"subtitle_line\">'+ subtitle_line +'</td>';
                            contents += '</tr>';
                            contents +=     '<tr class=\"text-center subtitle_keyword\" id=\"tr_search_keyword_'+ cnt +'\" style=\"display:none\">'
                            +'<td><img src=\"/static/img/refresh.png\" style=\"width:20px\" class=\"refresh_keyword\" id=\"refresh_keyword_'+cnt+'\"></td><td>'
                            contents +=         '<input type=\"text\" onkeypress=\"enter_test('+cnt+')\" class=\"form-control\" value=\"\" style=\"width:100%\" id=\"search_keyword_'+ cnt +'\">'
                            contents +=     '</td></tr>'
                            contents +=     '<tr class=\"text-center subtitle_keyword\" id=\"tr_search_keyword_output_'+ cnt +'\" style=\"display:none\"><td></td><td>'
                            contents +=     '</td></tr>'
                            /*contents += '<tr class=\"text-center subtitle_back\">';
                            contents +=     '<td class=\"subtitle_num\"></td>';
                            contents +=     '<td><div class=\"col-12 input-group\">'
                            contents +=         '<input type=\"text\" class=\"form-control kw\" value=\"\">'
                            contents +=         '<div class=\"input-group-append\">'
                            contents +=             '<button class=\"btn btn-outline-secondary\" type=\"button\" id=\"btn_search\">검색</button>'
                            contents +=         '</div>'
                            contents +=     '</div></td>'
                            contents += '</tr>';*/
                            subtitle_line = "";
                            cnt++;
                        }
                        subtitle_line += res[i] + "</br>";
                    }
                    $('#subtitle_cnt').val(cnt);
                    $('#AddOption').append(contents); // 추가기능
                    //$('#download_ctrl').css('display','none');


                    var keywords = $('#keyword').val();

                    var res = keywords.split("\n");
                    var cnt = 1;
                    var subtitle_line = "";
                    for(var i in res) {
                        //console.log(res[i]);
                        var line = res[i];
                        st = line.split("|");
                        //console.log(st[0])
                        //console.log(st[1])
                        $('#search_keyword_'+st[0]).val(st[1]);

                        // 저장된 썸네일, 영상이 있을경우 불러옴
                        if(st[2] == undefined || st[2] == ''){
                        }
                        else{
                        $('#tr_search_keyword_output_'+st[0]).html("<td colspan='2'>"
                        +"<video class='thevideo img-fluid img-thumbnail' poster=" + st[2] + " loop='' preload='none' style='height:250px;'>"
                        +"<source class='btnImages selected' id='search_thumb_" + st[0] + "_1' src='" + st[3] + "' type='video/mp4'>"
                        +"</video>"
                        +"</td>");
                        }
                    }


                    $('.subtitle_line').click(function(){
                        var keyword = $(this).html();
                        //keyword = keyword.replaceAll("<button type=\"button\" class=\"btn btn-primary col-md-2\" id=\"go_cur\">이동</button>", "");
                        //alert(keyword);
                        //keyword = "얼마 전 아세안 동남아 국가연합 외교 장관회의가 열렸습니다."
                        //keyword = keyword.replace(" ", " ");
                        //keyword = keyword.replaceAll("</br>", " ");

                        //keyword = keyword.replaceAll("<br>", " ");
                        keyword = keyword.replace(/<br>/gi, " ");
                        //keyword = keyword.replaceAll("\u0020", " ");
                        keyword = keyword.slice(0, -1)
                        //alert(keyword);

                        var obj = document.getElementById("content");
                        var text = obj.value;

                        //text = text.replaceAll(" "," ");
                        //text = text.replaceAll("\n", " ");
                        text = text.replace(/ /gi," ");
                        text = text.replace(/\n/gi, " ");

                        //alert(text);
                        var pos = text.indexOf( keyword );
                        //alert(pos);

                        //pos = pos + 5;
                        if ( obj.setSelectionRange ) {
                            obj.focus();
                            obj.setSelectionRange(pos,pos);
                        } else if ( obj.createTextRange ) {
                            var c = obj.createTextRange();
                            c.move("character",pos);
                            c.select();
                        }
                    });

                    $('.refresh_keyword').click(function(){

                        var num = this.id;
                        num = num.replace('refresh_keyword_','');
                        var key = $('#search_keyword_'+num).val();


                        var url = '/pybo/upload/search/keyword?page=1&kw=';

                        if(key != null && key != undefined && key != ''){
                            window.open(url+key+'&num='+num, 'windowPop', 'width=1200, height=600, left=680, top=420, resizable = yes, location = no ')
                        }

                        /*var num = this.id;
                        num = num.replace('refresh_keyword_','');
                        var key = $('#search_keyword_'+num).val();
                        if(key != null && key != undefined && key != ''){
                            keywords = num+'|'+key;
                            console.log(keywords);
                            $.ajax({
                                type:"POST",
                                url: "/pybo/editor/keyword/search",
                                data: {
                                    keywords : keywords,
                                    qid : qid
                                },
                                success: function(data,status){ //status는 생략해도 됨
                                    var num = data['num'];
                                    var tr_str = $('#tr_search_keyword_output_'+num).html();
                                    console.log(tr_str);
                                    console.log("num : " + num);
                                    $('#tr_search_keyword_output_'+num).html("<td colspan='2'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_1' style='width:50%;border: 5px solid white' src='"+ data['1'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_2' style='width:50%;border: 5px solid white' src='"+ data['2'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_3' style='width:50%;border: 5px solid white' src='"+ data['3'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_4' style='width:50%;border: 5px solid white' src='"+ data['4'] + "'>"
                                    +"</td>");

                                    for(var j=1; j<=4; j++){
                                        $('#search_thumb_'+num+'_'+j).click(function(){
                                            if($(this).hasClass('selected')){
                                                $(this).toggleClass('selected');
                                                this.style = "width:50%;border: 5px solid white";
                                            }
                                            else{
                                                $(this).toggleClass('selected');
                                                this.style = "width:50%;border: 5px solid red";
                                            }
                                        });
                                    }

                                },
                                error: function(error){
                                    console.log(error.responseText);
                                }
                            });
                        }*/
                    });

                },
                error: function(error){
                    console.log(error.responseText);
                }
            });
        }
    }

    $(window).bind('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (String.fromCharCode(event.which).toLowerCase()) {
            case 's':
                event.preventDefault();
                var subject = $('#subject').val();
                var text = $('textarea#content').val();
                var qid = $('#qid').val();
                var status = $('#select_default').val();

                if(text == "" || text == null || text == "undefined"){
                    alert("내용은 필수항목입니다");
                    var obj = document.getElementById("content");
                    obj.focus();
                }
                else{
                    //subject = encodeURIComponent(subject);
                    //text = encodeURIComponent(text);
                    $.ajax({
                        type:"POST",
                        url: "/pybo/editor/create",
                        data: {
                            subject : subject,
                            content : text,
                            qid : qid,
                            status : status
                        },
                        success: function(data,status){ //status는 생략해도 됨
                            //alert("스크립트 저장됨");
                            console.log('/pybo/editor/create 성공');
                            $('.alert').css('display','');
                            $('#qid').val(data.qid);
                            //$('#next_step').css('display','');
                            if(data.status == 'create')
                                window.location.href = '/pybo/' + data.qid;


                            var cnt = $('#subtitle_cnt').val();
                            // 썸네일, 동영상 경로 같이 저장
                            var keywords = '';
                            for(var i=1; i<=cnt; i++){
                                var key = $('#search_keyword_'+i).val()
                                var src = $('#search_thumb_'+i+'_1').attr('src')
                                var thumb = $('#search_thumb_'+i+'_1').parent().attr('poster')


                                if(key != null && key != undefined && key != ''){
                                    if(src != undefined){
                                        keywords += i + '|' + key + '|' + thumb + '|' + src + '\n';
                                    }
                                    else{
                                        keywords += i + '|' + key + '||' + '\n';
                                    }
                                }
                            }

                            console.log(keywords);
                            $.ajax({
                                type:"POST",
                                url: "/pybo/editor/keyword/save",
                                data: {
                                    keywords : keywords,
                                    qid : qid
                                },
                                success: function(data,status){ //status는 생략해도 됨
                                    console.log('/pybo/editor/keyword/save 성공');
                                },
                                error: function(error){
                                    alert("에러")
                                    console.log(error.responseText);
                                }
                            });

                            setTimeout("$('.alert').css('display','none');", 2000);
                            $('#next_step').focus();
                            //$('#next_step').get(0).scrollIntoView(true);
                        },
                        error: function(error){
                            console.log(error.responseText);
                        }
                    });
                }
                break;
            /*
            case 'f':
                event.preventDefault();
                alert('ctrl-f');
                break;
            case 'g':
                event.preventDefault();
                alert('ctrl-g');
                break;
                */
            }
        }
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });



    $(function(){
        $('textarea#content').keyup(function(){
            bytesHandler(this);
            realtime_Check();
        });
    });

    function getTextLength(str) {
        var len = 0;

        for (var i = 0; i < str.length; i++) {
            if (escape(str.charAt(i)).length == 6) {
                len++;
            }
            len++;
        }
        return len;
    }

    function getTextLength_removeBlank(str) {
        var len = 0;

        str = str.replace(/ /g,"");
        return str.length;
    }

    function bytesHandler(obj){
        var text = $(obj).val();
        var output = '';
        output += '공백 포함 : ' + getTextLength(text)+' bytes ( 권장 8000 byte ), ';
        output += '공백 제거 : ' + getTextLength_removeBlank(text)+' ( 권장 3700 )';
        $('p.bytes').text(output);
        //console.log($('textarea#content').val());
    }




/*    $('#convert_1').click(function(){
            // ajax()에 {}객체 1개 전달
            console.log($('textarea#content').val());
            var text = $('textarea#content').val();
            text = encodeURIComponent(text);
            $.ajax({
                type:"POST",
                url: "/pybo/editor/convert",
                data: "content="+text,
                success: function(data,status){ //status는 생략해도 됨
                    $('#subtitle').val(data);
                },
                error: function(error){
                    console.log(error.responseText);
                }
            });
    });*/



    $('#cur').click(function(){
        var obj = document.getElementById("content");
        obj.focus();
    });


    $('#save_button').click(function(){
            var subject = $('#subject').val();
            var text = $('textarea#content').val();
            var qid = $('#qid').val();
            var status = $('#select_default').val();

            if(text == "" || text == null || text == "undefined"){
                alert("내용은 필수항목입니다");
                var obj = document.getElementById("content");
                obj.focus();
            }
            else{
                //subject = encodeURIComponent(subject);
                //text = encodeURIComponent(text);
                $.ajax({
                    type:"POST",
                    url: "/pybo/editor/create",
                    data: {
                        subject : subject,
                        content : text,
                        qid : qid,
                        status : status
                    },
                    success: function(data,status){ //status는 생략해도 됨
                        $('.alert').css('display','');
                        $('#qid').val(data.qid);
                        //('#next_step').css('display','');
                        if(data.status == 'create')
                            window.location.href = '/pybo/' + data.qid;

                        setTimeout("$('.alert').css('display','none');", 2000);
                        $('#next_step').focus(); // 커서 이동
                        //$('#next_step').get(0).scrollIntoView(true); // 스크롤 이동
                    },
                    error: function(error){
                        console.log(error.responseText);
                    }
                });
            }
    });


    $('#next_step').click(function(){
        qid = $('#qid').val();
        if(qid == "" || qid == null || qid == "undefined"){
           alert("스크립트를 입력 후 저장해주세요.")
        }
        else{
           $('#content_field').css('display','none');
           $('#subtitle_field').attr('class','col-md-12');
           $('#tooltip_1').css('display','none');
           $('#next_step').css('display','none');
           $('#subtitle_field').scrollTop(0);
           $('#subtitle_field').css('height','100%');
           $('.subtitle_keyword').css('display','');

           $('#download_ctrl').css('display','');


        }
    });


    $('#step_back1').click(function(){
           $('#content_field').css('display','');
           $('#subtitle_field').attr('class','col-md-6');
           $('#tooltip_1').css('display','');
           $('#next_step').css('display','');
           $('#subtitle_field').scrollTop(0);
           $('#subtitle_field').css('height','700px');
           $('.subtitle_keyword').css('display','none');

           $('#download_ctrl').css('display','none');

    });


    $('#search_keyword').click(function(){
        var cnt = $('#subtitle_cnt').val();
        var keywords = '';
        for(var i=1; i<=cnt; i++){
            var key = $('#search_keyword_'+i).val()
            if(key != null && key != undefined && key != '')
                keywords += i+'|'+key+'\n';
        }

        console.log(keywords);
        $.ajax({
                    type:"POST",
                    url: "/pybo/editor/keyword",
                    data: {
                        keywords : keywords,
                        qid : qid
                    },
                    timeout: 1000,
                    success: function(data,status){ //status는 생략해도 됨
                        //window.location.href = '/static/keyword/'+ qid + '/keyword.zip';
                    },
                    error: function(error){
                        alert("다운로드 진행중입니다.");
                        window.location.href = '/pybo/';
                    },
                    fail: function(){
                        alert("다운로드 진행중입니다.");
                        window.location.href = '/pybo/';
                    }
        });
    });




    $('#only_search_keyword').click(function(){
        var cnt = $('#subtitle_cnt').val();
        var keywords = '';
        for(var i=1; i<=cnt; i++){
            var key = $('#search_keyword_'+i).val()
            if(key != null && key != undefined && key != ''){
                keywords = i+'|'+key;
                console.log(keywords);
                $.ajax({
                            type:"POST",
                            url: "/pybo/editor/keyword/search",
                            data: {
                                keywords : keywords,
                                qid : qid
                            },
                            success: function(data,status){ //status는 생략해도 됨
                                var num = data['num'];
                                var tr_str = $('#tr_search_keyword_output_'+num).html();
                                console.log(tr_str);
                                console.log("num : " + num);
                                $('#tr_search_keyword_output_'+num).html("<td colspan='2'>"
                                +"<img class='btnImages' id='search_thumb_"+num+"_1' style='width:50%;border: 5px solid white' src='"+ data['1'] + "'>"
                                +"<img class='btnImages' id='search_thumb_"+num+"_2' style='width:50%;border: 5px solid white' src='"+ data['2'] + "'>"
                                +"<img class='btnImages' id='search_thumb_"+num+"_3' style='width:50%;border: 5px solid white' src='"+ data['3'] + "'>"
                                +"<img class='btnImages' id='search_thumb_"+num+"_4' style='width:50%;border: 5px solid white' src='"+ data['4'] + "'>"
                                +"</td>");

                                for(var j=1; j<=4; j++){
                                    $('#search_thumb_'+num+'_'+j).click(function(){
                                        if($(this).hasClass('selected')){
                                            $(this).toggleClass('selected');
                                            this.style = "width:50%;border: 5px solid white";
                                        }
                                        else{
                                            $(this).toggleClass('selected');
                                            this.style = "width:50%;border: 5px solid red";
                                        }
                                    });
                                }


                            },
                            error: function(error){
                                //alert("다운로드 진행중입니다.");
                                //window.location.href = '/pybo/';
                            },
                            fail: function(){
                                //alert("다운로드 진행중입니다.");
                                //window.location.href = '/pybo/';
                            }
                });
                keywords = '';
            }

        }
    });



    $('#only_search_keyword_download').click(function(){
        var length = $("[class*='btnImages selected']").length;

        srcList = ''
        for(var i=0; i<length; i++){
            if(i==length-1)
                srcList += $("[class*='btnImages selected']")[i].id + "|" + $("[class*='btnImages selected']")[i].src;
            else
                srcList += $("[class*='btnImages selected']")[i].id + "|" + $("[class*='btnImages selected']")[i].src + "\n";
        }

        console.log(srcList);

        if(length > 0){
            $.ajax({
                type:"POST",
                url: "/pybo/editor/keyword/selectdown",
                data: {
                    keywords : srcList,
                    qid : qid
                },
                timeout: 1000,
                success: function(data,status){ //status는 생략해도 됨
                    alert("다운로드 진행중입니다.\n작업이 완료되면 리스트화면에 Down 아이콘이 표시됩니다.");
                    window.location.href = '/pybo/';
                },
                error: function(error){
                    alert("다운로드 진행중입니다.\n작업이 완료되면 리스트화면에 Down 아이콘이 표시됩니다.");
                    window.location.href = '/pybo/';
                },
                fail: function(){
                    alert("다운로드 진행중입니다.\n작업이 완료되면 리스트화면에 Down 아이콘이 표시됩니다.");
                    window.location.href = '/pybo/';
                }
            });
        }
    });



    $('#save_keyword').click(function(){
        $('.alert').css('display','');
        save_keyword();
        setTimeout("$('.alert').css('display','none');", 2000);
    });

    function save_keyword(){
        var cnt = $('#subtitle_cnt').val();

        var keywords = '';
        for(var i=1; i<=cnt; i++){
            var key = $('#search_keyword_'+i).val()
            var src = $('#search_thumb_'+i+'_1').attr('src')
            var thumb = $('#search_thumb_'+i+'_1').parent().attr('poster')

            if(key != null && key != undefined && key != ''){
                if(src != undefined){
                    keywords += i + '|' + key + '|' + thumb + '|' + src + '\n';
                }
                else{
                    keywords += i + '|' + key + '||' + '\n';
                }
            }
        }



        console.log(keywords);
        $.ajax({
            type:"POST",
            url: "/pybo/editor/keyword/save",
            data: {
                keywords : keywords,
                qid : qid
            },
            success: function(data,status){ //status는 생략해도 됨
                console.log('/pybo/editor/keyword/save 성공');
            },
            error: function(error){
                alert("에러")
                console.log(error.responseText);
            }
        });
    }

});


function enter_test(num) {
    if ( window.event.keyCode == 13 ) {
                        var key = $('#search_keyword_'+num).val();


                        var url = '/pybo/upload/search/keyword?page=1&kw=';

                        if(key != null && key != undefined && key != ''){
                            window.open(url+key+'&num='+num, 'windowPop', 'width=1200, height=600, left=680, top=420, resizable = yes, location = no ')
                        }

                        /*var key = $('#search_keyword_'+num).val();
                        if(key != null && key != undefined && key != ''){
                            keywords = num+'|'+key;
                            console.log(keywords);
                            $.ajax({
                                type:"POST",
                                url: "/pybo/editor/keyword/search",
                                data: {
                                    keywords : keywords,
                                    qid : qid
                                },
                                success: function(data,status){ //status는 생략해도 됨
                                    var num = data['num'];
                                    var tr_str = $('#tr_search_keyword_output_'+num).html();
                                    console.log(tr_str);
                                    console.log("num : " + num);
                                    $('#tr_search_keyword_output_'+num).html("<td colspan='2'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_1' style='width:50%;border: 5px solid white' src='"+ data['1'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_2' style='width:50%;border: 5px solid white' src='"+ data['2'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_3' style='width:50%;border: 5px solid white' src='"+ data['3'] + "'>"
                                    +"<img class='btnImages' id='search_thumb_"+num+"_4' style='width:50%;border: 5px solid white' src='"+ data['4'] + "'>"
                                    +"</td>");

                                    for(var j=1; j<=4; j++){
                                        $('#search_thumb_'+num+'_'+j).click(function(){
                                            if($(this).hasClass('selected')){
                                                $(this).toggleClass('selected');
                                                this.style = "width:50%;border: 5px solid white";
                                            }
                                            else{
                                                $(this).toggleClass('selected');
                                                this.style = "width:50%;border: 5px solid red";
                                            }
                                        });
                                    }

                                },
                                error: function(error){
                                    console.log(error.responseText);
                                }
                            });
                        }*/
    }
}