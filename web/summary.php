<?php
date_default_timezone_set('UTC');

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
		$object = json_decode($contents);
		array_push($frames, array($file, $object));
	}
	array_push($data, $frames);
}

echo json_encode($data);

?>
