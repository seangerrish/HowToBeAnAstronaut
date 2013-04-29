(function () {
    var r_html = "\u003Cdiv class\u003D\u0022section\u002Ditem recommendations\u002Dcontent\u0022\u003E\u000A    \u003Cdiv\u003E\u000A        \u003Cdiv class\u003D\u0022section_title\u0022 style\u003D\u0022border\u002Dbottom:none\u003B padding\u002Dbottom:0px\u0022\u003E\u000A            \u003Ch2\u003E\u000A                Endorsements \u000A            \u003C/h2\u003E\u000A        \u003C/div\u003E\u000A    \u003C/div\u003E\u000A    \u003Cdiv class\u003D\u0022items\u002Dcontainer\u0022\u003E\u000A        \u003Cdiv class\u003D\u0022data_display\u0022\u003E\u000A            \u000A            \u000A                \u003Cdiv\u003E\u000A                    Be the first to \u003Ca href\u003D\u0022https://endorse.indeed.com/endorse?r\u003D0fcdbf290fe25878\u0026amp\u003Bfrom\u003Dview_resume\u0026amp\u003Bcontinue\u003Dhttp%3A%2F%2Fwww.indeed.com%2Fr%2F0fcdbf290fe25878\u0022\u003Eendorse Apolynn\u003C/a\u003E\u000A                \u003C/div\u003E\u000A            \u000A        \u003C/div\u003E\u000A    \u003C/div\u003E\u000A\u003C/div\u003E\u000A";
    var r_el = document.createElement('div');
    r_el.innerHTML = r_html;
    var rez_body = document.getElementById("resume_body");
    rez_body.appendChild(r_el);
    var rpc_url = "http://www.indeed.com/resumes/rpc/log/endorsements?endsShown\u003D0\u0026viewTk\u003D17mb1uau11daa7u6\u0026tk\u003D17mb1u9961daa6h4";
    var rpcLog = function(href){ if (Image) { (new Image()).src = href; } };
    rpcLog(rpc_url);
})();