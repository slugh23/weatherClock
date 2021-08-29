<?php
$json = file_get_contents('php://input');
if ($json && strlen($json) > 0)
{
    echo "found data\n";
    $decoded = json_decode($json);
    var_dump($decoded[8]);
    $encoded = json_encode($decoded);
    echo "dec/en-coded data\n";
    if ($encoded && strlen($encoded) > 0) {
        echo "saving data\n";
        $saved = file_put_contents("special-events.json");
        var_dump($saved);
        if ($saved !== FALSE && $saved > 0) {
            echo "saved data $saved\n";
        }
    }
    exit();
}

echo file_get_contents("special-events.json");
echo "\n";

