
	
function checkStatus(tmanager_type, test_id, testname)
{
	
	var tmp = "&tmanager_type="+tmanager_type;
        tmp += "&testid=" + test_id;
        tmp += "&testname=" + testname; 
    var url = "http://itest-center/iTest/build?passed_test_nums=all" +tmp;        

    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
	
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
            //alert('XMLHttpReq.send: 1responseText ='+XMLHttpReq.responseText);
            document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
		else
		{
		    //alert('XMLHttpReq.send: readyState ='+XMLHttpReq.readyState);
		}
    }
	
    //var tmp = "?inprogress_test_case=all";
	//tmp = tmp + "&test_id=" + test_id; 	
	//url = "http://itest-center/iTest/build"+tmp
    XMLHttpReq.open("GET",url, true);	

	//alert('XMLHttpReq.send: 2responseText ='+XMLHttpReq.responseText);
    XMLHttpReq.send(null);
	//alert('XMLHttpReq.send: url='+url);
	//XMLHttpReq.responseText = "";
    //setInterval("get_info_inprogress_case("+test_id+")", 5000)
	//setTimeout("get_info_inprogress_case("+test_id+")", 5000);
	
}

function createXMLHttpRequest()
{
	XMLHttpReq=null;
	if(window.ActiveXObject)
        { 
            XMLHttpReq=new ActiveXObject("Microsoft.XMLHTTP"); 
        }
        else if(window.XMLHttpRequest)
        { 
            XMLHttpReq=new XMLHttpRequest(); 
        } 
} 


function getdetail(id)
{
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?action=ajax&Label_ID=" + id;    
    tmp = tmp + "&cache=" + Math.random();
    XMLHttpReq.open("GET","/trac/irelease/versiontree/buglist"+tmp,true);
    XMLHttpReq.send();
}

function get_buglist_dynamic(id,mylabel)
{   
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?action=ajax&Branch_ID=" + id;   
    tmp = tmp + "&Label_Name=" + mylabel; 
    tmp = tmp + "&cache=" + Math.random();
    XMLHttpReq.open("GET","/trac/irelease/branchtree/buglist"+tmp,true);
    //XMLHttpReq.open("GET","/trac/iTest/build/testsheet/20907",true);

    XMLHttpReq.send();
}

function get_buglist_dynamic_sync(id,mylabel)
{   
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?action=ajax&Branch_ID=" + id;   
    tmp = tmp + "&Label_Name=" + mylabel; 
    tmp = tmp + "&sync=1"; 
    tmp = tmp + "&cache=" + Math.random();
    XMLHttpReq.open("GET","/trac/irelease/branchtree/buglist"+tmp,true);
    XMLHttpReq.send();
}


function get_buglist_dynamic_init(id,mylabel)
{   
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?action=ajax&Branch_ID=" + id;   
    tmp = tmp + "&Label_Name=" + mylabel; 
    tmp = tmp + "&cache=" + Math.random();
    XMLHttpReq.open("GET","/trac/irelease/branchtree/buglist"+tmp,true);
    XMLHttpReq.send();
}

function tManagerTree_Agent(id,tmanager_type, starter, agent)
{
    //alert(id);
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    //var tmp = "?tmanager="+tmanager_type;
	//tmp = tmp + "&starter=" + starter; 
	//tmp = tmp + "&agent=" + agent;
    //XMLHttpReq.open("GET","http://itest-center/iTest/build"+tmp,true);
	

	var tmp = "?ajax=Agent";
	tmp = tmp + "&StarterIP=" + starter;
	tmp = tmp + "&AgentPort=" + agent;
    XMLHttpReq.open("GET","http://itest-center/iTest/itest/ServerManager/home/"+tmanager_type+tmp,true);
	
    XMLHttpReq.send();
	
}

function tManagerTree_Starter(id,tmanager_type, starter)
{
    //alert('tManagerTree_Starter');
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    //var tmp = "?tmanager="+tmanager_type;
	//tmp = tmp + "&starter=" + starter; 
    //XMLHttpReq.open("GET","http://itest-center/iTest/build"+tmp,true);

	var tmp = "?ajax=Starter";
	tmp = tmp + "&StarterIP=" + starter;
    XMLHttpReq.open("GET","http://itest-center/iTest/itest/ServerManager/home/"+tmanager_type+tmp,true);	
    //XMLHttpReq.open("GET","/itest/ServerManager/home/"+tmanager_type+tmp,true);	
    //alert('ok');
    XMLHttpReq.send();
	
}


function tManagerTree_tManager(id,tmanager_type)
{
	//alert('tManagerTree_tManager');
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    //var tmp = "?tmanager="+tmanager_type;
    //XMLHttpReq.open("GET","http://itest-center/iTest/build"+tmp,true);

	var tmp = "?ajax=tManager";
    XMLHttpReq.open("GET","http://itest-center/iTest/itest/ServerManager/home/"+tmanager_type+tmp,true);
    //alert('ok');
    XMLHttpReq.send();
	
}




function get_info_dynamic(id,tmanager_type, starter, agent)
{
    //alert(id);
    document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?tmanager="+tmanager_type;
	tmp = tmp + "&starter=" + starter; 
	tmp = tmp + "&agent=" + agent;
    XMLHttpReq.open("GET","http://itest-center/iTest/build"+tmp,true);
	

    XMLHttpReq.send();
	
}

function submit_bug()
{
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
        }
    }
    var tmp = "?action=newbug";    
    tmp = tmp + "&Label_ID=" + encodeURI(document.getElementById("Label_ID").value);
    tmp = tmp + "&Bug_ID=" + encodeURI(document.getElementById("Bug_ID").value);
    tmp = tmp + "&Merger=" + encodeURI(document.getElementById("Merger").value);
    tmp = tmp + "&cache=" + Math.random();
	XMLHttpReq.open("GET","/trac/irelease/versiontree/buglist"+tmp,true);
	XMLHttpReq.send();
    document.all["cur_edit_id"].value = "";
}
