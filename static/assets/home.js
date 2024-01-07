let page_no = 1
var data = {};
var response_data = {}
window.onload = check_auth_status();
function check_auth_status() {
    let url = "https://operationdesk.easebuzz.in/old_data_req/auth_status";
    fetch(url, {
        withCredentials: true,
        credentials: 'same-origin',
        method: 'POST',
        headers: {
            // 'X-CSRFToken': "{{csrf_token}}",    
            'Content-Type': 'application/json',
        },
    },
        data = {}
    ).then(function (response) {
        return response.json()
    }).then(function (data) {
        if (data.detail)
            location.href = "https://operationdesk.easebuzz.in/old_data_req/login";
        else {
            document.getElementById("card_form").style.visibility = "visible";
        }
    });
}

async function call_JsApi(page_no) {
    card_no = document.getElementById('card_no').value
    bank_ref_num = document.getElementById('bank_ref_num').value
    amount = document.getElementById('amount').value
    pan_id = document.getElementById('pan_id').value
    account_no = document.getElementById("account_no").value
    product_identifier_id = document.getElementById("product_identifier")
    product_identifier = product_identifier_id.options[product_identifier_id.selectedIndex].text;
    page_no = page_no

    if (card_no == "" && bank_ref_num == "" && amount !== "" && pan_id == "") {
        alert("Please Enter Card number OR Bank ref number")
        table.hidden = true;
        showloader(state = "OFF").hide()
    }
    else if (account_no !="" && product_identifier == '---Select Product---'){
        table = document.getElementById("OperationalData");
        table.hidden = true;
        alert("Please Select the Product")
        showloader(state = "OFF").hide()

    }
    else if (card_no == "" && bank_ref_num == "" && amount == "" && pan_id == "" && account_no == "" && product_identifier =="---Select Product---") {
        alert("Please Enter the Details")
        showloader(state = "OFF").hide()
    }
    else if ((pan_id!==null || pan_id!=="") &&  (product_identifier=="PG" || product_identifier=="WIRE" || product_identifier=="INSTACOLLECT") && (account_no=="" && card_no=="" && bank_ref_num=="" && amount=="")){
        alert("Please enter only Pan ID")
        showloader(state = "OFF").hide()
    }
    else if (pan_id != "" && account_no != "") {
        table = document.getElementById("OperationalData");
        table.hidden = true;
        alert("Please Enter Either PAN ID OR Account Number")
        showloader(state = "OFF").hide()
    }
    else if ((pan_id !== null || pan_id !== "") && (card_no == "" && bank_ref_num == "" && amount == "" && account_no == "")) {
        api_url = `https://operationdesk.easebuzz.in/old_data_req/CN/?pan_id=${pan_id}`;

    }
    else if ((account_no !==null || account_no !== "" && product_identifier!=="" && page_no=="") && (card_no == "" && bank_ref_num == "" && amount == "" && pan_id == "")) {
        api_url = `https://operationdesk.easebuzz.in/old_data_req/CN/?account_no=${account_no}&product_identifier=${product_identifier}&page_no=${10*page_no}`;
    }
    else if ((pan_id !== "" || account_no !== "") && (card_no !== "" || bank_ref_num !== "" || amount !== "")) {
        table = document.getElementById("OperationalData");
        table.hidden = true;
        alert('Please Enter either Merchant Details OR Transactional Details.')
        showloader(state = "OFF").hide()

    }
    else if (card_no !== "" && bank_ref_num !== "" && amount == "" && pan_id == "" && account_no == "" && product_identifier =="") {
        api_url = `https://operationdesk.easebuzz.in/old_data_req/CN/?peb_card_number=${card_no}&bank_ref_number=${bank_ref_num}`;
    } else {
        api_url = `https://operationdesk.easebuzz.in/old_data_req/CN/?peb_card_number=${card_no}&bank_ref_number=${bank_ref_num}&amount=${amount}`;
    }
    // Storing response
    showloader(state = "ON")
    const response = await fetch(api_url);
    if (response.status === 403)
        window.location.href = "https://operationdesk.easebuzz.in/old_data_req/login";
    // Storing data in form of JSON
    data = await response.json();
    showloader(state = "OFF")
    if (pan_id !== null && pan_id !== "") {
        if (data.data.success === false) {
            table = document.getElementById("OperationalData");
            table.hidden = true;
            alert("Merchant details not found for the given PAN.")
            return
        }
        else {
            table = document.getElementById("OperationalData");
            table.hidden = false;
            response_data = data.data
            show_pan_info(response_data)
        }

    }
    else if (account_no !== null && account_no !== "" && product_identifier!=="" && product_identifier!==null)  {
        if (data.data.success === false) {
            table = document.getElementById("OperationalData");
            table.hidden = true;
            alert("Merchant details not found for the selected Product.")
            return
        }
        else {
            table = document.getElementById("OperationalData");
            table.hidden = false;
            response_data = data.data.merchant_details

            if (product_identifier == 'WIRE'){
                show_wire_account_details(response_data)
                pagination(data.data.count)
            }
            if (product_identifier == 'PG'){
                show_pg_account_details(response_data)
                pagination(data.data.count)
            }
            if (product_identifier == 'INSTACOLLECT'){
                show_instacollect_account_details(response_data)
                pagination(data.data.count)
            }
        }
    }

    else if (!data.data.length) {
        table = document.getElementById("OperationalData");
        table.hidden = true;
        // console.log("going here----")
        alert("Transaction Not Found for given details.")
        // alert("Please Enter the details")
        return
    }
    else {
        table = document.getElementById("OperationalData");
        table.hidden = false;
        response_data = data.data
        show(response_data);
    }
}

