

$(() => {

    
    //extract faceID from URL parameter
    var imgPathPrefix = "https://hw2-faces.s3.amazonaws.com/"
    var urlParam = new URLSearchParams(window.location.search);
    var faceID = urlParam.get("faceID");
    if (faceID === null) {
        faceID = "blackcat";
    }
    var objKey = urlParam.get("objectKey");
    var imgPath = imgPathPrefix + objKey;
    //console.log(imgPath);
    $("#visitor-img").attr("src", imgPath);

    var nameReady = false;
    var numberReady = false;
    var passcodeReady = false;
    var phoneno = /^\+1([0-9]{10})$/;
    $("#visitor-name").blur(() => {
        if ($("#visitor-name").val() === "") {
            nameReady = false;
            $("#visitor-name").next().css("display", "inline");
        } else {
            $("#visitor-name").next().css("display", "none");
            nameReady = true;
        }
    });
    $("#visitor-number").blur(() => {
        phoneNumber = $("#visitor-number").val();
        if (!phoneNumber.match(phoneno)) {
            numberReady = false;
            $("#visitor-number").next().css("display", "inline");
        } else {
            numberReady = true;
            $("#visitor-number").next().css("display", "none");
        }
    });
    // $("#visitor-passcode").blur(() => {
    //     var passcode = $("#visitor-passcode").val();
    //     if ($("#visitor-passcode").val() === "") {
    //         passcodeReady = false;
    //         $("#visitor-passcode").next().css("display", "inline");
    //     } else {
            
    //         var re = $.post("https://7463my73x5.execute-api.us-east-1.amazonaws.com/deve/visitor-interface", 
    //         JSON.stringify(
    //             {
    //                 passcode: passcode
    //             }
    //         ),
    //         function(response) {
    //             console.log(response);
    //             response = JSON.parse(response);
    //             if (response["exisitence"] === "1") {
    //                 console.log(1);
    //                 //$("#visitor-passcode").next().css("display", "inline");
    //                 $("#visitor-passcode").next().html("this passcode already exists.");
    //                 $("#visitor-passcode").next().css("display", "inline");
    //                 passcodeReady = false;
    //             } else {
    //                 console.log(0);
    //                 $("#visitor-passcode").next().html("please enter a passcpde");
    //                 $("#visitor-passcode").next().css("display", "none");
    //                 passcodeReady = true;
    //             }
    //         },
    //         "json");

    //         //console.log(re)
    //     }
    // });
    $("#accept-button").click(() => {
        name = $("#visitor-name").val();
        phoneNumber = $("#visitor-number").val();
        passCode = $("#visitor-passcode").val();
        if (name === "") {
            $("#visitor-name").next().css("display", "inline");
        } 
        else {
            // $("#visitor-name").next().css("display", "none");
            if (!phoneNumber.match(phoneno)) {
                $("#visitor-number").next().css("display", "inline");
            }
            // if (phoneNumber === "") {
            //     $("#visitor-number").next().html("Please enter a phone number.");
            // }
            else {
                // if (passCode === "") {
                //     $("#visitor-passcode").next().css("display", "inline");
                // }
                // else {
                    // // check if everything is ready
                    // var exisitence;
                    // var re = $.post("https://7463my73x5.execute-api.us-east-1.amazonaws.com/deve/visitor-interface", 
                    // JSON.stringify(
                    //     {
                    //         passcode: passCode
                    //     }
                    // ),
                    // function(response) {
                    //     //console.log(response);
                    //     response = JSON.parse(response);
                    //     if (response["exisitence"] === "1") {
                    //         //console.log(1);
                    //         //$("#visitor-passcode").next().css("display", "inline");
                    //         $("#visitor-passcode").next().html("this passcode already exists.");
                    //         $("#visitor-passcode").next().css("display", "inline");
                    //         exisitence = true
                        
                    //     } else {
                    //         //console.log(0);
                    //         $("#visitor-passcode").next().html("please enter a passcpde");
                    //         $("#visitor-passcode").next().css("display", "none");
                            

                    //         var xhr = new XMLHttpRequest();
                    //         xhr.responseType = "json"
                    //         xhr.open("POST", "https://7463my73x5.execute-api.us-east-1.amazonaws.com/deve/owner-interface");
                    //         xhr.onreadystatechange = (event) => {
                    //             response = event.target.response;
                    //             //console.log(response);
                    //         };
                    //         xhr.setRequestHeader('Content-Type', 'application/json');
                    //         xhr.send(JSON.stringify(
                    //             {
                    //                 faceID: faceID,
                    //                 objectKey: objKey,
                    //                 name: name,
                    //                 phoneNumber: phoneNumber,
                    //                 passcode: passCode
                    //             }
                    //         ));

                    //         $("#visitor-name").val("");
                    //         $("#visitor-number").val("");
                    //         $("#visitor-passcode").val("");
                    //         alert("Successfully added a new visitor!");
                    //     }
                    // },
                    // "json");
                    

                    // $("#visitor-passcode").next().html("please enter a passcpde");
                            // $("#visitor-passcode").next().css("display", "none");
                            

                    var xhr = new XMLHttpRequest();
                    xhr.responseType = "json"
                    xhr.open("POST", "https://7463my73x5.execute-api.us-east-1.amazonaws.com/deve/owner-interface");
                    xhr.onreadystatechange = (event) => {
                        response = event.target.response;
                        //console.log(response);
                    };
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify(
                        {
                            faceID: faceID,
                            objectKey: objKey,
                            name: name,
                            phoneNumber: phoneNumber
                            // passcode: passCode
                        }
                    ));

                    $("#visitor-name").val("");
                    $("#visitor-number").val("");
                    // $("#visitor-passcode").val("");
                    alert("Successfully added a new visitor!");
                }
            }
            
        });
    $("#decline-button").click(() => {
        alert("You decilined this visit!");
        window.top.close();
    });
})