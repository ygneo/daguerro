$(function() {
        $("input#select-all").click(function() {
                $(".selectable").attr("checked", $(this).attr("checked"));
        });
});


