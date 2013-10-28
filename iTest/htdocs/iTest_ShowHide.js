function display_hidn(id) 
{
    var a_table = document.getElementById(id);
    var current = a_table.style.display;
    if (current == 'block')
    {
        a_table.style.display='none';
    }
    else
    {
        a_table.style.display='block';
    }
}




function show_new(id)
{
    var t=document.all.myCRListTable_PS.rows;
    var itest_counter = 0 ;
    var psit_counter = 0 ;
    var all_counter = 0 ;
    for(var i=1;i< t.length;i++)
    { 
        if(id=='')
        {
            t(i).style.display='block';
            if (t(i).cells(4).innerText=='1')
            {
                itest_counter = itest_counter +1;
            }
            if (t(i).cells(5).innerText!='null')
            {
                psit_counter = psit_counter +1;
            }
            all_counter = all_counter +1;
        }
        else
        {
            if (t(i).id==id)
            {
                t(i).style.display='block';
                if (t(i).cells(4).innerText=='1')
                {
                    itest_counter = itest_counter +1;
                }
                if (t(i).cells(5).innerText!='null')
                {
                    psit_counter = psit_counter +1;
                }
                all_counter = all_counter +1;
            }
            else
            {
                t(i).style.display='none';
            }
       }
    }
    if(all_counter==0)
    {
        document.all.iTest_Statis.innerText='';
        document.all.PSIT_Statis.innerText='';
        document.all.PS_Statis.innerText='0';
    }
    else
    {
        document.all.iTest_Statis.innerText=Math.round(itest_counter/all_counter*100);
        document.all.PSIT_Statis.innerText=Math.round(psit_counter/all_counter*100);
        document.all.PS_Statis.innerText=all_counter;
    }
}

function show(id)
{
    var t=document.all.myCRListTable_PS.rows;

    for(var i=1;i< t.length;i++)
    { 
        if(id=='')
        {
            t(i).style.display='block';
        }
        else
        {
            if (t(i).id==id)
            {
                    t(i).style.display='block';
            }
            else
            {
                t(i).style.display='none';
            }
       }
    }
    show_new(id);
}


