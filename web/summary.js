var CarSummary = function() {
	this.car = 'Tesla';
	this.vin = '123';
	this.count = 5;
	this.width = 123;
	this.height = 148;
	this.offset = 6;
	this.data = '';
	this.showFadeIcon = true;
	this.html = [];
}
CarSummary.prototype.refresh = function() {
	var self = this;
	dateFromFilename = function(file) {
		return new Date(file.substring(0, 4) + '-' + file.substring(4, 6) + '-' + file.substring(6, 8));
	}
	dateTimeFromFilename = function(file) {
		return new Date(file.substring(0, 4) + '-' + file.substring(4, 6) + '-' + file.substring(6, 8) + 'T' + file.substring(9, 11) + ':' + file.substring(11, 13));
	};
	$.ajax({
		type: 'GET',
		url: 'summary.php',
		async: true,
		cache: false,
		timeout: 5000,
		success: function(data) {
			self.data = JSON.parse(data);
			//console.log(self.data);
			var i;
			var html = [];
			// Use the latest day to set the current month
			var last = self.data[self.data.length - 1];
			var file = last[last.length - 1][0];
			var dayStart = dateFromFilename(file);
			var targetMonth = dayStart.getUTCMonth();
			var m = dayStart.toLocaleString('default', { timeZone: 'UTC' , month: 'long' });
			var y = dayStart.toLocaleString('default', { timeZone: 'UTC' , year: 'numeric' });
			var frame = JSON.parse(last[last.length - 1][1]);
			self.vin = frame['vin'] + ' - ' + frame['vehicle_state']['car_version'];
			html.push('<div class="boxContainer">');
			html.push('  <div class="title">');
			html.push('  <div class="titleMonth">' + m + '</div><div class="titleYear">' + y + '</div>');
			html.push('</div>');
			html.push('<div class="vin medium"><b>' + frame['vehicle_state']['vehicle_name'] + '</b> - ' + self.vin + '</div>');

			for (i = 0; i < 7; i++) {
				if (dayStart.getUTCDay() == 0) {
					break;
				}
				dayStart.setTime(dayStart.getTime() - 86400000);
			}
			console.log(dayStart.toUTCString());
			// Roll back another (count) weeks as the first Sunday
			dayStart.setTime(dayStart.getTime() - (self.count - 1) * 7 * 86400000);
			console.log(dayStart.toUTCString());

			// Make a top row showing days
			var t0 = dayStart.getTime();
			for (var n = 0; n < 7; n++) {
				var y = 60;
				var x = n * (self.width + self.offset);
				var d = t0.toLocaleString('default', { timeZone: 'UTC' , weekday: 'short' });
				t0.setTime(t0.getTime() + 86400000);
				html.push('  <div class="dayOfWeek" style="left:' + x + 'px; top:' + y + 'px">');
				html.push('    <div class="titleDayLabel">' + d + '</div>');
				html.push('  </div>');
			}
			// Look for the first Sunday to start showing
			t0 = dayStart.getTime();
			console.log(t0);
			for (i = 0; i < self.data.length; i++) {
				file = self.data[i][0][0];
				var fileDate = dateTimeFromFilename(file);
				if (fileDate.getTime() >= t0) {
					break;
				}
			}
			console.log('i = ' + i + ' --> ' + fileDate.toUTCString() + ' / ' + dayStart.toUTCString());
			
			var todayString = new Date().toLocaleString('default', {day: 'numeric'});

			file = self.data[i][0][0];
			var dayStart = dateFromFilename(file);

			// Loop through data (i) but up to (count) weeks. The variable i increases on Saturday
			var j = 0;
			var d = 0;
			var o1 = 0;
			var o0 = 0;
			var s1 = 0;
			for (var c = 0; c < self.count * 7; c++) {
				var x = d * (self.width + self.offset);
				var y = j * (self.height + self.offset) + 90;
				var elemClass = '';
				if (targetMonth != dayStart.getUTCMonth()) {
					elemClass += ' otherMonth';
				} 
				if (dayStart.getUTCMonth() == new Date().getUTCMonth() && 
					todayString == dayStart.toLocaleString('default', {timeZone: 'UTC' , day: 'numeric'})) {
					elemClass += ' today';
				}
				if (m != dayStart.getUTCMonth()) {
					m = dayStart.getUTCMonth();
					dayString = dayStart.toLocaleString('default', { timeZone: 'UTC' , month: 'short', day: 'numeric' });
				} else {
					dayString = dayStart.toLocaleString('default', { timeZone: 'UTC' , day: 'numeric' })
				}
				html.push('  <div class="box" style="left:' + x + 'px; top:' + y + 'px">');
				html.push('    <div class="dayLabel' + elemClass + '">' + dayString + '</div>');

				insertOrFadeIcon = function(cond, image) {
					appendix = '';
					if (cond || self.showFadeIcon) {
						if (!cond && self.showFadeIcon) {
							appendix += ' fade';
						}
						return '<img class="icon' + appendix + '" src="' + image + '"/>\n';
					}
					return '';
				};

				if (i < self.data.length) {
					day = self.data[i];
					file = day[day.length - 1][0];
					fileDate = dateTimeFromFilename(file);
					if (fileDate.getUTCDate() == dayStart.getUTCDate()) {
						var frameAlpha = JSON.parse(day[0][1]);
						var frameOmega = JSON.parse(day[day.length - 1][1]);
						// Battery level
						chargeLevel = frameOmega['charge_state']['battery_level'];
						elementClass = '';
						r = Math.floor(chargeLevel / 10)
						if (r <= 5) {
						   elementClass += ' charge' + r;
						}
						html.push('    <div class="chargeLevel' + elementClass + '" style="height:' + chargeLevel + '%"></div>\n');

						// Calculate total miles driven
						if (o1 == 0 && day.count > 1) {
							o1 = frameAlpha['vehicle_state']['odometer'];
						}
						o0 = frameOmega['vehicle_state']['odometer'];
						var delta_o = o0 - o1;
						var carDriven = delta_o > 1.0;
						o1 = o0;

						// If there was a charging event
						var carCharged = false;
						for (var k = 0; k < day.length && carCharged == false; k++) {
							if (day[k][1].includes('Charging')) {
								carCharged = true;
							}
						}

						// Software version
						var carUpdated = false;
						if (s1 == 0) {
							s1 = frameAlpha['vehicle_state']['car_version'];
						}
						s0 = frameOmega['vehicle_state']['car_version'];
						if (s0 != s1) {
							carUpdated = true;
						}
						s1 = s0;

						// Icon bar using the information derived earlier
						html.push('    <div class="iconBar">\n');
						html.push('      ' + insertOrFadeIcon(carDriven, 'blob/wheel.png'));
						html.push('      ' + insertOrFadeIcon(carCharged, 'blob/charge.png'));
						html.push('      ' + insertOrFadeIcon(carUpdated, 'blob/up.png'));
						html.push('    </div>\n');

						// Lines of information
						timeString = fileDate.toLocaleString('en-US', { timeZone: 'UTC', hour12: true, hour: 'numeric', minute: '2-digit'});
						html.push('    <div class="info">\n');
						html.push('      <span class="textInfo large">' + chargeLevel + '%</span>\n');
						html.push('      <span class="textInfo medium">' + timeString + '</span>\n');
						html.push('      <span class="textInfo medium">+' + delta_o.toFixed(1) + ' mi (' + day.length + ')</span>\n');
						html.push('      <span class="textInfo medium">' + o0.toFixed(1) + ' mi</span>\n');
						html.push('    </div>\n');

						i++;
					}
				}
				html.push('  </div>');
				dayStart.setDate(dayStart.getDate() + 1);
				if (d++ == 6) {
					d = 0;
					j++;
				}
			}

			document.getElementById('CarSummary').innerHTML = html.join('\n');
		},
		error: function(error) {
			console.log('AJAX Error');
			console.log(error);
		}
	});
}
CarSummary.prototype.start = function() {
	this.refresh();
}
// ----------------------------------- Script -----------------------------------

var mars = new CarSummary();

$(document).ready(function() {mars.start()});
