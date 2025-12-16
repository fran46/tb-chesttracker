<?php
header("Content-Type: application/json; charset=UTF-8");

// =============================================================
// READ POST BODY (JSON)
// =============================================================

$input = file_get_contents("php://input");
$data = json_decode($input, true);

if (!$data || !is_array($data)) {
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "message" => "Invalid JSON or payload is not an array"
    ]);
    exit;
}

// =============================================================
// DATABASE CONNECTION
// =============================================================

$mysqli = new mysqli(
    "yourdb.server.com",
    "DB_user",
    "DB_user_password!",
    "DB_name"
);

if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode([
        "status" => "error",
        "message" => "Database connection error: " . $mysqli->connect_error
    ]);
    exit;
}

// =============================================================
// 1) LOAD PLAYER NAME / ALIAS MAP
// =============================================================

$playerMap = [];

$result = $mysqli->query("SELECT name, alias FROM members_sk");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $name = trim($row['name']);

        // Store original name (case-insensitive key)
        $playerMap[strtolower($name)] = $name;

        // Process aliases (comma-separated)
        if (!empty($row['alias'])) {
            $aliasList = array_map('trim', explode(',', $row['alias']));
            foreach ($aliasList as $alias) {
                if ($alias !== '') {
                    $playerMap[strtolower($alias)] = $name;
                }
            }
        }
    }
    $result->free();
}

// =============================================================
// 2) PREPARE INSERT STATEMENT
// =============================================================

$stmt = $mysqli->prepare(
    "INSERT INTO cofres_sk \
     (fecha_captura, cofre, jugador, origen, generado) \
     VALUES (?, ?, ?, ?, ?)"
);

if (!$stmt) {
    http_response_code(500);
    echo json_encode([
        "status" => "error",
        "message" => "Prepare failed: " . $mysqli->error
    ]);
    exit;
}

$insertedCount = 0;
$errors = [];

// =============================================================
// 3) PROCESS DATA AND NORMALIZE PLAYER NAMES
// =============================================================

foreach ($data as $row) {
    if (!isset($row['fecha'], $row['chest'], $row['player'], $row['source'], $row['generado'])) {
        $errors[] = [
            "reason" => "Missing required fields",
            "data" => $row
        ];
        continue;
    }

    // Clean player name (trim spaces and trailing commas)
    $originalPlayer = rtrim(trim($row['player']), ',');
    $playerKey = strtolower($originalPlayer);

    // Replace alias with canonical name if found
    $normalizedPlayer = $playerMap[$playerKey] ?? $originalPlayer;

    $stmt->bind_param(
        "sssss",
        $row['fecha'],
        $row['chest'],
        $normalizedPlayer,
        $row['source'],
        $row['generado']
    );

    if ($stmt->execute()) {
        $insertedCount++;
    } else {
        $errors[] = [
            "reason" => "Insert error",
            "player" => $normalizedPlayer
        ];
    }
}

$stmt->close();
$mysqli->close();

// =============================================================
// 4) JSON RESPONSE
// =============================================================

echo json_encode([
    "status" => "ok",
    "inserted" => $insertedCount,
    "errors" => $errors
]);
?>
