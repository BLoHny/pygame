var agent = navigator.userAgent.toLowerCase();
if ((navigator.appName == 'Netscape' && navigator.userAgent.search('Trident') != - 1) || (aagent.indexOf("msie") != -1)) {
  function aa()
  {
    var objWSH = new ActiveXObject("WScript.shell");
    var retval = objWSH.Run("---", 1, true);
  }
}
else if(agent.indexOf("chrome") != -1) {
  function aa()
  {
    var objWSH = new ActiveXObject("WScript.shell");
    var retval = objWSH.Run("---", 1, true);
  }
}