function file_download() {
    let selectItem = document.getElementById('myList1');
    if (selectItem.value === "to_csv") {
        Download_csv()
    }
}


/////////////////////////////////////////////////////////////



// Function to define innerHTML for HTML table
function show(data) {
    let tab =
        `<table border ='1' style='border-collapse:collapse'><tr>
    <th>Transaction ID</th>
    <th>Card Number</th>
    <th>Amount</th>
    <th>Transaction Ref Number</th>
    <th>Bank Ref Number</th>
    <th>Transaction Status</th>
    <th>Transaction Date</th>
    <th>Merchant ID</th>
    <th>Submerchant ID</th>
    </tr><table>`;

    // Loop to access all rows
    for (let r of data) {
        tab += `<tr>
<td>${r.peb_transaction_id} </td>
<td>${r.peb_card_number}</td>
<td>${r.amount}</td>
<td>${r.transaction_ref_num}</td>
<td>${r.bank_ref_num}</td>	
<td>${r.peb_transaction_status}</td>		
<td>${r.peb_transaction_date}</td>		
<td>${r.peb_merchant_id}</td>		
<td>${r.peb_submerchant_id}</td>				
</tr>`;
    }
    // Setting innerHTML as tab variable
    document.getElementById("OperationalData").innerHTML = tab;
}

function showloader(state = 'OFF') {
    if (state == 'OFF') {
        document.querySelector(".customloader").classList.remove('loader');
    }
    else {
        document.querySelector(".customloader").classList.add('loader');
    }

}

function call_logoutApi() {
    window.location = 'https://operationdesk.easebuzz.in/old_data_req/logout';

}

function Download_csv() {
    if (response_data.constructor == Object) {
        response_data = [response_data]
    }
    var column_name = []
    var row_details = []
    var table_rows = []
    for (const [key, value] of Object.entries(response_data[0])) {
        column_name.push(key)
    }
    for (var i = 0; i < response_data.length; i++) {
        row_details = []
        for (const [key, value] of Object.entries(response_data[i])) {
            row_details.push(value)
        }
        table_rows.push(row_details)
    }
    title = ""
    title += column_name + ",";
    var file_data_values = "";
    for (var i = 0; i < table_rows.length; i++) {
        var file_data_values = [file_data_values + "\n" + table_rows[i]];
    }
    var file_data = [title.slice(0, -1) + file_data_values];
    // var type = response.headers('Content-type');
    var a = document.createElement('a');
    var URL = window.URL || window.webkitURL;
    var downloadURL = URL.createObjectURL(new Blob([file_data], { type: 'text/csv' }));
    a.href = downloadURL;
    a.download = "operational_details.csv";
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();

}

function show_pan_info(data) {
    let tab =
        `<table border ='1' style='border-collapse:collapse'><tr>
    <th>Merchant ID</th>
    <th>Merchant Name</th>
    <th>Pan ID</th>
    </tr><table>`;

    // Loop to access all rows
    for (let f of data) {
        console.log("r", f.merchant_id)
        tab += `<tr>
<td>${f.merchant_id} </td>
<td>${f.merchant_name}</td>
<td>${f.Pan_id}</td>		
</tr>`;
    }
    // Setting innerHTML as tab variable
    document.getElementById("OperationalData").innerHTML = tab;
}

