<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="stylesheet" type="text/css" href="common.css?v=4"/>
	<style type="text/css">
		.hidden {visibility:hidden;}
		.boxContainer {width:898px; height:935px;}
		.dayOfWeek {width:123px; height:50px;}
		.box {width:123px; height:148px;}
	</style>
	<title>Car Summary</title>
</head>

<body>

<div class="boxContainer">

<?php
date_default_timezone_set('UTC');

$store = '/home/boonleng/Documents/Tesla';
$folders = scandir($store, 0);
$folders = array_slice($folders, count($folders) - 35);
$count = 5;
$width = 123;
$height = 148;
$offset = 6;
$showFadeIcon = True;

// print_r($folders);

// Read in the data
$data = array();
foreach ($folders as $folder) {
	$files = array_diff(scandir($store . '/' . $folder), array('..', '.'));
	// print_r($files);
	$frames = array();
	foreach ($files as $file) {
		$fullpath = $store . '/' . $folder . '/' . $file;
		$object = json_decode(file_get_contents($fullpath), True);
		array_push($frames, array($file, $object));
	}
	array_push($data, $frames);
}

function date_from_filename($file) {
	return date_create_from_format('YmjHi', substr($file, 0, 8) . '0000');
}

function datetime_from_filename($file) {
	return date_create_from_format('Ymj-Hi', substr($file, 0, 13));
}

$i = 0;
$last = $data[count($data) - 1];
$file = $last[count($last) - 1][0];
$frame = $last[count($last) - 1][1];
$fileDate = date_from_filename($file);
$targetMonth = date_format($fileDate, 'm');
// echo $file . "\n";
// echo substr($file, 0, 13) . "\n";
// echo date_format($fileDate, 'Y-m-d H:i') . "\n";

// print_r($frame['vin']);

$m = date_format($fileDate, 'F');
$y = date_format($fileDate, 'Y');
$vin = $frame['vin'] . ' - ' . $frame['vehicle_state']['car_version'];

$lastUpdate = date_format(datetime_from_filename($file), 'Y-m-d g:i A');

$html = array();

array_push($html, '  <div class="title">');
array_push($html, '    <div class="titleMonth">' . $m . '</div><div class="titleYear">' . $y . '</div>');
array_push($html, '  </div>');
array_push($html, '  <div class="vin medium"><b>' . $frame['vehicle_state']['vehicle_name'] . '</b> - ' . $vin . '</div>');
array_push($html, '  <div class="update medium">Last Updated :' . $lastUpdate . '</div>');

$oneDay = new DateInterval('P1D');
for ($k = 0; $k < 7; $k++) {
	// echo date_format($fileDate, 'Y-m-d H:i w') . "\n";
	if (date_format($fileDate, 'w') == 0) {
		break;
	}
	$fileDate->sub($oneDay);
}
// Roll back another (count) weeks as the first Sunday
$fileDate->sub(DateInterval::createFromDateString(($count - 1) * 7 . 'days'));
//echo 'First Sunday -> ' . date_format($fileDate, 'Y-m-d H:i w') . "\n";

// Make a top row showing days
$t0 = $fileDate;
for ($k = 0; $k < 7; $k++) {
	$y = 60;
	$x = $k * ($width + $offset);
	$d = date_format($t0, 'D');
	$t0->add($oneDay);
	array_push($html, '  <div class="dayOfWeek" style="left:' . $x . 'px; top:' . $y . 'px">');
	array_push($html, '    <div class="titleDayLabel">' . $d . '</div>');
	array_push($html, '  </div>');
}
// Look for the first Sunday to start showing. This is the first day of the calendar
$t0 = $fileDate;
for ($i = 0; $i < count($data); $i++) {
	$file = $data[$i][0][0];
	//echo $file . "\n";
	$date = date_from_filename($file);
	if (date_format($date, 'w') == 0) {
		break;
	}
}
$calendarDay = date_from_filename($file);
// echo '$i = ' . $i . "\n";

$today = DateTime::createFromFormat('YmjHi', date('Ymd') . '0000');

// echo date_format($today, 'Ymj-Hi') . "\n";

function insertOrFadeIcon($cond, $image) {
	$appendix = '';
	if ($cond or $GLOBALS['showFadeIcon']) {
		if (!$cond and $GLOBALS['showFadeIcon']) {
			$appendix .= ' fade';
		}
		return '<img class="icon' . $appendix . '" src="' . $image . '"/>';
	}
	return '';
}

