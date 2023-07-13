$(document).ready(function (){
	var evaBoxReg = $('.eve-container.bg-register #eve-box'),
		evaBoxLogin = $('.eve-container.bg-login #eve-box'),
		evaBoxHome = $('.eve-container.bg-home-page #eve-box'),
		headEve1 = evaBoxReg.find('.head'),
		handEve1 = evaBoxReg.find('.hand'),
		leftHandEve2 = evaBoxLogin.find('.left-hand'),
		rightHandEve2 = evaBoxLogin.find('.right-hand'),
		headEve3 = evaBoxHome.find('.head'),
		bodyEve3 = evaBoxHome.find('.body'),
		rightHandEve3 = evaBoxHome.find('.right-hand'),
		bulbEve3 = evaBoxHome.find('.bulb'),
		bulbOnEve3 = bulbEve3.find('.bulb_on'),
		eyes = $('.eyes'),
		progressBar = $('.progress');

	// Eve blinking
	setInterval(function () {
		eyes.hide();
		setTimeout(function (){
			eyes.show();
		},200);
		setTimeout(function (){
			eyes.hide();
		},1200);
		setTimeout(function (){
			eyes.show();
		},1400);
	}, 5000);

	if (evaBoxReg.length) {
		$(window).resize(function (){
			onResize(evaBoxReg, true, 1.39, 0);
		});
		onResize(evaBoxReg, true, 1.39, 0);

		// Eve laughs
		setInterval(function () {
			eveMoving(headEve1, {'margin-top':'2%'}, 150, function () {
				eveMoving(headEve1, {'margin-top':0}, 100, function () {
					eveMoving(headEve1, {'margin-top':'3%'}, 150, function () {
						eveMoving(headEve1, {'margin-top':0}, 100);
					});
				});
			});
		}, 7000);

		// Hand moving
		setInterval(function () {
			eveMoving(handEve1,{'margin-top':'-2%'}, 150, function () {
				eveMoving(handEve1, {'margin-top':0}, 100, function () {
					eveMoving(handEve1, {'margin-top':'-3%'}, 150, function () {
						eveMoving(handEve1, {'margin-top':0}, 100);
					});
				});
			});
		}, 7000);
	} else if (evaBoxLogin.length) {
		$(window).resize(function (){
			onResize(evaBoxLogin, false, 1.046, 0);
		});
		onResize(evaBoxLogin, false, 1.046, 0);

		// Hands moving
		setInterval(function () {
			eveMoving(rightHandEve2,{'rotate':'10deg'}, 500, function () {
				eveMoving(rightHandEve2,{'rotate':'0deg'}, 500, function () {
					eveMoving(rightHandEve2,{'rotate':'8deg'}, 500, function () {
						eveMoving(rightHandEve2,{'rotate':'0deg'}, 500);
					});
				});
			});

			eveMoving(leftHandEve2,{'rotate':'-10deg'}, 500, function () {
				eveMoving(leftHandEve2,{'rotate':'0deg'}, 500, function () {
					eveMoving(leftHandEve2,{'rotate':'-8deg'}, 500, function () {
						eveMoving(leftHandEve2,{'rotate':'0deg'}, 500);
					});
				});
			});
		}, 7000);
	} else if (evaBoxHome.length) {
		$(window).resize(function (){
			onResize(evaBoxHome, true, 1.16, 30);
		});
		onResize(evaBoxHome, true, 1.16, 30);

		progressBar.each(function () {
			var text = $(this).find('.text'),
				barVal = parseInt($(this).attr('data1')),
				intVal = parseInt($(this).attr('data2')) / 10,
				coinImg = $('<img />').addClass('coin').attr('src','/static/images/coin.png'),
				coinsCounter = 0,
				progressWidth = $(this).width() / 100 * barVal,
				bar = $(this).find('.bar');

			text.find('span').html(coinsCounter);
			bar.animate({
				'width': progressWidth
			},1000);

			var coinsClones = setInterval(function (){
				coinImg.clone().css('margin-left',(!coinsCounter ? 0 : -10)).appendTo(text);
				coinsCounter++;
				if (coinsCounter == intVal) clearInterval(coinsCounter);
				text.find('span').html(coinsCounter);
			}, 50);
		});

		setInterval(function () {
			eveMoving(headEve3, {'margin-top': '-1%'}, 1000, function () {
				eveMoving(headEve3, {'margin-top': 0}, 1000);
			});

			eveMoving(bodyEve3, {'top': '1%'}, 1000, function () {
				eveMoving(bodyEve3, {'top': 0}, 1000);
			});

			eveMoving(rightHandEve3, {'rotate': '-5deg'}, 1000, function () {
				eveMoving(rightHandEve3, {'rotate': '0deg'}, 1000);
			});
		}, 2000);

		setInterval(function () {
			eveMoving(rightHandEve3, {'rotate': '-7deg'}, 1500, function () {
				eveMoving(rightHandEve3, {'rotate': '0deg'}, 1500);
			});
		}, 3000);

		setInterval(function () {
			eveMoving(bulbOnEve3, {'opacity': 0}, 2500, function () {
				eveMoving(bulbOnEve3, {'opacity': 1}, 2500);
			});

			eveMoving(progressBar, {'opacity': 0.5}, 2500, function () {
				eveMoving(progressBar, {'opacity': 1}, 2500);
			});

		}, 5000);
	}
});

function onResize(evaBox, multiplication, coof, marginBottom)
{
	if (multiplication) evaBox.css('height',evaBox.width() * coof);
	else evaBox.css('height',evaBox.width() / coof);
	var eveContainer = $('.eve-container');
	eveContainer.css('height',1);
	eveContainer.css({
		'height':$(document).height() + marginBottom,
		'background-size': 'cover'
	});
}

function eveMoving(obj, props, spped, callback)
{
	obj.animate(props, spped, function () {
		if (callback) callback();
	});
}