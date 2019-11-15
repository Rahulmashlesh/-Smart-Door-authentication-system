$(() => {
    $("#startButton").click(() => {
        var inputBox = $("#opt-input");
        var passcode = inputBox.val();

        //TODO:Send passcode to API to check if it exists in the DynamoDB
        //

        var xhr = new XMLHttpRequest();
        xhr.responseType = "json"
        xhr.open("POST", "https://7463my73x5.execute-api.us-east-1.amazonaws.com/deve/visitor-interface");
        xhr.onreadystatechange = (event) => {
            response = JSON.parse(event.target.response);
            console.log(response);
            if (response["exisitence"] === '1') {
                // console.log(response["name"]);
                name = response["name"];
                alert("Welcome, " + name);
                
            } else {
                alert("Access denied");
            }
        };
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(
            {
                passcode: passcode
            }
        ));

        inputBox.val("");
    });
});