// Loop through data (i) but up to (count) weeks. The variable i increases on Saturday
$j = 0;
$d = 0;
$o1 = 0;
$s1 = 0;
$chargeAlpha = 0;
for ($k = 0; $k < $count * 7; $k++) {
	$x = $d * ($width + $offset);
	$y = $j * ($height + $offset) + 90;
	$elemClass = '';
	if ($targetMonth != date_format($calendarDay, 'm')) {
		$elemClass .= ' otherMonth';
	} else if ($calendarDay == $today) {
		$elemClass .= ' today';
	}
	if ($m != date_format($calendarDay, 'm')) {
		$m = date_format($calendarDay, 'm');
		$dayString = date_format($calendarDay, 'M j');
	} else {
		$dayString = date_format($calendarDay, 'j');
	}
	array_push($html, '  <div class="box" style="left:' . $x . 'px; top:' . $y . 'px">');
	array_push($html, '    <div class="dayLabel' . $elemClass . '">' . $dayString . '</div>');
	if ($i < count($data)) {
		$day = $data[$i];
		$file = $day[count($day) - 1][0];
		$fileDate = date_from_filename($file);
		if ($fileDate == $calendarDay) {
			// Start and end frames of the day
			$frameAlpha = $day[0][1];
			$frameOmega = $day[count($day) - 1][1];
			$fileDate = datetime_from_filename($file);

			// Calculate total miles driven
			if ($o1 == 0 and count($day) > 1) {
				$o1 = $frameAlpha['vehicle_state']['odometer'];
			}
			$o0 = $frameOmega['vehicle_state']['odometer'];
			$miles = $o0 - $o1;
			$carDriven = $miles > 1.0;
			$o1 = $o0;

			// If there was a charging event
			$carCharged = False;
			for ($n = 0; $n < count($day) and !$carCharged; $n++) {
				$frame = $day[$n][1];
				if ($frame['charge_state']['charging_state'] == 'Charging') {
					$carCharged = True;
				}
			}

			// Software version
			$carUpdated = False;
			if ($s1 == 0) {
				$s1 = $frameAlpha['vehicle_state']['car_version'];
			}
			$s0 = $frameOmega['vehicle_state']['car_version'];
			$carUpdated = $s0 != $s1;
			$s1 = $s0;

			// Battery level
			if ($chargeAlpha == 0) {
				$chargeAlpha = $frameAlpha['charge_state']['battery_level'];
			}
			$chargeOmega = $frameOmega['charge_state']['battery_level'];
			$chargeDelta = $chargeOmega - $chargeAlpha;
			$elemClass = '';
			$r = floor($chargeOmega * 0.1);
			if ($r <= 5) {
				$elemClass .= ' charge' . $r;
			}
			array_push($html, '    <div class="chargeLevel' . $elemClass . '" style="height:' . $chargeOmega . '%"></div>');
			if ($carCharged) {
				array_push($html, '    <div class="chargeAdded" style="bottom:' . $chargeAlpha . '%; height:' . $chargeDelta . '%"></div>');
			} else {
				array_push($html, '    <div class="chargeUsed" style="bottom:' . $chargeOmega . '%; height:' . (-$chargeDelta) . '%"></div>');
			}
			$chargeAlpha = $chargeOmega;

			// Icon bar using the information derived earlier
			array_push($html, '    <div class="iconBar">');
			array_push($html, '      ' . insertOrFadeIcon($carDriven, 'blob/wheel.png'));
			array_push($html, '      ' . insertOrFadeIcon($carCharged, 'blob/charge.png'));
			array_push($html, '      ' . insertOrFadeIcon($carUpdated, 'blob/up.png'));
			array_push($html, '    </div>');

			// Lines of information
			array_push($html, '    <div class="info">');
			array_push($html, '      <span class="textInfo large">' . $chargeOmega . '%</span>');
			array_push($html, '      <span class="textInfo medium">' . date_format($fileDate, 'g:i A') . '</span>');
			array_push($html, '      <span class="textInfo medium">+' . number_format($miles, 1, '.', ',') . ' mi (' . count($day) . ')</span>');
			array_push($html, '      <span class="textInfo medium">' . number_format($o0, 1, '.', ',') . ' mi</span>');
			array_push($html, '    </div>');

			$i++;
		}
	}
	array_push($html, '  </div>');

	$calendarDay->add($oneDay);
	if ($d++ == 6) {
		$d = 0;
		$j++;
	}
}

echo join("\n", $html);

?>

</div>

</body>

</html>
