/*
	Be by TEMPLATE STOCK
	templatestock.co @templatestock
	Released for free under the Creative Commons Attribution 3.0 license (templated.co/license)
*/

(function($) {
/* ---------------------------------------------- /*
	 * owl header
	/* ---------------------------------------------- */
$(document).ready(function() {
      function loadFeaturedMedia($scope) {
        $scope.find("source[data-srcset]").each(function() {
          var $source = $(this);
          $source.attr("srcset", $source.attr("data-srcset"));
          $source.removeAttr("data-srcset");
        });
        $scope.find("img[data-src]").each(function() {
          var $img = $(this);
          $img.attr("src", $img.attr("data-src"));
          $img.removeAttr("data-src");
          $img.removeClass("featured-lazy-media");
        });
      }

      function loadFeaturedMediaAt($elem, index) {
        var $items = $elem.find(".owl-item");
        var itemCount = $items.length;
        if (!itemCount) return;
        var safeIndex = ((index % itemCount) + itemCount) % itemCount;
        loadFeaturedMedia($items.eq(safeIndex));
      }

      function loadCurrentFeaturedMedia($elem, includeNext) {
        var carousel = $elem.data("owlCarousel");
        var current = carousel && typeof carousel.currentItem === "number" ? carousel.currentItem : 0;
        loadFeaturedMediaAt($elem, current);
        if (includeNext) {
          loadFeaturedMediaAt($elem, current + 1);
        }
      }

      $(".header1").owlCarousel({
        autoPlay : 3000,
        stopOnHover : true,
        navigation:true,
        paginationSpeed : 1000,
        goToFirstSpeed : 2000,
        singleItem : true,
        autoHeight : true,
        navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
        afterInit : function($elem) {
          loadCurrentFeaturedMedia($elem, false);
          window.setTimeout(function() {
            loadCurrentFeaturedMedia($elem, true);
          }, 1200);
        },
        afterAction : function($elem) {
          loadCurrentFeaturedMedia($elem, true);
        },
		itemsDesktop : [1199,2],
	  itemsDesktopSmall : [980,2],
	  itemsTablet: [768,1],
	  itemsMobile : [479,1],
      });
    });
/* ---------------------------------------------- /*
	 * Preloader
	/* ---------------------------------------------- */

	var preloaderHidden = false;
	var preloaderHideScheduled = false;

	function hidePreloader() {
		if (preloaderHidden) return;
		preloaderHidden = true;

		var $preloader = $('#preloader');
		if (!$preloader.length) return;

		$('#loading').addClass('is-hidden');
		$preloader.addClass('is-hidden');

		window.setTimeout(function() {
			$preloader.addClass('is-gone').hide();
		}, 760);
	}

	function schedulePreloaderHide() {
		if (preloaderHidden || preloaderHideScheduled) return;
		preloaderHideScheduled = true;

		window.setTimeout(function() {
			if (window.requestAnimationFrame) {
				window.requestAnimationFrame(function() {
					window.requestAnimationFrame(hidePreloader);
				});
			} else {
				hidePreloader();
			}
		}, 640);
	}

	$(schedulePreloaderHide);
	$(window).on('load', schedulePreloaderHide);
	window.setTimeout(hidePreloader, 2400);

    "use strict"; // Start of use strict

    // jQuery for page scrolling feature - requires jQuery Easing plugin
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top - 50)
        }, 1250, 'easeInOutExpo');
        event.preventDefault();
    });

    // Highlight the top nav as scrolling occurs
    $('body').scrollspy({
        target: '.navbar-fixed-top',
        offset: 51
    })

    // Closes the Responsive Menu on Menu Item Click
    $('.navbar-collapse ul li a').click(function() {
        $('.navbar-toggle:visible').click();
    });

    // Fit Text Plugin for Main Header
    $("h1").fitText(
        1.2, {
            minFontSize: '35px',
            maxFontSize: '65px'
        }
    );

    // Offset for Main Navigation
    $('#mainNav').affix({
        offset: {
            top: 100
        }
    })
	

    // Initialize WOW.js Scrolling Animations
    new WOW().init();

})(jQuery); // End of use strict
/* Parallax
 =============================================*/
;
(function ($) {
    if (typeof include === "function") {
        include('../../js/jquery.rd-parallax.js');
    }
})(jQuery);

/* filter
 =============================================*/
/*--------------------------
	scrollUp
---------------------------- */
	if ($.scrollUp) {
		$.scrollUp({
	        scrollText: '<i class="fa fa-angle-up"></i>',
	        easingType: 'linear',
	        scrollSpeed: 900,
	        animation: 'fade'
	    });
	}
