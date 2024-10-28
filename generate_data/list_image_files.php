<?php
// error_reporting(E_ALL);
// ini_set('display_errors', 1);
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');
$files = glob("*.png");
$files = array_merge($files, glob("*.jpg"));
echo json_encode($files);
?>