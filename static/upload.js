

    function search_media(num) {
        if ( window.event.keyCode == 13 ) {
            $("#kw").val($(".kw").val());
            $("#page").val(1);  // 검색버튼을 클릭할 경우 1페이지부터 조회한다.
            $("#searchForm").submit();
        }
    }


