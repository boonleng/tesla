<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="stylesheet" type="text/css" href="common.css?v=15"/>
	<style type="text/css">
		.hidden {visibility:hidden}
		.boxContainer {width:898px; height:935px}
		.dayOfWeek {width:123px; height:50px}
		.box {width:123px; height:148px}
	</style>
	<title>Tesla Vehicle Summary</title>
</head>

<body>

<?php
date_default_timezone_set('UTC');

// Global variables
$store = '/home/boonleng/Documents/Tesla';
$debug = False;
$count = 5;
$width = 123;
$height = 148;
$offset = 6;
$showFadeIcon = True;

// Arrays for HTML and debugging info
$html = array('<div class="boxContainer">');
$info = array();

function list_folders($end_date = '20760520', $count = 35) {
	$folders = scandir($GLOBALS['store'], 0);
	$index = array_search($end_date, $folders);
	// echo "$end_date = $end_date   index = $index\n";
	array_push($GLOBALS['info'], "index = $index");
	// print_r($folders);
	if ($index) {
		$index -= $count - 1;
		if ($index < 2) {
			$count -= 2 - $index;
			$index = 2;
			array_push($GLOBALS['info'], "index = $index   count = $count");
		}
		array_push($GLOBALS['info'], "index = $index   count = $count / " . count($folders));
		array_push($GLOBALS['info'], "folder[$index] = " . $folders[$index]);
		array_push($GLOBALS['info'], "folder[" . ($index + $count - 1) . "] = " . $folders[$index + $count - 1]);
		$folders = array_slice($folders, $index, $count);
	} else {
		$folders = array_slice($folders, max(2, count($folders) - $count));
	}
	return $folders;
}

function date_from_filename($file) {
	return date_create_from_format('YmjHi', substr($file, 0, 8) . '0000');
}

function datetime_from_filename($file) {
	return date_create_from_format('Ymj-Hi', substr($file, 0, 13));
}

function insert_or_fade_icon($cond, $image) {
	$appendix = '';
	if ($cond or $GLOBALS['showFadeIcon']) {
		if (!$cond and $GLOBALS['showFadeIcon']) {
			$appendix .= ' fade';
		}
		return '<img class="icon' . $appendix . '" src="' . $image . '"/>';
	}
	return '';
}

// ---

// Get variables from the URL

if ($_GET['debug']) {
	$debug = True;
}
if ($_GET['end']) {
	$endDate = $_GET['end'];
} else {
	$endDate = date('Ymd');
}
// $endDate = '20190824';
array_push($info, 'endDate = ' . $endDate);

// List the folders and gather the data
$folders = list_folders($endDate, 7 * $count);
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
array_push($info, 'folders = [' . implode(', ', $folders) . ']');

// Common variables
$i = 0;
$last = $data[count($data) - 1];
$file = $last[count($last) - 1][0];
$frame = $last[count($last) - 1][1];
$fileDate = date_from_filename($file);
$targetMonth = date_format($fileDate, 'm');
$vin = $frame['vin'] . ' - ' . $frame['vehicle_state']['car_version'];
$lastUpdate = date_format(datetime_from_filename($file), 'Y-m-d g:i A');

// Calendar HTML
array_push($html, '  <div class="title">');
array_push($html, '    <div class="titleMonth">' . date_format($fileDate, 'F') . '</div>');
array_push($html, '    <div class="titleYear">' . date_format($fileDate, 'Y') . '</div>');
array_push($html, '  </div>');
array_push($html, '  <div class="vin medium"><b>' . $frame['vehicle_state']['vehicle_name'] . '</b> - ' . $vin . '</div>');
array_push($html, '  <div class="update medium">Last Updated :' . $lastUpdate . '</div>');

// Find the Sunday of the week of interest, then roll back another (count) weeks as the first Sunday of the Calendar
$oneDay = new DateInterval('P1D');
for ($k = 0; $k < 7; $k++) {
	array_push($info, 'Checkpoint 1.' . $k . ' - ' . date_format($fileDate, 'Y-m-d H:i:s D (w)'));
	if (date_format($fileDate, 'w') == 0) {
		break;
	}
	$fileDate->sub($oneDay);
}
$calendarDay = $fileDate->sub(DateInterval::createFromDateString(($count - 1) . 'weeks'));
array_push($info, 'calendarDay -> ' . date_format($calendarDay, 'Y-m-d H:i:s D'));

// Make a top row showing days
$t0 = clone $calendarDay;
for ($k = 0; $k < 7; $k++) {
	$y = 60;
	$x = $k * ($width + $offset);
	$d = date_format($t0, 'D');
	$t0->add($oneDay);
	array_push($html, '  <div class="dayOfWeek" style="left:' . $x . 'px; top:' . $y . 'px">');
	array_push($html, '    <div class="titleDayLabel">' . $d . '</div>');
	array_push($html, '  </div>');
}

