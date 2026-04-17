/* ---------------------------------------------------------------------
#   File:       default.ts
#   Created:    30-May-2023 21:21:21
#   Creator:    xchavon  (Chatchai Vongpratoom)
#   $Revision: 1.1 $
#   $Source: /svw/svbranch/admin/repository/attool/billrep/src/default.ts,v $
# ----------------------------------------------------------------------
#   DESCRIPTION
#   DO NOTE!! modify default.js
#   This file is generated from from $ATAI_TEST_BASE/billrep/src/default.ts
#   To generate default.js run following command
#
#     tsc -w
#
-----------------------------------------------------------------------*/
function ToggleExpandText(aObj : HTMLElement, targetName : string) {
    console.log(aObj);
    console.log(targetName);

    let currentClass = aObj.className;
    let flag : number = 0;
    if (currentClass.localeCompare("expandText1") == 0) {
        flag = 1;
    }

    let displayText  : string;
    let aClassName   : string;
    let divClassName : string;

    // Assign displayText
    displayText = "- " + aObj.innerHTML.substring(2);

    if (flag == 1) {
        // show expand text
        aClassName   = "expandText2";
        divClassName = "expandText";
    } else {
        // hide expand text
        aClassName   = "expandText2";
        divClassName = "expandText";
    }

    let em = document.getElementById(targetName);
    
    aObj.innerHTML = displayText;
    aObj.className = aClassName;

    if (em) {
        em.className   = divClassName;
    }

}


function CopyToClipboard(obj : HTMLElement, target : string) {
    console.log("object : ", obj);
    console.log("target : ", target);

    let em = document.getElementById(target);
    // Create a text area
    const el = document.createElement("textarea");
    // el.value = em.innerHTML;
    el.innerHTML = em?.innerHTML!;

    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    // remove text area
    document.body.removeChild(el);

    // Popup Copied text
    const popup = document.createElement("div");
    popup.innerHTML = "Copied to clipboard";
    let rect = obj.getBoundingClientRect();
    popup.style.left = Math.round(rect.right + window.scrollX + 10) + "px";
    popup.style.top  = Math.round(rect.top + window.scrollY) + "px";
    popup.className  = "popup";
    document.body.appendChild(popup);

    setTimeout(function() {
        document.body.removeChild(popup);
    }, 200);

}


function sortTable(tabName : string, colIdx : number, isNumber : boolean) {
    let rows : HTMLCollectionOf<HTMLTableRowElement>;
    let switching : boolean = true;
    let shouldSwitch : boolean = true;
    let i : number;
    let dir : string;
    let switchcount : number = 0;
    let table = document.getElementById(tabName) as HTMLTableElement;
    //Set the sorting direction to ascending:
    dir = "asc";
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /*Loop through all table rows (except the
        first, which contains table headers):*/
        for (i = 1; i < (rows.length - 1); i++) {
            //start by saying there should be no switching:
            shouldSwitch = false;
            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            let x = rows[i].getElementsByTagName("TD")[colIdx];
            let y = rows[i + 1].getElementsByTagName("TD")[colIdx];
            /*check if the two rows should switch place,
            based on the direction, asc or desc:*/
            if (dir == "asc")  {
                if (isNumber) {
                    if (Number(x.innerHTML) > Number(y.innerHTML)) {
                        shouldSwitch = true;
                        break;
                    }
                } else {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch= true;
                        break;
                    }
                }
            } else if (dir == "desc") {
                if (isNumber) {
                    if (Number(x.innerHTML) < Number(y.innerHTML)) {
                        shouldSwitch = true;
                        break;
                    }
                } else {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        } 

        if (shouldSwitch) {
            /*If a switch has been marked, make the switch
            and mark that a switch has been done:*/
            rows[i].parentNode?.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            //Each time a switch is done, increase this count by 1:
            switchcount++; 
        } else {
            /*If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again.*/
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}    



/* ---------------------------------------------------------------------
#   REVISION HISTORY
#   $Log: default.ts,v $
#   Revision 1.1  2023/06/15 11:24:53  xchavon
#   Initial version
#
-----------------------------------------------------------------------*/