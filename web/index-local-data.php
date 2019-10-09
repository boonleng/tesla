<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="stylesheet" type="text/css" href="common.css?ver=1">
	<style type="text/css">
		.hidden {visibility:hidden;}
		.boxContainer {width:898px; height:935px;}
		.dayOfWeek {width:123px; height:50px;}
		.box {width:123px; height:148px;}
	</style>
	<script type="text/javascript" src="/javascript/jquery.js"></script>
	<script type="text/javascript" src="summary.js"></script>
	<title>Car Summary</title>
</head>

<body>

<?php
	if ($_GET['debug']) {
		echo '<input class="hidden" id="SummaryDebug" value="' . $_GET['debug'] . '" />';
	}
?>

<div id="CarSummary"></div>

</body>

</html>
