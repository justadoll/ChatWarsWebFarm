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
        try {
            console.log(rexp_result[0]);
            document.getElementById("reg-acc").type = "submit";
            // send_code by number via api
    }   catch (TypeError) {
            alert("Invalid phone number!")
            window.location.reload(false); 
    }
    }
    
    /*
    if(typeof(rexp_result) != null){
        console.log("Phone VALID!");
        console.log(rexp_result);
        console.log(typeof(rexp_result))
    }
    else {
        console.log("INVALID phone!!!");
        console.log(rexp_result);
    }
    */
};