// Look for the first data index at the beginning of the calendar
$i = 0;
$file = $data[$i][0][0];
$fileDate = date_from_filename($file);
if ($fileDate < $calendarDay) {
	$t0 = clone $calendarDay;
	for ($i = 0; $i < count($data); $i++) {
		$file = $data[$i][0][0];
		$date = date_from_filename($file);
		array_push($info, 'Checkpoint 2.' . $i . ' file = ' . $file . ' -> ' . date_format($date, 'Y-m-d H:i:s D (w)'));
		if (date_format($date, 'w') == 0) {
			break;
		}
	}
}
$today = DateTime::createFromFormat('YmjHi', date('Ymd') . '0000');
array_push($info, 'today = ' . date_format($today, 'Ymj H:i:s'));
array_push($info, 'i = ' . $i);

// Loop through data (i) but up to (count) weeks. The variable j increases on Saturday
$j = 0;
$d = 0;
$m = 0;
$o1 = 0;
$s1 = 0;
$c1 = 0;
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
			$activity = $miles >= 0.1 ? '+' . number_format($miles, 1, '.', ',') . ' mi' : 'parked';

			// If there was a charging event
			$carCharged = False;
			$cMin = 100;
			$cMax = 0;
			for ($n = 0; $n < count($day); $n++) {
				$frame = $day[$n][1];
				if (!$carCharged and $frame['charge_state']['charging_state'] == 'Charging') {
					$carCharged = True;
				}
				$charge = $frame['charge_state']['battery_level'];
				$cMin = min($cMin, $charge);
				$cMax = max($cMax, $charge);
			}

			// Software version
			$carUpdated = False;
			if ($s1 == 0) {
				$s1 = $frameAlpha['vehicle_state']['car_version'];
			}
			$s0 = $frameOmega['vehicle_state']['car_version'];
			$carUpdated = $s0 != $s1;

			// Battery level
			if ($c1 == 0) {
				$c1 = $frameAlpha['charge_state']['battery_level'];
			}
			$c0 = $frameOmega['charge_state']['battery_level'];
			$elemClass = '';
			$r = floor($c0 * 0.1);
			if ($r <= 5) {
				$elemClass .= ' charge' . $r;
			}
			array_push($html, '    <div class="charge endOfDay' . $elemClass . '" style="height:' . $c0 . '%"></div>');
			if ($carCharged) {
				array_push($html, '    <div class="charge added" style="bottom:' . $c0 . '%; height:' . ($cMax - $c0) . '%"></div>');
				if ($c0 - $cMin) {
					array_push($html, '    <div class="charge addedUsed" style="bottom:' .  $cMin . '%; height:' . ($c0 - $cMin) . '%"></div>');
				} elseif ($c1 - $cMin) {
					array_push($html, '    <div class="charge usedAdded" style="bottom:' .  $cMin . '%; height:' . ($c1 - $cMin) . '%"></div>');
				}
			} else {
				array_push($html, '    <div class="charge used" style="bottom:' . $c0 . '%; height:' . ($c1 - $c0) . '%"></div>');
			}

			// Icon bar using the information derived earlier
			array_push($html, '    <div class="iconBar">');
			array_push($html, '      ' . insert_or_fade_icon($carDriven, 'blob/wheel.png'));
			array_push($html, '      ' . insert_or_fade_icon($carCharged, 'blob/charge.png'));
			array_push($html, '      ' . insert_or_fade_icon($carUpdated, 'blob/up.png'));
			array_push($html, '    </div>');

			// Lines of information
			array_push($html, '    <div class="info">');
			array_push($html, '      <span class="textInfo large">' . $c0 . '%</span>');
			array_push($html, '      <span class="textInfo medium">' . date_format($fileDate, 'g:i A') . '</span>');
			array_push($html, '      <span class="textInfo medium">' . $activity . ' (' . count($day) . ')</span>');
			array_push($html, '      <span class="textInfo medium">' . number_format($o0, 1, '.', ',') . ' mi</span>');
			array_push($html, '    </div>');

			$c1 = $c0;
			$o1 = $o0;
			$s1 = $s0;
			$i++;
		} else {
			array_push($html, '    <div class="charge endOfDay predict' . $elemClass . '" style="height:' . $c0 . '%"></div>');

			// Icon bar using the information derived earlier
			array_push($html, '    <div class="iconBar">');
			array_push($html, '      ' . insert_or_fade_icon(False, 'blob/wheel.png'));
			array_push($html, '      ' . insert_or_fade_icon(False, 'blob/charge.png'));
			array_push($html, '      ' . insert_or_fade_icon(False, 'blob/up.png'));
			array_push($html, '    </div>');

			// Lines of information
			array_push($html, '    <div class="info">');
			array_push($html, '      <span class="textInfo large predict">' . $c0 . '%</span>');
			array_push($html, '      <span class="textInfo medium">No data</span>');
			array_push($html, '      <span class="textInfo medium">Likely parked</span>');
			array_push($html, '      <span class="textInfo medium">' . number_format($o0, 1, '.', ',') . ' mi</span>');
			array_push($html, '    </div>');
		}
	}
	array_push($html, '  </div>');

	$calendarDay->add($oneDay);
	if ($d++ == 6) {
		$d = 0;
		$j++;
	}
}

array_push($html, '</div>');

echo implode("\n", $html);

if ($debug) {
	echo '<div id="debug">' . "\n";
	echo implode("\n", $info);
	echo '</div>' . "\n";
}

?>

</div>

</body>

</html>
