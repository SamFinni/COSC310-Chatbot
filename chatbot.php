<?php
session_start();

$host = '127.0.0.1';
$srcPort = 0;

// input check
$SP = isset($_SESSION['srcPort']) ? $_SESSION['srcPort'] : '';
$UI = isset($_POST['uInput']) ? $_POST['uInput'] : '';

// create UDP socket
$s = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
socket_set_option($s, SOL_SOCKET, SO_REUSEADDR, 1);
socket_set_option($s, SOL_SOCKET, SO_RCVTIMEO, array("sec"=>8,"usec"=>0));

if ($SP != '') {
 	// reconnect to existing port
 	socket_bind($s, $host, $SP);
 	// push user's new response to convo array
 	if ($UI != '')
 		array_push($_SESSION['convo'], $UI);
 		// send user's response to chatbot
 		$data = utf8_encode($UI);
 		socket_sendto($s, $data, strlen($data), 0, $host, $_SESSION['dstPort']);
 		// save bot's response to convo array
 		utf8_decode(socket_recvfrom($s, $rcv, 4096, 0, $ip, $port));
 		if ($rcv != '')
 			array_push($_SESSION['convo'], $rcv);
} else {
	socket_bind($s, $host);
	// get socket port
	socket_getsockname($s, $srcIP, $srcPort);
	$_SESSION['srcPort'] = $srcPort;
	// begin chatbot python process and give it our port
	shell_exec('/usr/bin/sudo /opt/rh/rh-python36/root/usr/bin/python charles.py '.$srcPort.' > /dev/null 2>&1 &');
	// receive first response from chatbot, save address
	socket_recvfrom($s, $rcv, 4096, 0, $dstIP, $dstPort);
	$_SESSION['dstIP'] = $dstIP;
	$_SESSION['dstPort'] = $dstPort;
	// make sure response is as expected
	if (utf8_decode($rcv) != "CONNECT") {
		echo "<script type='text/javascript'>alert('Connection failed.');</script>";
		$_SESSION['srcPort'] = '';
	}
	// create session array to hold conversation data
	$_SESSION['convo'] = array();
}
	// close socket
	socket_shutdown($s, 2);
	socket_close($s);
?>

<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<title>Charles the Chatbot</title>
		<link rel="stylesheet" href="stylesheet.css" type="text/css">
		<script>
			document.addEventListener('DOMContentLoaded', function(event) {
				var element = document.getElementById("convo");
				element.scrollTop = element.scrollHeight;
			})

			function submitOnEnter(event) {
			    if (event.which === 13) {
			        document.forms[0].submit();
			        event.preventDefault();
			    }
			}
		</script>
	</head>
	<body>
		<div id='container'>
			<div id='window'>
				<div id='convo'>
					<div class='system'>
						<div class='message'>Say hi!</div>
					</div>
<?php
for ($i = 0; $i < sizeof($_SESSION['convo']); $i += 2) {
	$userResponse = $_SESSION['convo'][$i];
	$botResponse = $_SESSION['convo'][$i+1];
	if ($userResponse != '')
		echo "<div class='you'><div class='message'>".$userResponse."</div></div>";
	if ($botResponse != '')
		echo "<div class='bot'><div class='message'>".$botResponse."</div></div>";
}
if (sizeof($_SESSION['convo']) >= 1) {
	if (strtolower($userResponse) == "bye" or strtolower($userResponse) == "exit") {
		$_SESSION['srcPort'] = '';
		echo "<div class='system'><div class='message'>You have ended the conversation.</div></div>";
	} elseif ($botResponse == '') {
		$_SESSION['srcPort'] = '';
		echo "<div class='system'><div class='message'>The conversation has timed out. Refresh to start a new one!</div></div>";
	}
}
?>
				</div>
				<form id='input' method='post'>
					<textarea id='uInput' name='uInput' onkeydown="submitOnEnter(event)" placeholder="Say something..."></textarea>
					<button id='send'>Send</button>
				</form>
			</div>
		</div>
	</body>
</html>