<?php
// Skitter's 27-value calibration lattice (654d61ed, comment 227c3f79) through the REAL filter:
// MessageBlindFloor::isCalibration at register PR #683 head 97a42f1, decoded with json_decode(..., true)
// (the register's decode mode) and, for the record, with assoc=false where the value is an object.
require __DIR__ . '/MessageBlindFloor_97a42f1.php';
$inputs = ['null','true','false','0','1','-1','0.0','-0.0','1.5','""','"0"','"0.0"','"00"','" "','"false"','"null"','"a"','[]','[0]','[""]','[null]','{}','{"a":0}','{"":null}','"\u0000"','1e-9','"[]"'];
$rows = [];
foreach ($inputs as $j) {
    $assoc = json_decode($j, true, 512, JSON_THROW_ON_ERROR);
    $obj = json_decode($j, false, 512, JSON_THROW_ON_ERROR);
    $rows[] = ['json' => $j,
        'php_filter_assoc' => \App\Service\MessageBlindFloor::isCalibration($assoc),
        'php_filter_object' => \App\Service\MessageBlindFloor::isCalibration($obj),
        'php_empty_assoc' => !empty($assoc),
        'php_empty_object' => !empty($obj)];
}
$rows[] = ['json' => '(absent)', 'php_filter_assoc' => \App\Service\MessageBlindFloor::isCalibration(null), 'php_filter_object' => \App\Service\MessageBlindFloor::isCalibration(null), 'php_empty_assoc' => false, 'php_empty_object' => false];
echo json_encode(['filter' => 'MessageBlindFloor::isCalibration @97a42f1', 'php' => PHP_VERSION, 'rows' => $rows], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), "\n";
