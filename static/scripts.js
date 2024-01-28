$(document).on("click", 'a[href^="#"]', function (event) {
  event.preventDefault();
  $("html, body").animate(
    {
      scrollTop: $($.attr(this, "href")).offset().top,
    },
    500
  );
});

$(document).ready(function () {
  $(window)
    .scroll(function () {
      var scrollDistance = $(window).scrollTop();
      $(".card").each(function (i) {
        if ($(this).position().top <= scrollDistance) {
          $(".menu-list a.active").removeClass("active");
          $(".menu-list a").eq(i).addClass("active");
        }
      });
    })
    .scroll();
});

function createContainer(buttonId, divId, placeholders) {
  var counter = 0; // Initialize a counter for unique field names

  $(buttonId).click(function () {
    var div = $("<div></div>").addClass("container");
    var deleteButton = $("<button type='button'>Delete</button>").addClass(
      "deleteButton"
    );
    deleteButton.click(function () {
      div.remove();
    });
    div.append(deleteButton);
    for (var i = 0; i < placeholders.length; i++) {
      var input = $("<input></input>")
        .attr("type", "text")
        .attr("placeholder", placeholders[i])
        .attr(
          "name",
          placeholders[i].toLowerCase().replace(/\s+/g, "_") + "_" + counter
        ) // Unique name
        .addClass("input");
      div.append(input);
    }
    $(divId).append(div);
    counter++; // Increment the counter
  });
}

$(document).ready(function () {
  createContainer("#educationButton", "#educationDiv", [
    "School",
    "Degree",
    "Field of Study",
    "Start Year",
    "End Year",
  ]);
  createContainer("#skillsButton", "#skillsDiv", ["Skill"]);
  createContainer("#certificationsButton", "#certificationsDiv", [
    "Certification",
  ]);
  createContainer("#experienceButton", "#experienceDiv", [
    "Job Title",
    "Company",
    "Start Date",
    "End Date",
    "Job Description",
  ]);
  createContainer("#projectsButton", "#projectsDiv", [
    "Project Title",
    "Tech Used",
    "Project Description",
  ]);
});
