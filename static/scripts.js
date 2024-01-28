  $(document).on("click", 'a[href^="#"]', function(event) {
    event.preventDefault();
    $("html, body").animate(
      {
        scrollTop: $($.attr(this, "href")).offset().top
      },
      500
    );
  });


  $(document).ready(function() {
    $(window).scroll(function() {
      var scrollDistance = $(window).scrollTop();
      $('.card').each(function(i) {
        if ($(this).position().top <= scrollDistance) {
          $('.menu-list a.active').removeClass('active');
          $('.menu-list a').eq(i).addClass('active');
        }
      });
    }).scroll();
  });
  
  
  $(document).ready(function(){
    $(".collapsible").click(function(){
        $(this).next(".content").slideToggle("slow");
        $(this).toggleClass("active");
    });
});

  


function createContainer(buttonId, divId, placeholders, inputTypes) {
  var counter = 0;

  $(buttonId).click(function() {
      counter++;
      var div = $("<div></div>").addClass("container");

      // Generate a title for each new container
      if (placeholders.length > 1) {
          var titleText = divId.charAt(1).toUpperCase() + divId.slice(2).replace("Div", "") + " #" + counter;
          if (divId === "#projectsDiv") {
              titleText = "Project #" + counter;
          }
          // Add spaces between words in the title
          if (divId === "#researchExperienceDiv" || divId === "#industryExperienceDiv") {
              titleText = titleText.replace(/([a-z])([A-Z])/g, '$1 $2');
          }
          var title = $("<h4></h4>").text(titleText).css("text-align", "center").css("margin-top", "15px");
          div.append(title);
      }

      // Create input fields with unique names
      for (var i = 0; i < placeholders.length; i++) {
          var baseName = divId.slice(1, -3).toLowerCase().replace(/([A-Z])/g, '_$1');
          var inputName = baseName + "_" + counter + "_" + placeholders[i].toLowerCase().replace(/\s+/g, '_');
          var input = $("<input></input>")
              .attr("type", inputTypes[i])
              .attr("placeholder", placeholders[i])
              .attr("name", inputName)
              .addClass("input");
          div.append(input);
      }

      // Create and append the delete button
      var deleteButton = $("<button type='button'>Delete</button>")
          .addClass("deleteButton, button, is-danger, is-light")
          .css({
              "display": "block",
              "margin-left": "auto",
              "margin-right": "auto",
              "margin-top": "15px"
          });
      deleteButton.click(function() {
          div.remove();
      });
      div.append(deleteButton);

      $(divId).append(div);
  });
}

$(document).ready(function(){
    createContainer("#educationButton", "#educationDiv", ["Name", "Location", "Level", "Major", "Start Date", "End Date"], ["text", "text", "text", "text", "date", "date"]);
    createContainer("#researchExperienceButton", "#researchExperienceDiv", ["Project Title", "University", "Location", "Start Date", "End Date", "Job Description"], ["text", "text", "text", "date", "date", "text"]);
    createContainer("#industryExperienceButton", "#industryExperienceDiv", ["Position Title", "Company", "Location", "Start Date", "End Date", "Job Description"], ["text", "text", "text", "date", "date", "text"]);
    createContainer("#projectsButton", "#projectsDiv", ["Project Title", "Tech Used", "Description"], ["text", "text", "text"]);

    function addSkill(inputId, divId, parameter) {
      $(inputId).keypress(function(e) {
          if (e.which == 13) { // Enter key
              e.preventDefault();
              var inputVal = $(this).val();

              // Create the visual bubble
              var bubble = $("<span></span>").text(inputVal).addClass("bubble");
              var deleteBubbleButton = $("<button></button>").addClass("deleteBubbleButton").click(function(){
                  bubble.remove();
                  hiddenInput.remove(); // Remove corresponding hidden input
              });
              bubble.append(deleteBubbleButton);

              // Create a hidden input field with the correct name attribute
              var hiddenInput = $("<input>")
                  .attr("type", "hidden")
                  .attr("name", parameter) // Ensure this matches with your Flask backend expectations
                  .val(inputVal);

              $(this).val(""); // Clear the visible input field
              $(divId).append(bubble);
              $(divId).append(hiddenInput); // Append the hidden input to the form
          }
      });
  }
  addSkill("#languagesSkillsInput", "#languagesSkillsDiv", "languages");
    addSkill("#frameSkillsInput", "#frameSkillsDiv", "frameworks");
    addSkill("#developerSkillsInput", "#developerSkillsDiv", "dev_tools");
    addSkill("#librarySkillsInput", "#librarySkillsDiv", "libraries");
});