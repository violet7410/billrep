function ToggleExpandText(aObj, target) {

    console.log('object: ', aObj);
    console.log('target: ', target);

    currentClass = aObj.className;
    flag = 0;
    if (currentClass.localeCompare('expandText1') == 0) {
        flag = 1;
    } 

    var displayText;
    var aClassName;
    var divClassName;
    if (flag == 1) {
        // show expand text
        displayText  = '- ' + aObj.innerHTML.substring(2);
        aClassName   = 'expandText2';
        divClassName = 'expandText';
    } else {
        // hide expand text
        displayText  = '+ ' + aObj.innerHTML.substring(2);
        aClassName   = 'expandText1';
        divClassName = 'collapseText';
    }

    var em = document.getElementById(target);

    aObj.innerHTML = displayText;
    aObj.className = aClassName;
    em.className   = divClassName;
}


function CopyToClipboard(obj, target) {
    console.log('object: ', obj);
    console.log('target: ', target);
    
    var em = document.getElementById(target);
    // Create a text area
    const el = document.createElement("textarea");
    // el.value = em.innerHTML;
    el.innerHTML = em.innerHTML;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    // remove text area
    document.body.removeChild(el);


    // Popup Copied text
    const popup = document.createElement("div");
    popup.innerHTML =  'Copied to clipboard';
    var rect = obj.getBoundingClientRect();
    popup.style.left = Math.round(rect.right + window.scrollX + 10) + 'px';
    popup.style.top = Math.round(rect.top + window.scrollY) + 'px';
    popup.className = 'popup';
    document.body.appendChild(popup);

    setTimeout(function(){
        document.body.removeChild(popup);
     }, 200);
}


function sortTable(tabName, colIdx, isNumber) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById(tabName);
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  
  /*Make a loop that will continue until
  no switching has been done:*/
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
      x = rows[i].getElementsByTagName("TD")[colIdx];
      y = rows[i + 1].getElementsByTagName("TD")[colIdx];
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (dir == "asc") {
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
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
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

function maxtest() {
    alert('max here');
}