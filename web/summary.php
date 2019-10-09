<?php
date_default_timezone_set('UTC');

// $strJsonFileContents = file_get_contents('/home/boonleng/Documents/Tesla/20191008/20191008-1000.json');
// var_dump($strJsonFileContents); 

$store = '/home/boonleng/Documents/Tesla';
$folders = scandir($store, 0);
$folders = array_slice($folders, count($folders) - 35);

// print_r($folders);

$data = array();
foreach ($folders as $folder) {
	$files = array_diff(scandir($store . '/' . $folder), array('..', '.'));
	// print_r($files);
	$frames = array();
	foreach ($files as $file) {
		$fullpath = $store . '/' . $folder . '/' . $file;
		$contents = file_get_contents($fullpath);
		array_push($frames, array($file, $contents));
	}
	array_push($data, $frames);
}

echo json_encode($data);

?>
