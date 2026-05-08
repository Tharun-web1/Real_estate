function projectLead(event, leadToId, proId, phoneNumber) {
  event.preventDefault();
  fetch(`/projectlead/${leadToId}/${proId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.msg);
      window.location.href = `tel:${phoneNumber}`;
    })
    .catch((error) => console.error("Error:", error));
}

function propertyLead(event, leadToId, propId, phoneNumber) {
  event.preventDefault();

  fetch(`/propertyllead/${leadToId}/${propId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.msg);
      window.location.href = `tel:${phoneNumber}`;
    })
    .catch((error) => console.error("Error:", error));
}

function profileLead(event, leadToId) {
  event.preventDefault();

  const phoneLink = event.target.href;

  fetch(`/profilellead/${leadToId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.message);

      // continue to call AFTER saving the lead
      window.location.href = phoneLink;
    })
    .catch((error) => console.error("Error:", error));
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = cookie.substring(name.length + 1);
        break;
      }
    }
  }
  return cookieValue;
}
