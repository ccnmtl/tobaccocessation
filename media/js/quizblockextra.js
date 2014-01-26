function showAnswer(radioElt) {
    jQuery(radioElt).parents("div.casequestion").next().find("div.toggleable").show()
}

function maybeUnlockNextSection() {
   // is our next section unlocked now?
   var next_section_slug = jQuery("#next_section_slug").val();
   if (next_section_slug !== undefined) {
       var loadUrl = 'http://' + location.hostname + ':' + location.port + "/main/accessible/" + next_section_slug + "/";
       jQuery.getJSON(loadUrl, { "noCache":  new Date().getTime() }, function(data) {
          for (var section_slug in data) {
             jQuery("#span_" + section_slug).css("display", "none");
             jQuery("#next_disabled").css("display", "none");
             jQuery("#" + section_slug).css("display", "inline");
             jQuery("#next").css("display", "inline");
          }
       });
   }
}

function hasVideo() {
    // Video associated with each answer
    return jQuery("#multivideo").length > 0 || jQuery("#singlevideo").length > 0; 
}

function loadState(blockId, pageblockId) {
    maybeUnlockNextSection();
}

function storeState(element) {
    if (element.is(':checkbox') || element.is(':radio')) {
        if (jQuery(element).is(":checked")) {
            var pattern = /\d*$/g
            var questionId = element.attr("name").match(pattern)[0];
            var serializedData = jQuery("#form-" + questionId).serialize();
            
            jQuery.ajax({
                type: "POST",
                url: jQuery("#form-" + questionId).attr("action"),
                data: serializedData, 
                success: function() {
                    maybeUnlockNextSection();
                },
                error: function() {}
            });

            // show the "correct" answer block
            jQuery("#q" + questionId).css("display", "block");
        }
    }
}

function showVideo(radioElt) {
    // hide any videos that are currently playing
    // stop the video?
    jQuery("div.quiz-video").addClass("answer-video").removeClass("quiz-video");
    var video = jQuery(radioElt).siblings("div.answer-video")[0];
    
    jQuery(video).addClass("quiz-video");
    
    // center the video vertically 
    var top = jQuery("div.multiple-video-quiz").offset().top;
    var height = jQuery("div.multiple-video-quiz").outerHeight();
    
    var center = (top + height) / 2 - jQuery(video).height() / 2 ; 
    
    jQuery(video).css({"top": center + "px"});
    
    jQuery(video).removeClass("answer-video");
}


jQuery(document).ready(function() {
    var a = jQuery("div.multiple-video-quiz").find("input[type='radio']:checked");
    if (a.length > 0) {
        showVideo(a[0]);
    }
});
