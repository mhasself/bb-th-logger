<html>
<body>

<?php
   $is_post = isset($_POST["submit"]);
   if ($is_post) {
      // Set the time...
      if (isset($_POST["datestr"])) {
        $timestr = $_POST["datestr"] . " " . $_POST["timestr"] . " UTC";
        $timestamp = strtotime($timestr);
        exec("/bin/date -s@{$timestamp}");
        echo $timestr . " " . $timestamp;
      }
      // Trigger reload.
      header("Refresh:5");
   } else {
      // Get system time.
      exec("/bin/date", $output);
      echo "<b>The current system time is: " . $output[0] .
         "</b>\n";
   } 
?>
<hr>
Change the time:
<form action="set_time.php" method="post">
Date (YYYY-MM-DD): <input type="text" name="datestr"><br>
Time (HH:MM:DD): <input type="text" name="timestr"><br>
<input name="submit" type="submit">
</form>

</body>
</html>
