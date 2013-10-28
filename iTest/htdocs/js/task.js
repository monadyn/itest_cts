
function getProjectControl(str)
     {
         var xmlhttp;
         if (str=="")
         {
             document.getElementById("task_Product_C").innerHTML="";
             return;
         }
         if (window.XMLHttpRequest)
         {// code for IE7+, Firefox, Chrome, Opera, Safari
             xmlhttp=new XMLHttpRequest();
         }
         else
         {// code for IE6, IE5
             xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
         }
         xmlhttp.onreadystatechange=function()
         {
           if (xmlhttp.readyState==4 && xmlhttp.status==200)
           {
              document.getElementById("task_Product_C").innerHTML=xmlhttp.responseText;
           }
         }
         xmlhttp.open("GET","/trac/task/getprojectcontrol?Product_ID="+str+"&nocache="+Math.random(),false);
         xmlhttp.send();
     }
