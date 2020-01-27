function getCookie(cookieName) {
    var strCookie = document.cookie;
    var arrCookie = strCookie.split("; ");
    for(let i = 0; i < arrCookie.length; i++){
        let arr = arrCookie[i].split("=");
        if(cookieName === arr[0]){
            return arr[1];
        }
    }
    return "";
}
function setCookie(c_name, value, expiredays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + expiredays);
    document.cookie = c_name + "=" + escape(value) + ";max-age=" + (-1) + ";path=/";
}
function clearCookie(name) {
    setCookie(name, "", -1);
}