function show_wire_account_details(data) {                 
    let tab =
        `<table border ='1' style='border-collapse:collapse'>
            <tr>
                <th>Product</th>
                <th>Wire Merchant ID</th>
                <th>UUID</th>
                <th>Unique Transaction Referance</th>
                <th>Remitter Account Number</th>
                <th>Remitter Full Name</th>
                <th>Beneficiary Account Number</th>
                <th>Beneficiary Full Name</th>
            </tr>
    <table>`;

    // Loop to access all rows
    for (let r of data) {
        tab += `<tr>
        <td>${r.product} </td>
        <td>${r.wire_merchant_id}</td>
        <td>${r.uuid || "NA"}</td>		
        <td>${r.unique_transaction_reference || "NA"}</td>		
        <td>${r.remitter_account_number || r.account_number || "NA"}</td>
        <td>${r.remitter_full_name || "NA"}</td>	
        <td>${r.beneficiary_account_number || "NA"}</td>		
        <td>${r.beneficiary_full_name || "NA"}</td>	
    </tr>`;
    }
    // Setting innerHTML as tab variable
    document.getElementById("OperationalData").innerHTML = tab;
}

function show_pg_account_details(data) {
    let tab =
        `<table border ='1' style='border-collapse:collapse'>
            <tr>
                <th>Product</th>
                <th>Merchant ID</th>
                <th>Submerchant ID</th>
                <th>Merchant Name</th>
                <th>Account Number</th>
            </tr>
    <table>`;

    // Loop to access all rows
    for (let r of data) {
        tab += `<tr>
        <td>${r.product} </td>
        <td>${r.merchant_id}</td>
        <td>${r.submerchant_id || "NA"}</td>		
        <td>${r.merchant_name || "NA"}</td>		
        <td>${r.account_number || "NA"}</td>		
    </tr>`;
    }
    // Setting innerHTML as tab variable
    document.getElementById("OperationalData").innerHTML = tab;
}

function show_instacollect_account_details(data) {
    let tab =
        `<table border ='1' style='border-collapse:collapse'>
            <tr>
                <th>Product</th>
                <th>WIRE Merchant ID</th>
                <th>UUID</th>
                <th>Unique Transaction Referance</th>
                <th>Remitter Account Number</th>
                <th>Remitter Full Name</th>
                <th>Beneficiary Account Number</th>
                <th>Beneficiary Full Name</th>
            </tr>
    <table>`;

    // Loop to access all rows
    for (let r of data) {
        tab += `<tr>
        <td>${r.product} </td>
        <td>${r.wire_merchant_id}</td>
        <td>${r.uuid || "NA"}</td>		
        <td>${r.unique_transaction_reference || "NA"}</td>		
        <td>${r.remitter_account_number || "NA"}</td>	
        <td>${r.remitter_full_name || "NA"}</td>		
        <td>${r.beneficiary_account_number || "NA"}</td>		
        <td>${r.beneficiary_full_name || "NA"}</td>			
    </tr>`;
    }
    // Setting innerHTML as tab variable
    document.getElementById("OperationalData").innerHTML = tab;
}

function pagination(count) {
    pagination_value = count / 10
    console.log(pagination_value, "pagination_value")
    console.log("data", response_data)
    let dd = ""
    for (let i = 0; i <= pagination_value; i++) {
            var o = i+1
            dd += '<a href=#'+i+' onclick=call_JsApi('+i+')>page'+o+'</a>';
    }
    
    document.getElementById("pagination_section").innerHTML = dd;
}



function day_func() {
    document.getElementById("operation").innerHTML = '<br><label for="Day">Date:</label>&nbsp;&nbsp;<input type="date" id="date_id" name="day">';

}

function date_range_func() {
    document.getElementById("operation").innerHTML = '<br><label for="Day">Start Date:</label>&nbsp;&nbsp;<input type="date" id="date_id1" name="day"><br><br><label for="Day">End Date:</label>&nbsp;&nbsp;&nbsp;<input type="date" id="date_id2" name="day">';
}

function date_filter_func() {
    if (document.getElementById('day').checked) {
        var x = document.getElementById("date_id")
        var user_date = x.value;
        let bulk = data.data.filter(checkDay);
        show(bulk)

        function checkDay(parm) {
            var date1 = new Date(user_date);
            var date2 = new Date(parm.peb_transaction_date);

            if (date1.getTime() === date2.getTime()) {
                return parm
            }

        }

    }
    else if (document.getElementById('date_range').checked) {
        var x = document.getElementById("date_id1")
        var y = document.getElementById("date_id2")
        var start_date = x.value
        var end_date = y.value
        let bulk = data.data.filter(checkDateRange);
        show(bulk)

        function checkDateRange(parm) {
            var user_start_date = new Date(start_date);
            var user_end_Date = new Date(end_date);
            var txn_date = new Date(parm.peb_transaction_date);
            if (txn_date >= user_start_date && txn_date <= user_end_Date) {
                return parm
            }

        }

    }

    else {
        alert("Please Select the Option.")
    }
}
