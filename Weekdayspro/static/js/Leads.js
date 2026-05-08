function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = cookie.substring(name.length + 1);
        break;
      }
    }
  }
  return cookieValue;
}

function projectLead(event, leadToId, proId, phoneNumber) {
  if (event) event.preventDefault();
  fetch("/projectlead/" + leadToId + "/" + proId + "/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then(function(response) { return response.json(); })
    .then(function(data) {
      console.log(data.msg);
      window.location.href = "tel:" + phoneNumber;
    })
    .catch(function(error) { console.error("Error:", error); });
}

function propertyLead(event, leadToId, propId, phoneNumber) {
  if (event) event.preventDefault();
  fetch("/propertyllead/" + leadToId + "/" + propId + "/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then(function(response) { return response.json(); })
    .then(function(data) {
      console.log(data.msg);
      window.location.href = "tel:" + phoneNumber;
    })
    .catch(function(error) { console.error("Error:", error); });
}

function profileLead(event, leadToId) {
  if (event) event.preventDefault();
  var phoneLink = event.currentTarget ? event.currentTarget.href : (event.target ? event.target.href : "");

  fetch("/profilellead/" + leadToId + "/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then(function(response) { return response.json(); })
    .then(function(data) {
      console.log(data.message);
      if (phoneLink) {
        window.location.href = phoneLink;
      }
    })
    .catch(function(error) { console.error("Error:", error); });
}
