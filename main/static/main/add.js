function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const delay = ms => new Promise(res => setTimeout(res, ms));

const get_qr = async () => {
    $.ajax({
        url: "upd/",
        success: function(data, status) {
            alert("Captured session, now click CREATE player");
            console.log("data:",data);
            document.getElementById("reg-acc").type = "submit";
            //data['session_string']
            document.getElementById("id_session").value = data['session_string'];
        },
        error: function(data, status){
            if (data.status == 401) {
                alert("Disable 2FA pls!");
            }
            else if(data.status == 408){
                alert("Timeout, click \"Update QR\"");
            }
            else{
                alert("Some unknow error...");
                console.log("Error data:", data);
            }
        },
        timeout: 35000,
    });
    await delay(3500);
    $.get("get_qr/",function(data,status){
        var parser = new DOMParser();
        var get_html = parser.parseFromString(data, 'text/html');
        var new_img_src = get_html.getElementsByTagName("img")[0].src;
        console.log(new_img_src);
        document.getElementById("qr-code").src = new_img_src;
    });
}
/*
const send_code = () => {
    username_input = document.getElementById("id_username").value;
    phone_input = document.getElementById("id_phone_number").value;
    if(username_input==null || username_input=="", phone_input==null || phone_input=="") {
        alert("Fill all forms pls!")
        return false;
    }
    else {
        phone_exp = /^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$/g
        rexp_result = phone_input.match(phone_exp);
        if(typeof(rexp_result) != null){
                console.log("Phone VALID!");
                console.log("Phone from regex: ",rexp_result[0]);
                document.getElementById("input-code").type = "text"
                document.getElementById("reg-acc").type = "submit";
                const csrftoken = getCookie('csrftoken');
                $.ajax({
                    type: 'PUT',
			        dataType: 'json',
			        url: `send_code/`,
			        headers: {"X-HTTP-Method-Override": "PUT", 'X-CSRFToken': csrftoken},
			        mode: 'same-origin',
			        dataType: "json",
			        data: `{"phone_number":"${rexp_result[0]}"}`,
                })
        }
        else {
            console.log("INVALID phone!!!");
        }
    }
};
*/
