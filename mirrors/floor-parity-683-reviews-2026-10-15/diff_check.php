<?php
// JSON values as PHP decodes them (assoc), empty() per value
$vals = ['null'=>null,'true'=>true,'false'=>false,'0'=>0,'1'=>1,'-1'=>-1,'0.0'=>0.0,'0.5'=>0.5,'""'=>"",'"0"'=>"0",'"0.0"'=>"0.0",'"00"'=>"00",'" "'=>" ",'"a"'=>"a",'[]'=>[],'[0]'=>[0],'{}'=>json_decode('{}', true),'{"a":0}'=>json_decode('{"a":0}', true)];
$out = [];
foreach ($vals as $k => $v) { $out['empty'][$k] = empty($v) ? 'empty' : 'nonempty'; }
$out['trim'] = ['NUL_a_FF' => bin2hex(trim("\x00a\x0c")), 'NBSP_a' => bin2hex(trim("\xc2\xa0a")), 'VT_a' => bin2hex(trim("\x0ba")), 'FS_a' => bin2hex(trim("\x1ca"))];
$out['casefold'] = ['mb_fold_sharp_s' => mb_convert_case("straße", MB_CASE_FOLD, "UTF-8"), 'mb_lower_sharp_s' => mb_strtolower("straße", "UTF-8"), 'strtolower_STRASSE' => strtolower("STRASSE")];
$out['round'] = ['number_format_17_32' => number_format(17/32, 4), 'php_version' => PHP_VERSION];
echo json_encode($out, JSON_UNESCAPED_UNICODE), "\n";
