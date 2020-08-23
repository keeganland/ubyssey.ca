import * as mp from './modules/Mixpanel';
import upcomingEvents from './widgets/upcoming-events';

(function() {

  initializeSearchFormActions();
  initializeSocialMediaActions();

  ubysseyHeaderMobilePopUp();
  ubysseyHeaderMagazineDropDown();
  archiveMobileDropDown();
  
  if ($('.js-article').length) {
    mp.pageView('article', $('.js-article'), 1)
  } else {
    mp.pageView();
  }

  //listener for magazine in mobile header pop up
  $('#magazine-mobile').click(function(){
    $('#magazine-more').slideToggle(200);
  });

  let isUpcomingEventsCreated = false;

  $(document).ready(function() {

    embedMargins();

    if($(window).width() <= 500) {
      resizeFullWidthStoryBanner();
    }

    // register widgets
    if(!isUpcomingEventsCreated && $(window).width() >= 1200) {
      isUpcomingEventsCreated = true;
      upcomingEvents();
    }

    //Calls issue parser only in homepage
    if(window.location.pathname === '/'){ issueParser(); }
    
  }); 
  
  $(window).resize(function() {

    //make sure the carousel widget has correct size
    if(!isUpcomingEventsCreated && $(window).width() >= 1200) {
      isUpcomingEventsCreated = true;
      upcomingEvents();
    }

    if($(window).width() <= 500) {
      resizeFullWidthStoryBanner();
    }

  });

})();

function disableScroll() {
  $(document).on('touchmove', function(e) {
    e.preventDefault();
  });
  $('body').addClass('u-no-scroll');
}

function enableScroll() {
  $(document).off('touchmove');
  $('body').removeClass('u-no-scroll');
}

function embedMargins() {
  const marginLeft = $('.article-content > p:first-child').css('marginLeft')
  const marginRight = $('.article-content > p:first-child').css('marginRight')
  $('.image-attachment.left').css('marginLeft', marginLeft)
  $('.image-attachment.right').css('marginRight', marginRight)
}

function resizeFullWidthStoryBanner(){
  if($('.fw-banner banner-image') !== undefined) {
    let bannerHeight = $('.banner-image').height();
    let captionHeight = $('.caption').height();
    let headlineHeight = $('.headline-container').height();
    let minimumHeight = captionHeight+headlineHeight+30;
    if(bannerHeight < minimumHeight) {
      $('.banner-image').height(minimumHeight);
    }
  }
}

//Should be improved (temp)
function issueParser() {
  var req = new XMLHttpRequest();
  req.open('GET', 'https://cors-anywhere.herokuapp.com/https://search.issuu.com/api/2_0/document?q=username%3Aubyssey&responseParams=title&sortBy=epoch&pageSize=4');
  req.setRequestHeader('Ubyssey', 'XMLHttpRequest');
  req.onload = function() {
    var res = req.responseText;
    var jsonQuery = '[' + res.split('[')[1].split(']')[0] + ']';
    var issueArray = JSON.parse(jsonQuery);
    for(var i = 0; i < issueArray.length; i++) {
      var docName = issueArray[i].docname;
      var docId = issueArray[i].documentId;
      var title = issueArray[i].title;
      var issueID = '#issue' + (i+1);
      $(issueID).attr('href', 'https://issuu.com/ubyssey/docs/' + docName).text(title);
      if(i == 0)
        $(issueID).append('<img src="https://image.isu.pub/' + docId +'/jpg/page_1_thumb_large.jpg">');
    }
  };
  req.send();
}

function ubysseyHeaderMagazineDropDown(){
  $('#sections-more-dropdown').hover(function(e) {
    e.stopPropagation();
    $('.sections-more').finish();
    $('.sections-more').slideToggle(300);
    }, (function(e) {
      e.stopPropagation();
      $('.sections-more').finish();
      $('.sections-more').fadeOut(300);
    })
  );
}

function archiveMobileDropDown(){
  let DROPDOWN_FADE_TIME = 100;

  $('.js-dropdown-container').click(function(e) {
    e.preventDefault();
    var dropdown = $(this).parent();
    dropdown.fadeOut(DROPDOWN_FADE_TIME);
    enableScroll();
    return false;
  });

  $('.js-dropdown > a').click(function(e) {
    e.preventDefault();
    var dropdown = $(this).parent().find('.js-dropdown-list');
    if (dropdown.is(':visible')){
      dropdown.fadeOut(DROPDOWN_FADE_TIME);
      enableScroll();
    } else {
      dropdown.fadeIn(DROPDOWN_FADE_TIME);
      if ($(this).hasClass('js-disable-scroll')) {
        disableScroll();
      }
    }
    return false;
  });

  $('.js-dropdown-list a').click(function(e) {
    e.stopPropagation();
  });
}

function ubysseyHeaderMobilePopUp(){
  $('a.menu').click(function(e){
    e.preventDefault();
    if ($('nav.mobile').is(':visible')){
      $('nav.mobile').hide();
      $(this).removeClass('active');
    } else {
      if ($('#search-form').is(':visible')){
        $('#search-form').hide();
        $('a.search').removeClass('active');
      }
      $('nav.mobile').show();
      $(this).addClass('active');
    }
  });
}

//Pending deletion
function initializeSearch(){ 
  $('.dropdown > a').click(function(e){
    e.preventDefault();
    var dropdown = $(this).parent().find('.list');
    if (dropdown.is(':visible')){
      dropdown.hide();
    } else {
      dropdown.show();
    }
    return false;
  });



}

function initializeSearchFormActions(){
    $(document).on('click', 'a.search', function(e){
      e.preventDefault();
      if ($('#search-form').is(':visible')){
        $('#search-form').hide();
        $(this).removeClass('active');
      } else {
        if ($('nav.mobile').is(':visible')){
          $('nav.mobile').hide();
          $('a.menu').removeClass('active');
        }
        $('#search-form').show();
        $('#search-bar').focus();
        $(this).addClass('active');
      }
      e.stopPropagation();
    });

    //listeners for hiding search form
    $(document).on('keyup', function(e) {
      var ESCAPE = 27;
      if (e.keyCode == ESCAPE) {
        $('#search-form').is(':visible') && $('#search-form').hide();
      }
    });
  
    $(document).click(function() {
      $('#search-form').hide();
    });

    $(document).on('click', '#search-form > .u-container', function(e){
      e.stopPropagation();
    });
}

function initializeSocialMediaActions(){
  $(document).on('click', 'a.facebook', function(e){
    e.preventDefault();
    FB.ui({
      method: 'share_open_graph',
      action_type: 'og.likes',
      action_properties: JSON.stringify({
        object: $(this).data('url'),
      })
    }, function(response){});
  });

  $(document).on('click', 'a.twitter', function(e){
    e.preventDefault();
    window.open('http://twitter.com/share?url=' + $(this).data('url') + '&text=' + $(this).data('title') + '&', 'twitterwindow', 
    'height=450, width=550, top='+($(window).height()/2 - 225) +', left='+($(window).width()/2 - 225) +', toolbar=0, location=0, menubar=0, directories=0, scrollbars=0');
  });

  $(document).on('click', 'a.reddit', function(e){
    e.preventDefault();
    window.open('http://www.reddit.com/submit?url=' + $(this).data('url') + '&title=' + $(this).data('title') + '&', 'redditwindow', 
    'height=450, width=550, top='+($(window).height()/2 - 225) +', left='+($(window).width()/2 - 225) +', toolbar=0, location=0, menubar=0, directories=0, scrollbars=0');
  });
}
